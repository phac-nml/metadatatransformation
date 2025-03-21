# phac-nml/metadatatransformation: Usage

## Introduction

This pipeline transforms metadata from IRIDA Next.

## Sample sheet input

You will need to create a sample sheet with information about the samples you would like to analyse before running the pipeline. Use this parameter to specify its location. It has to be a comma-separated file with 10 columns, and a header row as shown in the examples below.

```bash
--input '[path to samplesheet file]'
```

### Full samplesheet

The input samplesheet must contain the following columns: `sample`, and `metadata_1` through `metadata_8`. The IDs within a samplesheet should be unique. You may optionally provide a `sample_name` column, which will replace the Irida Next IDs in the `sample` column if available. All other columns will be ignored.

A final samplesheet file contain the `sample_name` column may look something like the one below.

```csv title="samplesheet.csv"
sample,sample_name,metadata_1,metadata_2,metadata_3,metadata_4,metadata_5,metadata_6,metadata_7,metadata_8
sample1,"ABC",1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8
sample2,"DEF",2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8
sample3,"GHI",3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8
```

| Column                   | Description                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `sample`                 | Sample ID. Samples should be unique within a samplesheet. Likely Irida Next IDs.                                                           |
| `sample_name`            | Sample name. Likely user-provided IDs that should be unique, but are not required to be unique. Will be used over `sample` when available. |
| `metadata_1..metadata_8` | Metadata that will be used in the metadata transformations.                                                                                |

An [example samplesheet](../assets/samplesheet.csv) has been provided with the pipeline.

## Running the pipeline

The typical command for running the pipeline is as follows:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results --transformation lock
```

This will launch the pipeline with the `singularity` configuration profile. See below for more information about profiles.

Note that the pipeline will create the following files in your working directory:

```bash
work                # Directory containing the nextflow working files
<OUTDIR>            # Finished results in specified location (defined with --outdir)
.nextflow_log       # Log file from Nextflow
# Other nextflow hidden files, eg. history of pipeline runs and old logs.
```

If you wish to repeatedly use the same parameters for multiple runs, rather than specifying each flag in the command, you can specify these in a params file.

Pipeline settings can be provided in a `yaml` or `json` file via `-params-file <file>`.

Do not use `-c <file>` to specify parameters as this will result in errors. Custom config files specified with `-c` must only be used for [tuning process resource specifications](https://nf-co.re/docs/usage/configuration#tuning-workflow-resources), other infrastructural tweaks (such as output directories), or module arguments (args).

### Lock

The lock transformation may be run as follows:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results --transformation lock
```

You may wish to specify the `--metadata_1_header` through `--metadata_8_header` parameters to ensure the metadata is named as desired:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results --transformation lock --metadata_1_header country --metadata_2_header outbreak
```

### Age

The calculate age transformation may be run as follows:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/age/success_failure_mix.csv --outdir results --transformation age --metadata_1_header "date_of_birth" --metadata_2_header "collection_date" --age_header "age_at_collection"
```

For this transformation, the `metadata_1` column of the sample sheet is understood as the date of birth and the `metadata_2` column is understood as the date at which to calculate the age.

The following parameters can be used to rename CSV-generated output columns and Irida Next fields as follows:

- `--metadata_1_header`: names the date of birth column header
- `--metadata_2_header`: names the current/target data column header
- `--age_header`: names the calculated age column header and related output columns

### Earliest

The earliest date transformation may be run as follows:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/earliest/basic.csv --outdir results --transformation earliest
```

For this transformation, the `metadata_1` column through `metadata_8` column of the sample sheet are understood as containing a date or being empty. The transformation will determine the earliest date among these metadata columns.

You may wish to specify the `--metadata_1_header` through `--metadata_8_header` parameters to provide appropriate column names in the `results.csv` file, but these headers do not affect results returned to IRIDA Next.

If at least one metadata column contains non-empty data that does not conform to the expected "YYYY-MM-DD" date format, then the sample will report an error and no date will be reported for the sample (even if one other valid date appears among the invalid metadata for that sample).

### Populate

The populate transformation may be run as follows:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/populate/basic.csv --outdir results --transformation populate --populate_header "new_header" --populate_value "new_value"
```

For this transformation, all input metadata (`metadata_1` through `metadata_8`) will be ignored. However, the transformation will write or overwrite the input metadata as specified by `--populate_header`. The value specified by `--populate_value` will be written for every sample under the column specified by `--populate_header`.

For example, when running the transformation with the following sample sheet:

```
sample,sample_name,metadata_1,metadata_2,metadata_3,metadata_4,metadata_5,metadata_6,metadata_7,metadata_8
sample1,"ABC",1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8
sample2,"DEF",2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8
sample3,"GHI",3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8
```

and command:

```bash
nextflow run phac-nml/metadatatransformation -profile singularity --input tests/data/samplesheets/populate/basic.csv --outdir results --transformation populate --populate_header "new_header" --populate_value "new_value"
```

following output `results.csv` file will be generated:

```
sample,sample_name,metadata_1,metadata_2,metadata_3,metadata_4,metadata_5,metadata_6,metadata_7,metadata_8,new_header
sample1,ABC,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,new_value
sample2,DEF,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,new_value
sample3,GHI,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,new_value
```

and the following `transformation.csv` file (written back to IRIDA Next) will be generated:

```
sample,new_header
sample1,new_value
sample2,new_value
sample3,new_value
```

### Reproducibility

It is a good idea to specify a pipeline version when running the pipeline on your data. This ensures that a specific version of the pipeline code and software are used when you run your pipeline. If you keep using the same tag, you'll be running the same version of the pipeline, even if there have been changes to the code since.

