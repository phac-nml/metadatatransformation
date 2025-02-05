[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A523.04.3-brightgreen.svg)](https://www.nextflow.io/)

# Metadata Transformation Pipeline for IRIDA Next

This pipeline transforms metadata from IRIDA Next.

# Input

The input to the pipeline is a sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | sample_name | metadata_1 | metadata_2 | metadata_3 | metadata_4 | metadata_5 | metadata_6 | metadata_7 | metadata_8 |
| ------- | ----------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Sample1 | SampleA     | meta_1     | meta_2     | meta_3     | meta_4     | meta_5     | meta_6     | meta_7     | meta_8     |

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json). Validation of the sample sheet is performed by [nf-validation](https://nextflow-io.github.io/nf-validation/).

# Parameters

The main parameters are `--input` as defined above and `--output` for specifying the output results directory. You may wish to provide `-profile singularity` to specify the use of singularity containers and `-r [branch]` to specify which GitHub branch you would like to run.

## Transformation

You may specify the metadata transformation with the `--transformation` parameter. For example, `--transformation lock` will perform the lock transformation. The available transformations are as follows:

| Transformation | Explanation                       |
| -------------- | --------------------------------- |
| lock           | Locks the metadata in IRIDA Next. |

## Other Parameters

Other parameters (defaults from nf-core) are defined in [nextflow_schema.json](nextflow_schema.json).

# Running

To run the pipeline, please do:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results --transformation lock
```

Where the `samplesheet.csv` is structured as specified in the [Input](#input) section.
For more information see [usage doc](docs/usage.md)

# Output

A JSON file for loading metadata into IRIDA Next is output by this pipeline. The format of this JSON file is specified in our [Pipeline Standards for the IRIDA Next JSON](https://github.com/phac-nml/pipeline-standards#32-irida-next-json). This JSON file is written directly within the `--outdir` provided to the pipeline with the name `iridanext.output.json.gz` (ex: `[outdir]/iridanext.output.json.gz`).

An example of the what the contents of the IRIDA Next JSON file looks like for this particular pipeline is as follows:

```
{
    "files": {
        "global": [
            
        ],
        "samples": {
            
        }
    },
    "metadata": {
        "samples": {
            "ABC": {
                "irida_id": "sample1",
                "metadata_1": "1.1",
                "metadata_2": "1.2",
                "metadata_3": "1.3",
                "metadata_4": "1.4",
                "metadata_5": "1.5",
                "metadata_6": "1.6",
                "metadata_7": "1.7",
                "metadata_8": "1.8"
            },
            "DEF": {
                "irida_id": "sample2",
                "metadata_1": "2.1",
                "metadata_2": "2.2",
                "metadata_3": "2.3",
                "metadata_4": "2.4",
                "metadata_5": "2.5",
                "metadata_6": "2.6",
                "metadata_7": "2.7",
                "metadata_8": "2.8"
            },
            "GHI": {
                "irida_id": "sample3",
                "metadata_1": "3.1",
                "metadata_2": "3.2",
                "metadata_3": "3.3",
                "metadata_4": "3.4",
                "metadata_5": "3.5",
                "metadata_6": "3.6",
                "metadata_7": "3.7",
                "metadata_8": "3.8"
            }
        }
    }
}
```

For more information see [output doc](docs/output.md).

## Test profile

To run with the test profile, please do:

```bash
nextflow run phac-nml/metadatatransformation -profile docker,test -r main -latest --outdir results --transformation lock
```

# Legal

Copyright 2025 Government of Canada

Licensed under the MIT License (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

https://opensource.org/license/mit/

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
