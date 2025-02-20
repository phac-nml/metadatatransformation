#!/usr/bin/env python

import argparse
import pathlib
import pandas

from dateutil.relativedelta import relativedelta
from datetime import datetime

# Column headers:
SAMPLE_HEADER = "sample"
SAMPLE_NAME_HEADER = "sample_name"
AGE_HEADER = "age"

# Column indices:
DATE_1_INDEX = 2
DATE_2_INDEX = 3

# Transformations:
LOCK = "lock"
AGE = "age"

# Other:
AGE_THRESHOLD = 2 # Ages less than this will include a decimal component.

def remove_empty_columns(metadata):
    metadata.dropna(axis="columns", how="all", inplace=True)

def lock(metadata):
    metadata_readable = metadata.copy(deep=True)
    metadata_irida = metadata.drop(columns=[SAMPLE_NAME_HEADER], inplace=False)

    return metadata_readable, metadata_irida

def format_age(age):
    if age < AGE_THRESHOLD:
        formatted_age = "{:.4f}".format(age)
    else:
        formatted_age = "{:.0f}".format(age)

    return formatted_age

def calculate_age(row):
    pattern = "%Y-%m-%d"

    date_1_string = row[DATE_1_INDEX]
    date_2_string = row[DATE_2_INDEX]

    date_1 = datetime.strptime(date_1_string, pattern)
    date_2 = datetime.strptime(date_2_string, pattern)

    relative_delta = relativedelta(date_2, date_1)

    if relative_delta.years < AGE_THRESHOLD:
        time_delta = date_2 - date_1
        age = time_delta.days / 365.0
    else:
        age = relative_delta.years

    return age

def age(metadata):
    metadata_readable = metadata.iloc[:, :DATE_2_INDEX+1].copy(deep=True) # drop extra columns in new copy
    metadata_readable[AGE_HEADER] = metadata_readable.apply(calculate_age, axis="columns")

    metadata_irida = metadata_readable[[SAMPLE_HEADER, AGE_HEADER]].copy(deep=True)

    return metadata_readable, metadata_irida

def main():
    parser = argparse.ArgumentParser(
        prog="Transform Metadata",
        description="Transforms metadata according to the passed transformation. Generates both human- and machine-readable output files.")

    parser.add_argument("input", type=pathlib.Path,
                        help="The CSV-formatted input file to transform.")
    parser.add_argument("transformation", choices=[LOCK, AGE],
                        help="The type of transformation to perform.")
    
    args = parser.parse_args()
    metadata = pandas.read_csv(args.input)

    if (args.transformation == LOCK):
        metadata_readable, metadata_irida = lock(metadata)
    elif (args.transformation == AGE):
        metadata_readable, metadata_irida = age(metadata)

    remove_empty_columns(metadata_irida)

    metadata_readable.to_csv("results.csv", index=False, float_format=format_age)
    metadata_irida.to_csv("transformation.csv", index=False)

if __name__ == '__main__':
    main()
