#!/usr/bin/env python

import argparse
import pathlib
import pandas
import numpy
import math

from dateutil.relativedelta import relativedelta
from datetime import datetime

# Column headers:
SAMPLE_HEADER = "sample"
SAMPLE_NAME_HEADER = "sample_name"
AGE_HEADER = "age"
EARLIEST_HEADER = "earliest_date"
VALID_HEADER_EXTENSION = "_valid"
ERROR_HEADER_EXTENSION = "_error"

# Column indices:
DATE_1_INDEX = 2
DATE_2_INDEX = 3

# Transformations:
LOCK = "lock"
AGE = "age"
EARLIEST = "earliest"

# Output Files:
RESULTS_PATH = "results.csv"
TRANSFORMATION_PATH = "transformation.csv"

# Other:
DATE_FORMAT = "%Y-%m-%d" # YYYY-MM-DD
AGE_THRESHOLD = 2 # Ages less than this will include a decimal component.
DAYS_IN_YEAR = 365.0

def remove_empty_columns(metadata):
    metadata.dropna(axis="columns", how="all", inplace=True)

def find_earliest_date(row):
    earliest = ""
    earliest_valid = False
    earliest_error = "Unable to find the earliest age."

    dates = []

    # Are ALL dates missing?
    if (row.iloc[DATE_1_INDEX:].isnull().values.all(axis=0) or
        row.iloc[DATE_1_INDEX:].isna().values.all(axis=0)):
        earliest = ""
        earliest_valid = False
        earliest_error = "No data was found."

        return pandas.Series([earliest, earliest_valid, earliest_error])

    # Check all dates in the row:
    for date_string in row.iloc[DATE_1_INDEX:]:

        # Ignore missing values:
        if (pandas.isna(date_string) or date_string == ""):
            continue

        # Is the date string in the correct format?
        if isinstance(date_string, str):
            try:
                date = datetime.strptime(date_string, DATE_FORMAT)
                dates.append(date)

            except ValueError:
                earliest = ""
                earliest_valid = False
                earliest_error = "At least one of the date values are incorrectly formatted."

                return pandas.Series([earliest, earliest_valid, earliest_error])

        # The value is not null or NA, and is formatted as something other than a string.
        else:
            earliest = ""
            earliest_valid = False
            earliest_error = "At least one of the date values are incorrectly formatted."

            return pandas.Series([earliest, earliest_valid, earliest_error])

    # At least one valid date was found:
    if len(dates) > 0:
        earliest = min(dates).strftime(DATE_FORMAT)
        earliest_valid = True
        earliest_error = ""

    result = pandas.Series([earliest, earliest_valid, earliest_error])

    return result

def earliest(metadata, earliest_header):
    earliest_valid_header = earliest_header + VALID_HEADER_EXTENSION
    earliest_error_header = earliest_header + ERROR_HEADER_EXTENSION

    metadata_readable = metadata.copy(deep=True)
    metadata_readable[[earliest_header, earliest_valid_header, earliest_error_header]] = metadata_readable.apply(find_earliest_date, axis="columns")

    metadata_irida = metadata_readable[[SAMPLE_HEADER, earliest_header]].copy(deep=True)

    return metadata_readable, metadata_irida

def lock(metadata):
    metadata_readable = metadata.copy(deep=True)
    metadata_irida = metadata.drop(columns=[SAMPLE_NAME_HEADER], inplace=False)

    return metadata_readable, metadata_irida

def format_age(age):
    if age < AGE_THRESHOLD:
        formatted_age = "{:.4f}".format(age)
    else:
        formatted_age = "{:.0f}".format(math.floor(age))

    return formatted_age

def calculate_age(row):
    age = numpy.nan
    # numpy.nan, not pandas.NA because numpy.nan is treated as a float.
    # Otherwise, there's a risk of mixing age floats with pandas.NA and having
    # the column be treated as an object column, which will prevent
    # .to_csv(..., float_format=format_age) from working.
    age_valid = False
    age_error = "Unable to calculate age."

    # Is a date missing?
    if pandas.isnull(row.iloc[DATE_1_INDEX]) or pandas.isnull(row.iloc[DATE_2_INDEX]):
        age = numpy.nan
        age_valid = False
        age_error = "At least one of the dates is missing."

        return pandas.Series([age, age_valid, age_error])

    date_1_string = row.iloc[DATE_1_INDEX]
    date_2_string = row.iloc[DATE_2_INDEX]

    # Are the dates in the correct format?
    try:
        date_1 = datetime.strptime(date_1_string, DATE_FORMAT)
        date_2 = datetime.strptime(date_2_string, DATE_FORMAT)

    except ValueError:
        age = numpy.nan
        age_valid = False
        age_error = "The date format does not match the expected format (YYYY-MM-DD)."

        return pandas.Series([age, age_valid, age_error])

    # Calculate the relative delta in calendar time:
    relative_delta = relativedelta(date_2, date_1)

    # Under age threshold, calculate as (days/days_in_year):
    # Note: this is inaccurate, because how many days is a year?
    if relative_delta.years < AGE_THRESHOLD:
        time_delta = date_2 - date_1
        age = time_delta.days / DAYS_IN_YEAR

    # Age meets threshold, calculate as calendar years:
    else:
        age = relative_delta.years
        age_valid = True

    # Positive age:
    if age >= 0:
        age_valid = True
        age_error = ""

    # Negative age, dates reversed:
    else:
        age = numpy.nan
        age_valid = False
        age_error = "The dates are reversed."

    result = pandas.Series([age, age_valid, age_error])

    return result

def age(metadata, age_header):
    age_valid_header = age_header + VALID_HEADER_EXTENSION
    age_error_header = age_header + ERROR_HEADER_EXTENSION

    metadata_readable = metadata.iloc[:, :DATE_2_INDEX+1].copy(deep=True) # drop extra columns in new copy
    metadata_readable[[age_header, age_valid_header, age_error_header]] = metadata_readable.apply(calculate_age, axis="columns")

    metadata_irida = metadata_readable[[SAMPLE_HEADER, age_header]].copy(deep=True)

    return metadata_readable, metadata_irida

def main():
    parser = argparse.ArgumentParser(
        prog="Transform Metadata",
        description="Transforms metadata according to the passed transformation. Generates both human- and machine-readable output files.")

    parser.add_argument("input", type=pathlib.Path,
                        help="The CSV-formatted input file to transform.")
    parser.add_argument("transformation", choices=[LOCK, AGE, EARLIEST],
                        help="The type of transformation to perform.")
    parser.add_argument("--age_header", default=AGE_HEADER, required=False,
                        help="The output column header for the calculated age.")
    parser.add_argument("--earliest_header", default=EARLIEST_HEADER, required=False,
                        help="The output column header for the earliest date.")

    args = parser.parse_args()
    metadata = pandas.read_csv(args.input)

    if (args.transformation == LOCK):
        metadata_readable, metadata_irida = lock(metadata)

        remove_empty_columns(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

    elif (args.transformation == AGE):
        metadata_readable, metadata_irida = age(metadata, args.age_header)

        remove_empty_columns(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False, float_format=format_age)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False, float_format=format_age)

    elif (args.transformation == EARLIEST):
        metadata_readable, metadata_irida = earliest(metadata, args.earliest_header)

        remove_empty_columns(metadata_irida)
        metadata_readable.to_csv(RESULTS_PATH, index=False)
        metadata_irida.to_csv(TRANSFORMATION_PATH, index=False)

if __name__ == '__main__':
    main()
