# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.12"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # PQL Assert Tests – Automated DAX & SQL Validation
# 
# This notebook validates a Power BI semantic model end-to-end:
# 
# 1. Runs **PQL.Assert** data quality and relationship tests.
# 2. Runs **PQL.Assert** best-practice checks (formatting, DAX expressions, maintenance, performance).
# 3. Uses GitHub Copilot to translate each DAX measure into an equivalent T-SQL query, executes it against the Warehouse, and cross-validates the result against the model via `Measures.ANY.Tests`.
# 
# > **Prerequisites:** a Fabric Warehouse SQL endpoint, a semantic model exposing `PQL.Assert` functions, and a GitHub token.


# CELL ********************

%pip install -q github-copilot-sdk semantic-link-labs tabulate pandas

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import asyncio
from copilot import CopilotClient
from copilot.session import PermissionHandler
from copilot.session_events import AssistantMessageData, SessionIdleData
import json
import notebookutils
import pandas as pd
import re
import sempy.fabric as fabric
from typing import Dict, List, Tuple, Optional

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Variables
lib = notebookutils.variableLibrary.getLibrary("vl_variables")
WORKSPACE_ID = lib.semanticModel.get("workspaceId") # REPLACE ME
DATASET_ID = lib.semanticModel.get("itemId") # REPLACE ME
WAREHOUSE_ID = lib.dataWarehouse.get("itemId") # REPLACE ME
GITHUB_TOKEN = lib.githubPAT # REPLACE ME

