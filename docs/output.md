# phac-nml/metadatatransformation: Output

## Introduction

This document describes the output produced by the pipeline.

The directories listed below may be created in the results directory after the pipeline has finished. All paths are relative to the top-level results directory. The exact directories created may depend on which metadata transformation is performed.

- lock: the outputs of the metadata lock operation

The IRIDA Next-compliant JSON output file will be named `iridanext.output.json.gz` and will be written to the top-level of the results directory. This file is compressed using GZIP and conforms to the [IRIDA Next JSON output specifications](https://github.com/phac-nml/pipeline-standards#42-irida-next-json).

## Pipeline overview

The pipeline is built using [Nextflow](https://www.nextflow.io/) and processes data using the following steps:

- [Lock](#lock) - Locks the metadata for IRIDA Next.

### Lock

<details markdown="1">
<summary>Output files</summary>

- `lock/`
  - A CSV-format file reporting locked files: `locked.csv`

</details>

[Nextflow](https://www.nextflow.io/docs/latest/tracing.html) provides excellent functionality for generating various reports relevant to the running and execution of the pipeline. This will allow you to troubleshoot errors with the running of the pipeline, and also provide you with other information such as launch commands, run times and resource usage.
