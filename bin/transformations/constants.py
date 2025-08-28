# Default Column Headers:
AGE_HEADER = "calc_host_age"
EARLIEST_HEADER = "calc_earliest_date"
POPULATE_HEADER = "populated"

# Headers:
SAMPLE_HEADER = "sample"
SAMPLE_NAME_HEADER = "sample_name"
VALID_HEADER_EXTENSION = "_valid"
ERROR_HEADER_EXTENSION = "_error"

# Other:
DATE_FORMAT = "%Y-%m-%d" # YYYY-MM-DD
ROWS_AXIS = 0 # i.e. axis=0 // axis="rows"
COLUMNS_AXIS = 1 # i.e. axis=1 // axis="columns"

# Special Entries:
NOT_APPLICABLE = "Not Applicable"
MISSING = "Missing"
NOT_COLLECTED = "Not Collected"
NOT_PROVIDED = "Not Provided"
RESTRICTED_ACCESS = "Restricted Access"
BLANK = ""

SPECIAL_ENTRIES = [NOT_APPLICABLE, MISSING, NOT_COLLECTED,
                    NOT_PROVIDED, RESTRICTED_ACCESS, BLANK]
SPECIAL_ENTRIES_REGEX = ['(?i)^{}$'.format(x) for x in SPECIAL_ENTRIES] # case insensitive