# Connections
wh_connection = notebookutils.data.connect_to_artifact(
    artifact=WAREHOUSE_ID,
    workspace=WORKSPACE_ID
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

asserts_df = fabric.evaluate_dax(
    workspace=WORKSPACE_ID,
    dataset=DATASET_ID,
    dax_string="""
        EVALUATE 
            UNION(
                DataQuality.ANY.Tests(),
                Relationships.ANY.Tests()
            )
    """
)

display(asserts_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

bp_df = fabric.evaluate_dax(
    workspace=WORKSPACE_ID,
    dataset=DATASET_ID,
    dax_string="""
        EVALUATE UNION(
            PQL.Assert.BP.CheckErrorPrevention(),
            PQL.Assert.BP.CheckFormatting(),
            PQL.Assert.BP.CheckDAXExpressions(),
            PQL.Assert.BP.CheckMaintenance(),
            PQL.Assert.BP.CheckPerformance()
        )
    """
)

display(bp_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

metadata_query = """
    SELECT
        SCHEMA_NAME(tab.schema_id) AS 'Schema Name',
        tab.name AS 'Table Name',
        col.name AS 'Column Name',
        t.name AS 'Data Type'
    FROM 
        sys.tables AS tab
    INNER JOIN 
        sys.columns AS col ON tab.object_id = col.object_id
    LEFT JOIN 
        sys.types AS t ON col.user_type_id = t.user_type_id;
"""

constraints_query = """
    SELECT
        tp.name AS 'Parent Table',
        cp.name AS 'Parent Column',
        tr.name AS 'Referenced Table',
        cr.name AS 'Referenced Column'
    FROM
        sys.foreign_keys fk
    INNER JOIN
        sys.tables tp ON fk.parent_object_id = tp.object_id
    INNER JOIN
        sys.tables tr ON fk.referenced_object_id = tr.object_id
    INNER JOIN
        sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
    INNER JOIN
        sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
    INNER JOIN 
        sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
    ORDER BY
        tp.name, cp.column_id
"""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

class GitHubCopilotClient:
    def __init__(self, github_token=None, model="gpt-5", timeout_s=120):
        self.github_token = github_token
        self.model = model
        self.timeout_s = timeout_s
        self.client = None
        self.session = None

    async def start(self):
        if self.session is not None:
            return

        self.client = CopilotClient(
            github_token=self.github_token,
            use_logged_in_user=False
        )
        await self.client.start()
        self.session = await self.client.create_session(
            on_permission_request=PermissionHandler.approve_all,
            model=self.model,
        )

    async def ask(self, prompt):
        
        if self.session is None:
            await self.start()

        done = asyncio.Event()
        parts = []

        def on_event(event):
            match event.data:
                case AssistantMessageData() as data:
                    text = data.content or ""
                    parts.append(text)
                case SessionIdleData():
                    done.set()

        off = self.session.on(on_event)
        try:
            await self.session.send(prompt)
            await asyncio.wait_for(done.wait(), timeout=self.timeout_s)
        finally:
            if callable(off):
                off()
        
        return "".join(parts).strip()

    async def close(self):
        await self.session.disconnect()
        await self.client.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# Measures metadata
measures_df = fabric.list_measures(workspace=WORKSPACE_ID, dataset=DATASET_ID)[["Measure Name", "Measure Description"]]

# SQL source metadata
md_df = wh_connection.query(metadata_query)

# Constraints info
constraints_df = wh_connection.query(constraints_query)

max_date = fabric.evaluate_dax(
    workspace=WORKSPACE_ID,
    dataset=DATASET_ID,
    dax_string="""
        EVALUATE ROW("Max Calendar Date", MAX('Date'[Date]))
    """
).iat[0,0].strftime("%Y-%m-%d")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

prompt = f"""
You are an expert in DAX, Power BI and Microsoft SQL Server.

**INPUT**

Measures
{measures_df.to_markdown()}

Available tables and columns
{md_df.to_markdown()}

Primary keys and relationships
{constraints_df.to_markdown()}

Reference date
{max_date}

**OBJECTIVE**

Generate exactly one SQL Server query for each input measure, preserving the same measure order.
The generated SQL must implement the measure description literally and only with information explicitly available in the input.

**IMPORTANT INSTRUCCIONS**

- Use only tables and columns that exist in INPUT.
- Do NOT invent, assume, derive, or substitute columns that are not explicitly present in the provided metadata.
- For measure logic, you may use a column only when the column is explicitly referenced in the measure description, 
    or its use is strictly necessary to implement an operation explicitly requested by the measure description and the intended column can be determined unambiguously from the provided metad
- Columns that are not referenced by the measure description may be used ONLY as join keys when the relationship is explicitly defined in INPUT.
- Join-only columns must NOT be used for:
    - filtering
    - aggregation
    - grouping
    - ordering
    - date calculations
    - CASE expressions
    - business logic

    unless their use is explicitly required by the measure description.

- Do NOT introduce additional filters, business rules, exclusions, default conditions, or assumptions.
- Use only relationships explicitly provided in INPUT.
- Do NOT create a join based only on columns having similar names.
- Use the minimum number of tables and joins required to implement the measure.
- If multiple columns, tables, relationships, or interpretations could plausibly satisfy the measure and the input does not identify the correct one unambiguously, return "SQL": NULL.

**TIME INTELLIGENCE**

- Use {max_date} as the reference date for every temporal calculation, including but not limited to:
    - YTD
    - MTD
    - QTD
    - previous periods
    - year-over-year comparisons
    - month-over-month comparisons
    - rolling periods
    - last N days/months/years
- Do not use GETDATE(), CURRENT_TIMESTAMP, SYSDATETIME(), or any other current-date function.

**SQL REQUIREMENTS**

- Generate Microsoft SQL Server compatible T-SQL.
- Generate one standalone SELECT query per measure.
- Do NOT include SQL comments.
- Do NOT include explanations inside the SQL.
- Do NOT return multiple alternative queries.
- Prefer square brackets for SQL identifiers when quoting is required, for example [Unit Price].
- Prefer single quotes for SQL string and date literals.
- Avoid double quotes inside SQL unless strictly necessary.
- Do not add output columns that are not necessary to return the requested measure.

**MEASURE FIDELITY**

For every output item:
- Copy measure name exactly from the input.
- Copy Measure Description exactly from the input.
- Do NOT rewrite, summarize, translate, correct, expand, or normalize the measure description.
- Implement only what the description states.
- Do NOT add business context that is not present in the description.
- If the measure cannot be implemented reliably and literally using the supplied metadata and relationships, return "SQL": = NULL.

**OUTPUT**

- Return exactly one JSON array conforming to the specified schema.
- Do NOT include ANY TEXT OUTSIDE the JSON array.
- Each object must contain exactly:
    - "Measure Name"
    - "Measure Description"
    - "SQL"
- "SQL" must be a JSON string or NULL.

Example:
[{{"Measure Name":"Total Customers","Measure Description":"Counts customer rows in the current filter context.","SQL":"SELECT COUNT(*) FROM [dwh].[Customer];"}}]
"""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

def _execute_sql(sql: Optional[str]) -> Optional[float]:
    if not sql:
        return None
    return wh_connection.query(sql).iat[0, 0]

def _validate_measure(row: pd.Series) -> Optional[bool]:
    if row["Expected Value"] is None:
        sql_result = "BLANK()"
    else:
        sql_result = float(row["Expected Value"])
    
    measure_result = fabric.evaluate_dax(
        workspace=WORKSPACE_ID,
        dataset=DATASET_ID,
        dax_string=f"""
            EVALUATE Measures.ANY.Tests({sql_result},[{row["Measure Name"]}])
        """
    )

    return measure_result.iat[0, 2], measure_result.iat[0, 3]

chat = GitHubCopilotClient(github_token=GITHUB_TOKEN, model="gpt-5.3-codex", timeout_s=300)
try:
    response = await chat.ask(prompt)
finally:
    await chat.close()

json_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip())
try:
    results_df = pd.DataFrame(json.loads(json_text))
except json.JSONDecodeError as e:
    raise ValueError(f"Copilot response was not valid JSON: {e}\n\nResponse:\n{response}") from e

results_df["Expected Value"] = results_df["SQL"].apply(_execute_sql)
results_df[["Actual Value", "Passed"]] = results_df.apply(_validate_measure, axis="columns", result_type="expand")

# Summary - check for column name with or without brackets
total = len(results_df)
passed = int(results_df["Passed"].sum())
failed = total - passed
print(f"Results  |  Total: {total}  |  ✅ Passed: {passed}  |  ❌ Failed: {failed}")
print()

# Display the full results table
display(results_df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }
