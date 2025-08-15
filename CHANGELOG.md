# phac-nml/metadatatransformation: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025/08/15

### `Added`

- `categorize` transformation: Assigns a categorical variable to a `calc_source_type` column which specifies the type of a sample. Currently limited to PNC values. It expects specific columns: `host_scientific_name`, `host_common_name`, `food_product`, `environmental_site`, `environmental_material` and will assign the following categories: "Human", "Animal", "Food", "Environmental", "Unknown", "Host Conflict" [PR #20](https://github.com/phac-nml/metadatatransformation/pull/20)
- Added auxillary `missing_val()` function to `transform.py` to check if a value is in our list of Special values (indicating things like "Not Available") or if it is a "True" null (like `pandas.NA` or `None` in python) [PR #20](https://github.com/phac-nml/metadatatransformation/pull/20)

## [1.1.1] - 2025/08/07

### `Added`

- Special entries are now ignored when determining the earliest age: `Not Applicable`, `Missing`, `Not Collected`, `Not Provided`, `Restricted Access`, `(blank)` [PR #15](https://github.com/phac-nml/metadatatransformation/pull/15)

### `Changed`

- The pipeline will no longer report empty metadata values in the Irida Next JSON output file for the earliest date transformation, meaning previous "earliest_date" entries will no longer be overwritten within Irida Next. [PR #15](https://github.com/phac-nml/metadatatransformation/pull/15)
- The default column name for the earliest date transformation ("earliest_date") is now "calc_earliest_date". [PR #16](https://github.com/phac-nml/metadatatransformation/pull/16)

## [1.1.0] - 2025/03/17

### `Added`

- `earliest` transformation: finds earliest date among metadata [PR #9](https://github.com/phac-nml/metadatatransformation/pull/9)
- `populate` transformation: populates an output column with a specific value [PR #10](https://github.com/phac-nml/metadatatransformation/pull/10)

### `Fixed`

- A crash when calculating age if an entire date column contained only floats.

## [1.0.0] - 2025/03/07

Initial release of phac-nml/metadatatransformation.

### `Added`

- `lock` transformation: locks metadata in IRIDA Next
- `age` transformation: calculates age between two dates

### `Fixed`

### `Dependencies`

### `Deprecated`

[1.0.0]: https://github.com/phac-nml/metadatatransformation/releases/tag/1.0.0
[1.1.0]: https://github.com/phac-nml/metadatatransformation/releases/tag/1.1.0
[1.1.1]: https://github.com/phac-nml/metadatatransformation/releases/tag/1.1.1
[1.2.0]: https://github.com/phac-nml/metadatatransformation/releases/tag/1.2.0
