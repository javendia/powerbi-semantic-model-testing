# Power BI Semantic Model Testing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Microsoft Fabric](https://img.shields.io/badge/Microsoft-Fabric-0078D4)](https://www.microsoft.com/microsoft-fabric)
[![Power BI](https://img.shields.io/badge/Power-BI-F2C811)](https://powerbi.microsoft.com/)

A practical Microsoft Fabric project that demonstrates how to validate Power BI
semantic models with automated DAX tests. It combines [PQL.Assert](https://github.com/PBI-Tools/PQL.Assert),
Semantic Link, and the GitHub Copilot SDK to test data quality, model
relationships, best practices and the consistency of DAX measures against the
underlying SQL source.

## Overview

The project uses a Contoso sample model backed by a Fabric Warehouse. The
`nb_pql_tests` notebook runs three complementary validation scenarios:

1. **Assertion tests** validate data-quality rules and model relationships
	 implemented as DAX user-defined functions.
2. **Best-practice tests** use the PQL.Assert Best Practice Analyzer checks to
	 identify common semantic-model issues and anti-patterns.
3. **Measure cross-validation** retrieves each measure and its functional
	 description, asks GitHub Copilot to produce an equivalent T-SQL query using
	 the Warehouse metadata, then compares the SQL result with the DAX measure.

The third scenario provides an experimental approach to independently validate
business metrics while preserving the model's reference date and source-schema
constraints.

## Contents

```
powerbi-semantic-model-testing/
├── /src/
│   ├── nb_pql_tests.Notebook/       # Fabric notebook with the test scenarios
│   ├── sm_contoso.pbip              # Power BI project entry point
│   ├── sm_contoso.Report/           # Report definition
│   ├── sm_contoso.SemanticModel/    # Semantic model and PQL.Assert functions
│   └── wh_data_warehouse.Warehouse/ # Contoso Warehouse project
├── LICENSE
└── README.md
```

## Prerequisites

To run the project in Microsoft Fabric, you need:

- An active Microsoft Fabric capacity and a workspace where you have at least
	Contributor permissions.
- A Fabric Warehouse deployed from `wh_data_warehouse.Warehouse` and populated
	with the [Contoso](https://github.com/sql-bi/Contoso-Data-Generator-V2-data/releases/tag/ready-to-use-data) tables.
- A Power BI semantic model deployed from `sm_contoso.SemanticModel`, connected
	to the Warehouse and refreshed after importing `functions.tmdl`.
- A Fabric notebook environment with access to the Warehouse and semantic
	model.
- A GitHub personal access token with access to GitHub Copilot, used by the
	`github-copilot-sdk` integration in the cross-validation scenario.

The notebook installs these Python dependencies at runtime:

```text
github-copilot-sdk
semantic-link-labs
tabulate
pandas
```

## Setup and Usage

1. Fork or clone this repository.
2. Connect the Fabric workspace to the repository's `src` folder.
3. Create a Fabric Variable Library named `vl_variables` and configure:

	 | Variable | Description |
	 | --- | --- |
	 | `semanticModel` | Item reference to the deployed semantic model. |
	 | `dataWarehouse` | Item reference to the deployed Warehouse. |
	 | `githubPAT` | GitHub token used by the GitHub Copilot SDK. |

4. Ensure the model contains the PQL.Assert functions in
	 `sm_contoso.SemanticModel/definition/functions.tmdl`, then refresh the
	 semantic model.
5. Open and run `nb_pql_tests.Notebook` in Fabric.
6. Review the results returned by each scenario. The final table shows the
	 generated SQL, expected result, actual DAX result, and pass/fail status for
	 every validated measure.

## Key Artifacts

- **PQL.Assert functions:** reusable DAX assertions and test-discovery helpers
	stored in the semantic model definition.
- **Contoso model:** a PBIP semantic model, report, and Warehouse schema used
	as the test subject.
- **Fabric notebook:** the executable test harness, including semantic-model
	queries, Warehouse metadata discovery, and GitHub Copilot-assisted T-SQL
	generation.

## License

This project is licensed under the [MIT License](LICENSE).