First, go to the [phac-nml/metadatatransformation page](https://github.com/phac-nml/metadatatransformation) and find the latest pipeline version - numeric only (eg. `1.3.1`). Then specify this when running the pipeline with `-r` (one hyphen) - eg. `-r 1.3.1`. Of course, you can switch to another version by changing the number after the `-r` flag.

This version number will be logged in reports when you run the pipeline, so that you'll know what you used when you look back in the future.

To further assist in reproducbility, you can use share and re-use [parameter files](#running-the-pipeline) to repeat pipeline runs with the same settings without having to write out a command with every single parameter.

If you wish to share such profile (such as upload as supplementary material for academic publications), make sure to NOT include cluster specific paths to files, nor institutional specific profiles.

## Core Nextflow arguments

These options are part of Nextflow and use a _single_ hyphen (pipeline parameters use a double-hyphen).

### `-profile`

Use this parameter to choose a configuration profile. Profiles can give configuration presets for different compute environments.

Several generic profiles are bundled with the pipeline which instruct the pipeline to use software packaged using different methods (Docker, Singularity, Podman, Shifter, Charliecloud, Apptainer, Conda) - see below.

We highly recommend the use of Docker or Singularity containers for full pipeline reproducibility, however when this is not possible, Conda is also supported.

The pipeline also dynamically loads configurations from [https://github.com/nf-core/configs](https://github.com/nf-core/configs) when it runs, making multiple config profiles for various institutional clusters available at run time. For more information and to see if your system is available in these configs please see the [nf-core/configs documentation](https://github.com/nf-core/configs#documentation).

Note that multiple profiles can be loaded, for example: `-profile test,docker` - the order of arguments is important!
They are loaded in sequence, so later profiles can overwrite earlier profiles.

If `-profile` is not specified, the pipeline will run locally and expect all software to be installed and available on the `PATH`. This is _not_ recommended, since it can lead to different results on different machines dependent on the computer enviroment.

- `test`
  - A profile with a complete configuration for automated testing
  - Includes links to test data so needs no other parameters
- `docker`
  - A generic configuration profile to be used with [Docker](https://docker.com/)
- `singularity`
  - A generic configuration profile to be used with [Singularity](https://sylabs.io/docs/)
- `podman`
  - A generic configuration profile to be used with [Podman](https://podman.io/)
- `shifter`
  - A generic configuration profile to be used with [Shifter](https://nersc.gitlab.io/development/shifter/how-to-use/)
- `charliecloud`
  - A generic configuration profile to be used with [Charliecloud](https://hpc.github.io/charliecloud/)
- `apptainer`
  - A generic configuration profile to be used with [Apptainer](https://apptainer.org/)
- `conda`
  - A generic configuration profile to be used with [Conda](https://conda.io/docs/). Please only use Conda as a last resort i.e. when it's not possible to run the pipeline with Docker, Singularity, Podman, Shifter, Charliecloud, or Apptainer.

### `-resume`

Specify this when restarting a pipeline. Nextflow will use cached results from any pipeline steps where the inputs are the same, continuing from where it got to previously. For input to be considered the same, not only the names must be identical but the files' contents as well. For more info about this parameter, see [this blog post](https://www.nextflow.io/blog/2019/demystifying-nextflow-resume.html).

You can also supply a run name to resume a specific run: `-resume [run-name]`. Use the `nextflow log` command to show previous run names.

### `-c`

Specify the path to a specific config file (this is a core Nextflow command). See the [nf-core website documentation](https://nf-co.re/usage/configuration) for more information.

## Custom configuration

### Resource requests

Whilst the default requirements set within the pipeline will hopefully work for most people and with most input data, you may find that you want to customise the compute resources that the pipeline requests. Each step in the pipeline has a default set of requirements for number of CPUs, memory and time. For most of the steps in the pipeline, if the job exits with any of the error codes specified [here](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/base.config#L18) it will automatically be resubmitted with higher requests (2 x original, then 3 x original). If it still fails after the third attempt then the pipeline execution is stopped.

To change the resource requests, please see the [max resources](https://nf-co.re/docs/usage/configuration#max-resources) and [tuning workflow resources](https://nf-co.re/docs/usage/configuration#tuning-workflow-resources) section of the nf-core website.

### Custom Containers

In some cases you may wish to change which container or conda environment a step of the pipeline uses for a particular tool. By default nf-core pipelines use containers and software from the [biocontainers](https://biocontainers.pro/) or [bioconda](https://bioconda.github.io/) projects. However in some cases the pipeline specified version maybe out of date.

To use a different container from the default container or conda environment specified in a pipeline, please see the [updating tool versions](https://nf-co.re/docs/usage/configuration#updating-tool-versions) section of the nf-core website.

### Custom Tool Arguments

A pipeline might not always support every possible argument or option of a particular tool used in pipeline. Fortunately, nf-core pipelines provide some freedom to users to insert additional parameters that the pipeline does not include by default.

To learn how to provide additional arguments to a particular tool of the pipeline, please see the [customising tool arguments](https://nf-co.re/docs/usage/configuration#customising-tool-arguments) section of the nf-core website.

### nf-core/configs

In most cases, you will only need to create a custom config as a one-off but if you and others within your organisation are likely to be running nf-core pipelines regularly and need to use the same settings regularly it may be a good idea to request that your custom config file is uploaded to the `nf-core/configs` git repository. Before you do this please can you test that the config file works with your pipeline of choice using the `-c` parameter. You can then create a pull request to the `nf-core/configs` repository with the addition of your config file, associated documentation file (see examples in [`nf-core/configs/docs`](https://github.com/nf-core/configs/tree/master/docs)), and amending [`nfcore_custom.config`](https://github.com/nf-core/configs/blob/master/nfcore_custom.config) to include your custom profile.

See the main [Nextflow documentation](https://www.nextflow.io/docs/latest/config.html) for more information about creating your own configuration files.

## Azure Resource Requests

To be used with the `azurebatch` profile by specifying the `-profile azurebatch`.
We recommend providing a compute `params.vm_type` of `Standard_D16_v3` VMs by default but these options can be changed if required.

Note that the choice of VM size depends on your quota and the overall workload during the analysis.
For a thorough list, please refer the [Azure Sizes for virtual machines in Azure](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes).

## Running in the background

Nextflow handles job submissions and supervises the running jobs. The Nextflow process must run until the pipeline is finished.

The Nextflow `-bg` flag launches Nextflow in the background, detached from your terminal so that the workflow does not stop if you log out of your session. The logs are saved to a file.

Alternatively, you can use `screen` / `tmux` or similar tool to create a detached session which you can log back into at a later time.
Some HPC setups also allow you to run nextflow within a cluster job submitted your job scheduler (from where it submits more jobs).

## Nextflow memory requirements

In some cases, the Nextflow Java virtual machines can start to request a large amount of memory.
We recommend adding the following line to your environment to limit this (typically in `~/.bashrc` or `~./bash_profile`):

```bash
NXF_OPTS='-Xms1g -Xmx4g'
```
