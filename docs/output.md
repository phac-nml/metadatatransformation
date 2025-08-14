# phac-nml/metadatatransformation: Output

## Introduction

This document describes the output produced by the pipeline.

The directories listed below may be created in the results directory after the pipeline has finished. All paths are relative to the top-level results directory. The exact directories created may depend on which metadata transformation is performed.

- lock: the outputs of the metadata lock operation

The IRIDA Next-compliant JSON output file will be named `iridanext.output.json.gz` and will be written to the top-level of the results directory. This file is compressed using GZIP and conforms to the [IRIDA Next JSON output specifications](https://github.com/phac-nml/pipeline-standards#42-irida-next-json).

## Pipeline overview

The pipeline is built using [Nextflow](https://www.nextflow.io/) and processes data using the following steps:

- [Lock](#lock) - Locks the metadata for IRIDA Next.
- [Age](#age) - Calculates the age between the first and second metadata columns.
- [Earliest](#earliest) - Determines the earliest date among metadata columns.
- [Populate](#populate) - Populates a specified column with a specified value. Existing values will be overwritten if the column already exists.

### Lock

<details markdown="1">
<summary>Output files</summary>

- `transformation/`
  - An Irida-Next intended CSV-format file for locking metadata fields within Irida Next: `transformation.csv`
  - A user-intended CSV-format file for reference: `result.csv`

### Age

<details markdown="1">
<summary>Output files</summary>

- `transformation/`
  - An Irida-Next intended CSV-format file for reporting calculated ages within Irida Next: `transformation.csv`
  - A user-intended CSV-format file for reference: `result.csv`

</details>

### Earliest

<details markdown="1">
<summary>Output files</summary>

- `transformation/`
  - A CSV-formatted file for reporting to Irida Next the earliest dates among metadata columns for each sample (empty dates will not be reported): `transformation.csv`
  - A user-intended CSV-formatted file for reference (all dates will be reported): `result.csv`

</details>

### Populate

<details markdown="1">
<summary>Output files</summary>

- `transformation/`
  - A CSV-formatted file for reporting to IRIDA Next the populated column for each sample: `transformation.csv`
  - A user-intended CSV-formatted file for reference: `result.csv`

### Categorize

<details markdown="1">
<summary>Output files</summary>

- `transformation/`
  - A CSV-formatted file for reporting to IRIDA Next the source type column ("calc_source_type") for each sample: `transformation.csv`
  - A user-intended CSV-formatted file for reference: `result.csv`

</details>

[Nextflow](https://www.nextflow.io/docs/latest/tracing.html) provides excellent functionality for generating various reports relevant to the running and execution of the pipeline. This will allow you to troubleshoot errors with the running of the pipeline, and also provide you with other information such as launch commands, run times and resource usage.
