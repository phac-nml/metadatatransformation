#!/usr/bin/env python

import argparse
import pathlib
import pandas

from transformations.age import age, age_pnc
from transformations.constants import *

# Transformations:
LOCK = "lock"
AGE = "age"
AGE_PNC = "age_pnc"
EARLIEST = "earliest"
POPULATE = "populate"
CATEGORIZE = "categorize"
PNC = "pnc"

# Default Values:
POPULATE_VALUE = "NA"
UNKNOWN_VALUE = "Unknown"

# Output Files:
RESULTS_PATH = "results.csv"
TRANSFORMATION_PATH = "transformation.csv"

def missing_val(x, empty_strs = SPECIAL_ENTRIES):
    return (pandas.isna(x) | (x in empty_strs + [None]))

def remove_any_NA_rows(metadata):
    # If at least one entry in the row is NA,
    # then remove the whole row.
    metadata.dropna(axis=ROWS_AXIS, how="any", inplace=True)

def remove_all_NA_rows(metadata):
    # If all entries in the row are NA,
    # then remove the whole row.
    # Need to ignore "sample" column.
    metadata.dropna(axis=ROWS_AXIS, how="all", inplace=True, subset=metadata.columns.difference([SAMPLE_HEADER]))

def remove_all_NA_columns(metadata):
    # If all entries in the column are NA,
    # then remove the whole column.
    # We need to check if the data frame is empty,
    # because the "sample" column will be removed
    # if there's no samples (i.e. it's empty).
    if not metadata.empty:
        metadata.dropna(axis=COLUMNS_AXIS, how="all", inplace=True)

def populate(metadata, populate_header, populate_value):
    metadata_readable = metadata.copy(deep=True)
    metadata_readable[[populate_header]] = populate_value

    metadata_irida = metadata_readable[[SAMPLE_HEADER, populate_header]].copy(deep=True)

    return metadata_readable, metadata_irida

def calculate_earliest_date(row):
    earliest = pandas.NA
    earliest_valid = False
    earliest_error = "Unable to find the earliest date."

    dates = []

    # Replace special entries (not in place):

    # We need everything to be a string (pandas.NA) and not another
    # type (numpy.nan, etc.).
    replaced = row.fillna(value=pandas.NA, inplace=False)

    # Drop "sample" and "sample_name" if they exist:
    replaced = replaced.drop([SAMPLE_HEADER, SAMPLE_NAME_HEADER], errors="ignore")

    # We need to check for all NA at this point, because numpy
    # will fail to replace if everything is NA:
    if (replaced.isnull().values.all(axis=ROWS_AXIS)):
        earliest = pandas.NA
        earliest_valid = False
        earliest_error = "No data was found."

        result = pandas.Series([earliest, earliest_valid, earliest_error]), dates
        return result

    # Not everything is NA. Replace special entries:
    replaced = replaced.replace(to_replace=SPECIAL_ENTRIES_REGEX, value=pandas.NA, inplace=False, regex=True)

    # After the replacement, are all dates NA?
    # This will happen when the row is only
    # special entries and blank, which at this point
    # are all converted to pandas.NA.
    if (replaced.isnull().values.all(axis=ROWS_AXIS)):
        earliest = pandas.NA
        earliest_valid = False
        earliest_error = "No dates were found."

        result = pandas.Series([earliest, earliest_valid, earliest_error]), dates
        return result

    try:
        dates = pandas.to_datetime(replaced, format="%Y-%m-%d", errors="raise")
        dates = dates.dropna()

    except ValueError:
        earliest = pandas.NA
        earliest_valid = False
        earliest_error = "At least one of the dates are incorrectly formatted."

        result = pandas.Series([earliest, earliest_valid, earliest_error]), dates
        return result

    # At least one valid date was found:
    if len(dates) > 0:
        earliest = min(dates).strftime(DATE_FORMAT)
        earliest_valid = True
        earliest_error = ""

    result = pandas.Series([earliest, earliest_valid, earliest_error]), dates
    return result

def find_earliest_date_pnc(row):
    MIN_DATE = pandas.to_datetime("1900-01-01")
    MIN_SAMPLE_RECEIVED_DATE_NML = pandas.to_datetime("1995-01-01")
    MIN_SEQUENCING_DATE = pandas.to_datetime("2007-01-01")

    earliest, dates = calculate_earliest_date(row)

    if(len(dates) > 0):
        # Any of the dates are too old (the oldest date check):
        if(len(dates[dates < MIN_DATE]) > 0):
            earliest = pandas.NA
            earliest_valid = False
            earliest_error = "At least one of the dates is too old."

            return pandas.Series([earliest, earliest_valid, earliest_error])

        # The NML sample received date is too old:
        elif(PNC_EARLIEST_DATE_SAMPLE_RECEIVED_DATE_NML in dates and dates[PNC_EARLIEST_DATE_SAMPLE_RECEIVED_DATE_NML] < MIN_SAMPLE_RECEIVED_DATE_NML):
            earliest = pandas.NA
            earliest_valid = False
            earliest_error = "The NML sample received date is too old."

            return pandas.Series([earliest, earliest_valid, earliest_error])

        # The sequencing date is too old:
        elif(PNC_EARLIEST_DATE_SEQUENCING_DATE in dates and dates[PNC_EARLIEST_DATE_SEQUENCING_DATE] < MIN_SEQUENCING_DATE):
            earliest = pandas.NA
            earliest_valid = False
            earliest_error = "The sequencing date is too old."

            return pandas.Series([earliest, earliest_valid, earliest_error])

    return earliest

