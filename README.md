[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A523.04.3-brightgreen.svg)](https://www.nextflow.io/)

# Metadata Transformation Pipeline for IRIDA Next

This pipeline transforms metadata from IRIDA Next.

# Input

The input to the pipeline is a sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | sample_name | metadata_1 | metadata_2 | metadata_3 | metadata_4 | metadata_5 | metadata_6 | metadata_7 | metadata_8 |
| ------- | ----------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Sample1 | SampleA     | meta_1     | meta_2     | meta_3     | meta_4     | meta_5     | meta_6     | meta_7     | meta_8     |

The amount and meaning of the metadata columns may be different for each metadata transformation.

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json). Validation of the sample sheet is performed by [nf-validation](https://nextflow-io.github.io/nf-validation/).

# Parameters

The main parameters are `--input` as defined above and `--output` for specifying the output results directory. You may wish to provide `-profile singularity` to specify the use of singularity containers and `-r [branch]` to specify which GitHub branch you would like to run.

## Transformation

You may specify the metadata transformation with the `--transformation` parameter. For example, `--transformation lock` will perform the lock transformation. The available transformations are as follows:

| Transformation | Explanation                                                                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| lock           | Locks, or copies and locks, the metadata in IRIDA Next.                                                                                                    |
| age            | Calculates the age between the first and second metadata columns. Ages under 2 years old are calculated as (days/365) years old, showing 4 decimal places. |
| earliest       | Reports the earliest date among the metadata columns.                                                                                                      |
| populate       | Populates an output column with a specific value.                                                                                                          |
| categorize     | Categorizes data into Human, Animal, Food or Environmental source based on values in a specific set of fields                                              |

## Lock Parameters

The following parameters can be used to rename CSV-generated output columns and Irida Next fields as follows:

- `--metadata_1_header`: names the first metadata_1 column header
- `--metadata_2_header`: names the first metadata_2 column header
- `--metadata_3_header`: names the first metadata_3 column header
- `--metadata_4_header`: names the first metadata_4 column header
- `--metadata_5_header`: names the first metadata_5 column header
- `--metadata_6_header`: names the first metadata_6 column header
- `--metadata_7_header`: names the first metadata_7 column header
- `--metadata_8_header`: names the first metadata_8 column header

## Age Parameters

The following parameters can be used to rename CSV-generated output columns and Irida Next fields as follows:

- `--metadata_1_header`: names the date of birth column header
- `--metadata_2_header`: names the current/target data column header
- `--age_header`: names the calculated age column header and related output columns

For example, the following code:

```
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/age/success_failure_mix.csv --outdir results --transformation age --metadata_1_header "date_of_birth" --metadata_2_header "collection_date" --age_header "age_at_collection"
```

would generate the following `results.csv` file:

```
sample,sample_name,date_of_birth,collection_date,age_at_collection,age_at_collection_valid,age_at_collection_error
sample1,ABC,2000-01-01,2000-12-31,1.0000,True,
sample2,DEF,2000-02-29,2024-02-29,24,True,
sample3,GHI,2000-05-05,1950-12-31,,False,The dates are reversed.
```

## Earliest Parameters

The following parameters can be used to rename CSV-generated output columns as follows:

- `--metadata_1_header`: names the first metadata_1 column header
- `--metadata_2_header`: names the first metadata_2 column header
- `--metadata_3_header`: names the first metadata_3 column header
- `--metadata_4_header`: names the first metadata_4 column header
- `--metadata_5_header`: names the first metadata_5 column header
- `--metadata_6_header`: names the first metadata_6 column header
- `--metadata_7_header`: names the first metadata_7 column header
- `--metadata_8_header`: names the first metadata_8 column header
- `--earliest_header`: names the earliest date column header and related output columns

The above parameters will only affect the `results.csv` file and not the information returned to IRIDA Next. The earliest date column will be reported as `calc_earliest_date` in `results.csv`, `transformation.csv`, and the `iridanext.output.json` file, which is returned to IRIDA Next.

The following special entries are ignored when calculating the earliest age (they are not considered malformed data): `Not Applicable`, `Missing`, `Not Collected`, `Not Provided`, `Restricted Access`, `(blank)`

## Populate Parameters

- `--populate_header`: names the header of the column to populate with `populate_value`
- `--populate_value`: the value to populate every entry within the `populate_header` column

## Categorize Parameters

This transformation is expecting a specific set of metadata headers:

- `host_scientific_name`: Scientific / latin name of host species (ie. _Genus species_)
- `host_common_name`: The common name for host species
- `food_product`: Name of food product (if food sample)
- `environmental_site`: Name of environmental site/facility (if environmental sample)
- `environmental_material`: Name of environmental material (if environmental sample)

In order to ensure these columns are recognized, the metadata header parameters must be used to specify which input headers are which expected headers
(ie. If `metadata_1` contains the host species common name, `--metadata_1_header host_common_name` must be added to the command)

For example, the following code:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/categorize/basic.csv --outdir results --transformation categorize --metadata_1_header host_scientific_name --metadata_2_header host_common_name  --metadata_3_header food_product --metadata_4_header environmental_site  --metadata_5_header environmental_material
```

would generate the following `results.csv` file:

```
sample,sample_name,host_scientific_name,host_common_name,food_product,environmental_site,environmental_material,calc_source_type
sample1,"A",Homo sapiens (Human),Human NCBITaxon:9606,,,,Human
sample2,"B",,dog,,,,Animal
sample3,"C",,,eggs,,,Food
sample4,"D",,,,farm,wastewater,Environmental
sample5,"E",,,,,,Unknown
sample6,"F",Homo sapiens (Human),dog,,,,Host Conflict
sample7,"G",Homo sapiens (Human),,,,,Human
sample8,"H",,Human NCBITaxon:9606,,,,Human
sample9,"J",Homo sapiens (Human),Human NCBITaxon:9606,eggs,farm,wastewater,Human
sample10,"K",,dog,eggs,,,Animal
sample11,"L",,,eggs,farm,,Food
sample12,"M",,,eggs,,wastewater,Food
```

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
            {
                "path": "transformation/results.csv"
            }
        ],
        "samples": {

        }
    },
    "metadata": {
        "samples": {
            "sample1": {
                "metadata_1": "1.1",
                "metadata_2": "1.2",
                "metadata_3": "1.3",
                "metadata_4": "1.4",
                "metadata_5": "1.5",
                "metadata_6": "1.6",
                "metadata_7": "1.7",
                "metadata_8": "1.8"
            },
            "sample2": {
                "metadata_1": "2.1",
                "metadata_2": "2.2",
                "metadata_3": "2.3",
                "metadata_4": "2.4",
                "metadata_5": "2.5",
                "metadata_6": "2.6",
                "metadata_7": "2.7",
                "metadata_8": "2.8"
            },
            "sample3": {
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

For more information see the [output documentation](docs/output.md).

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
