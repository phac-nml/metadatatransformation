import pandas
import numpy
import math

from dateutil.relativedelta import relativedelta
from datetime import datetime

from transformations.constants import (SAMPLE_HEADER, SAMPLE_NAME_HEADER, DATE_FORMAT,
                                       VALID_HEADER_EXTENSION, ERROR_HEADER_EXTENSION,
                                       COLUMNS_AXIS, SPECIAL_ENTRIES_REGEX, BLANK,
                                       AGE_HEADER)

# TODO: PNC-specific metadata in nextflow

# Age Headers:
DATE_OF_BIRTH_HEADER = "host_date_of_birth_DOB"
DATE_HEADER = "calc_earliest_date"
HOST_AGE_HEADER = "host_age"
HOST_AGE_UNIT_HEADER = "host_age_unit"
AGE_HEADERS = [SAMPLE_HEADER, SAMPLE_NAME_HEADER, DATE_OF_BIRTH_HEADER, DATE_HEADER, HOST_AGE_HEADER, HOST_AGE_UNIT_HEADER]

AGE_CONSOLIDATION_THRESHOLD = 1 # Threshold for accepting differences in DOB-based and units-based ages (in years).
AGE_THRESHOLD = 2 # Ages less than this will include a decimal component.
DAYS_IN_YEAR = 365.0
WEEKS_IN_YEAR = 52.0
MONTHS_IN_YEAR = 12.0
MAX_AGE = 150 # years

DAY_UNITS = ["day", "days"]
WEEK_UNITS = ["week", "weeks"]
MONTH_UNITS = ["month", "months"]
YEAR_UNITS = ["year", "years"]

def format_age(age):
    if age < AGE_THRESHOLD and age > -AGE_THRESHOLD:
        formatted_age = "{:.4f}".format(age)
    else:
        formatted_age = "{:.0f}".format(math.floor(age))

    return formatted_age

def calculate_age_between_dates(date_1_string, date_2_string):
    age = numpy.nan
    # numpy.nan, not pandas.NA because numpy.nan is treated as a float.
    # Otherwise, there's a risk of mixing age floats with pandas.NA and having
    # the column be treated as an object column, which will prevent
    # .to_csv(..., float_format=format_age) from working.
    age_valid = False
    age_error = "Unable to calculate age."

    # Are the dates in the correct type (string) and format?
    try:
        date_1 = datetime.strptime(date_1_string, DATE_FORMAT)
        date_2 = datetime.strptime(date_2_string, DATE_FORMAT)

    except (TypeError, ValueError) as error:
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

    return pandas.Series([age, age_valid, age_error])

def calculate_age_by_units(age_string, age_unit_string):
    # Convert age_string into a number:
    try:
        age_number = float(age_string)
    except ValueError:
        return pandas.Series([numpy.nan, False, f"{HOST_AGE_HEADER} ({age_string}) could not be converted to a number"])

    # Calculate age in years:
    if age_unit_string.lower() in (unit.lower() for unit in DAY_UNITS):
        age_in_years = age_number / DAYS_IN_YEAR
        age = pandas.Series([age_in_years, True, ""])
    elif age_unit_string.lower() in (unit.lower() for unit in WEEK_UNITS):
        age_in_years = age_number / WEEKS_IN_YEAR
        age = pandas.Series([age_in_years, True, ""])
    elif age_unit_string.lower() in (unit.lower() for unit in MONTH_UNITS):
        age_in_years = age_number / MONTHS_IN_YEAR
        age = pandas.Series([age_in_years, True, ""])
    elif age_unit_string.lower() in (unit.lower() for unit in YEAR_UNITS):
        age_in_years = age_number
        age = pandas.Series([age_in_years, True, ""])
    else:
        age = pandas.Series([numpy.nan, False, f"invalid {HOST_AGE_UNIT_HEADER} ({age_unit_string})"])

    return age