def find_earliest_date(row):
    earliest, dates = calculate_earliest_date(row)
    return earliest

def earliest(metadata, earliest_header, function):
    earliest_valid_header = earliest_header + VALID_HEADER_EXTENSION
    earliest_error_header = earliest_header + ERROR_HEADER_EXTENSION

    metadata_readable = metadata.copy(deep=True)
    metadata_readable[[earliest_header, earliest_valid_header, earliest_error_header]] = metadata_readable.apply(function, axis=COLUMNS_AXIS)

    metadata_irida = metadata_readable[[SAMPLE_HEADER, earliest_header]].copy(deep=True)

    return metadata_readable, metadata_irida

def lock(metadata):
    metadata_readable = metadata.copy(deep=True)
    metadata_irida = metadata.drop(columns=[SAMPLE_NAME_HEADER], inplace=False)

    return metadata_readable, metadata_irida

def categorize(metadata):
    # Check for required headers (output error message and blank if missing)
    metadata_readable = metadata.copy(deep=True)

    missing_required_headers = [col for col in CATEGORIZE_HEADERS if col not in metadata.columns]
    included_required_headers = [col for col in CATEGORIZE_HEADERS if col in metadata.columns]

    if (len(missing_required_headers) > 0):
        metadata_irida = pandas.DataFrame({SAMPLE_HEADER:[]})
        metadata_readable[CATEGORIZE_RESULTS_HEADERS] = pandas.Series([pandas.NA, False, "Missing required headers: " + str(missing_required_headers)])
        metadata_readable = metadata_readable[[SAMPLE_HEADER, SAMPLE_NAME_HEADER] + included_required_headers + CATEGORIZE_RESULTS_HEADERS]
        return metadata_readable, metadata_irida

    # Helper fun for row-wise categorization
    def categorize_row(row):
        if ((row["host_scientific_name"] == "Homo sapiens (Human)") & (row["host_common_name"] == "Human NCBITaxon:9606")):
            return "Human"
        elif ((row["host_scientific_name"] == "Homo sapiens (Human)") & missing_val(row["host_common_name"])):
            return "Human"
        elif (missing_val(row["host_scientific_name"]) & (row["host_common_name"] == "Human NCBITaxon:9606")):
            return "Human"
        elif ((row["host_scientific_name"] == "Homo sapiens (Human)") & (row["host_common_name"] != "Human NCBITaxon:9606")):
            return "Host Conflict"
        elif ((row["host_scientific_name"] != "Homo sapiens (Human)") & (row["host_common_name"] == "Human NCBITaxon:9606")):
            return "Host Conflict"
        elif ((not missing_val(row["host_scientific_name"])) | (not missing_val(row["host_common_name"]))):
            return "Animal"
        elif ((not missing_val(row["food_product"]))):
            return "Food"
        elif ((not missing_val(row["environmental_site"])) | (not missing_val(row["environmental_material"]))):
            return "Environmental"
        else:
            return UNKNOWN_VALUE

    metadata_readable[CATEGORIZE_SOURCE_TYPE_HEADER] = metadata_readable.apply(categorize_row, axis = COLUMNS_AXIS)
    metadata_readable[CATEGORIZE_VALID_HEADER] = True
    metadata_readable[CATEGORIZE_ERROR_HEADER] = ""

    metadata_readable = metadata_readable[[SAMPLE_HEADER, SAMPLE_NAME_HEADER] + included_required_headers + CATEGORIZE_RESULTS_HEADERS]
    metadata_irida = metadata_readable[[SAMPLE_HEADER, CATEGORIZE_SOURCE_TYPE_HEADER]].copy(deep=True)

    return metadata_readable, metadata_irida

def pnc(metadata):
    # The PNC transformation requires many exactly-matching
    # metadata column headers:
    required_headers = [SAMPLE_HEADER] + PNC_EARLIEST_DATE_HEADERS + CATEGORIZE_HEADERS + PNC_AGE_HEADERS

    # The PNC_AGE_DATE_HEADER is normally required for the
    # Age PNC transformation, but is calculated during the
    # chained PNC transformation during the earliest date step.
    if(PNC_AGE_DATE_HEADER in required_headers):
        required_headers.remove(PNC_AGE_DATE_HEADER)

    missing_headers = [col for col in required_headers if col not in metadata.columns]

    if len(missing_headers) > 0:
        metadata_irida = pandas.DataFrame({SAMPLE_HEADER:[]})
        metadata_readable = metadata.copy(deep=True)
        metadata_readable[CATEGORIZE_RESULTS_HEADERS] = pandas.Series([pandas.NA, False, "Missing headers: " + "; ".join(missing_headers)])
        metadata_readable[PNC_EARLIEST_RESULTS_HEADERS] = pandas.Series([pandas.NA, False, "Missing headers: " + "; ".join(missing_headers)])
        metadata_readable[PNC_AGE_RESULTS_HEADERS] = pandas.Series([pandas.NA, False, "Missing headers: " + "; ".join(missing_headers)])
        return metadata_readable, metadata_irida

    # Categorize
    categorize_readable, categorize_irida = categorize(metadata)
    categorize_readable = categorize_readable[CATEGORIZE_COMBINED_RESULTS_HEADERS]

    # Earliest
    metadata_earliest = metadata[[SAMPLE_HEADER] + PNC_EARLIEST_DATE_HEADERS]
    earliest_readable, earliest_irida = earliest(metadata_earliest, EARLIEST_HEADER_PNC, find_earliest_date_pnc)
    earliest_readable = earliest_readable[PNC_EARLIEST_DATE_COMBINED_RESULTS_HEADERS]

    # Age PNC
    metadata_age_pnc = metadata.merge(earliest_irida, how="inner", on=SAMPLE_HEADER)
    age_pnc_readable, age_pnc_irida = age_pnc(metadata_age_pnc, AGE_PNC_HEADER)
    age_pnc_readable = age_pnc_readable[PNC_AGE_COMBINED_RESULTS_HEADERS]

    # Merge
    metadata_readable = categorize_readable.merge(earliest_readable, how="inner", on=SAMPLE_HEADER)
    metadata_readable = metadata_readable.merge(age_pnc_readable, how="inner", on=SAMPLE_HEADER)

    metadata_irida = categorize_irida.merge(earliest_irida, how="inner", on=SAMPLE_HEADER)
    metadata_irida = metadata_irida.merge(age_pnc_irida, how="inner", on=SAMPLE_HEADER)

    return metadata_readable, metadata_irida

def main():
    parser = argparse.ArgumentParser(
        prog="Transform Metadata",
        description="Transforms metadata according to the passed transformation. Generates both human- and machine-readable output files.")

    parser.add_argument("input", type=pathlib.Path,
                        help="The CSV-formatted input file to transform.")
    parser.add_argument("transformation", choices=[LOCK, AGE, AGE_PNC, EARLIEST, POPULATE, CATEGORIZE, PNC],
                        help="The type of transformation to perform.")
    parser.add_argument("--age_header", default=AGE_HEADER, required=False,
                        help="The output column header for the calculated age.")
    parser.add_argument("--earliest_header", default=EARLIEST_HEADER, required=False,
                        help="The output column header for the earliest date.")
    parser.add_argument("--populate_header", default=POPULATE_HEADER, required=False,
                        help="The output column header for the populate transformation.")
    parser.add_argument("--populate_value", default=POPULATE_VALUE, required=False,
                        help="The value to populate the specified column with for the populate transformation.")

    args = parser.parse_args()
    metadata = pandas.read_csv(args.input)

    if (args.transformation == LOCK):
        metadata_readable, metadata_irida = lock(metadata)

        remove_all_NA_columns(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == AGE):
        metadata_readable, metadata_irida = age(metadata, args.age_header)

        remove_all_NA_columns(metadata_irida)
        remove_any_NA_rows(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == AGE_PNC):
        metadata_readable, metadata_irida = age_pnc(metadata, AGE_PNC_HEADER)

        remove_all_NA_columns(metadata_irida)
        remove_any_NA_rows(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == EARLIEST):
        metadata_readable, metadata_irida = earliest(metadata, args.earliest_header, find_earliest_date)

        remove_all_NA_columns(metadata_irida)
        remove_any_NA_rows(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == POPULATE):
        metadata_readable, metadata_irida = populate(metadata, args.populate_header, args.populate_value)

        remove_all_NA_columns(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == CATEGORIZE):
        metadata_readable, metadata_irida = categorize(metadata)

        if len(metadata_irida) > 0:
            remove_all_NA_columns(metadata_irida)

        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == PNC):
        metadata_readable, metadata_irida = pnc(metadata)

        remove_all_NA_columns(metadata_irida)
        remove_all_NA_rows(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

if __name__ == '__main__':
    main()