def consolidate_ages(age1, age2):
    # Are there any problems?
    if pandas.isnull(age1[0]) or pandas.isnull(age2[0]):
        return pandas.Series([numpy.nan, False, "Unexpected error consolidating ages."])

    # Are they the same?
    if(abs(age1[0] - age2[0]) <= AGE_CONSOLIDATION_THRESHOLD):
        return pandas.Series([numpy.mean([age1[0], age2[0]]), True, ""])

    # Too different from each other:
    else:
        return pandas.Series([numpy.nan, False, f"{AGE_HEADER} and {HOST_AGE_HEADER} are greater than {AGE_CONSOLIDATION_THRESHOLD} year(s) different"])

def calculate_age(row):
    age_dob = pandas.Series()
    age_units = pandas.Series()

    # Replace special entries:
    row = row.replace(to_replace=SPECIAL_ENTRIES_REGEX, value=pandas.NA, inplace=False, regex=True)

    # Special entries and blanks in host_age_unit are
    # to be interpretted as "years". At this point,
    # special entries have already been replaced with null,
    # so they'll be treated the same as blanks.
    if (pandas.isnull(row[HOST_AGE_UNIT_HEADER])
        or row[HOST_AGE_UNIT_HEADER] == BLANK):
        row[HOST_AGE_UNIT_HEADER] = YEAR_UNITS[0]

    # If there's a date of birth but no earliest date,
    # then throw an error:
    if not pandas.isnull(row[DATE_OF_BIRTH_HEADER]) and pandas.isnull(row[DATE_HEADER]):
        return pandas.Series([numpy.nan, False, f"{DATE_OF_BIRTH_HEADER} provided but {DATE_HEADER} is missing"])

    # Calculate the date based on the date of birth and date:
    if not pandas.isnull(row[DATE_OF_BIRTH_HEADER]) and not pandas.isnull(row[DATE_HEADER]):
        dob_string = row[DATE_OF_BIRTH_HEADER]
        date_string = row[DATE_HEADER]
        age_dob = calculate_age_between_dates(dob_string, date_string)

    # Calculate the date based on the host age and host age units:
    if not pandas.isnull(row[HOST_AGE_HEADER]) and not pandas.isnull(row[HOST_AGE_UNIT_HEADER]):
        age_string = row[HOST_AGE_HEADER]
        age_unit_string = row[HOST_AGE_UNIT_HEADER]
        age_units = calculate_age_by_units(age_string, age_unit_string)

    # Only a date of birth-based age was calculated:
    if not age_dob.empty and age_units.empty:
        result = age_dob
    # Only a unit-based age was calculated:
    elif age_dob.empty and not age_units.empty:
        result = age_units
    # Both a date of birth-based and unit-based age was calculated:
    elif not age_dob.empty and not age_units.empty:
        # One may contain an error!
        result = consolidate_ages(age_dob, age_units)
    # No age was calculated because of missing data.
    else:
        result = pandas.Series([numpy.nan, False, "Insufficient data to calculate an age."])

    # Check if age is within an acceptable range:
    if (not pandas.isnull(result[0])):

        age_value = result[0]

        # Negative:
        if age_value < 0:
            result = pandas.Series([age_value, False, f"{AGE_HEADER} is negative"])
        # Exactly zero:
        elif age_value == 0:
            result = pandas.Series([age_value, False, f"{AGE_HEADER} cannot be exactly zero"])
        # Too large:
        elif age_value > MAX_AGE:
            result = pandas.Series([age_value, False, f"{AGE_HEADER} is too large"])

    return result

def age(metadata, age_header):
    age_valid_header = age_header + VALID_HEADER_EXTENSION
    age_error_header = age_header + ERROR_HEADER_EXTENSION

    metadata_readable = metadata[AGE_HEADERS].copy(deep=True) # drop extra columns in new copy
    metadata_readable[[age_header, age_valid_header, age_error_header]] = metadata_readable.apply(calculate_age, axis=COLUMNS_AXIS)

    metadata_irida = metadata_readable[[SAMPLE_HEADER, age_header]].copy(deep=True)

    return metadata_readable, metadata_irida