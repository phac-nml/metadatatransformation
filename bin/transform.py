#!/usr/bin/env python

import argparse
import pathlib
import csv

LOCK = "lock"
AGE = "age"

def lock(metadata):

    transformation = [] # Machine-readable
    results = [] # Human-readable

    # Machine-readable:
    # Slice out the "sample_name" column.
    SAMPLE_NAME = "sample_name"
    metadata_headers = metadata[0]

    sample_name_index = metadata_headers.index(SAMPLE_NAME)

    for row in metadata:
        transformation.append([row[0]] + row[sample_name_index+1:])

    # Human-readable:
    for row in metadata:
        results.append(row)

    return transformation, results

def write_metadata(metadata, path):

    with open(path, "w") as output_file:
        writer = csv.writer(output_file, delimiter=",")
        writer.writerows(metadata)

def parse_metadata(input_path):

    metadata = []

    with open(input_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            metadata.append(row)

    return metadata

def main():

    parser = argparse.ArgumentParser(
        prog="Transform Metadata",
        description="Transforms metadata according to the passed transformation. Generates both human- and machine-readable output files.")

    parser.add_argument("input", type=pathlib.Path,
                        help="The CSV-formatted input file to transform.")
    parser.add_argument("transformation", choices=[LOCK, AGE],
                        help="The type of transformation to perform.")
    
    args = parser.parse_args()    
    metadata = parse_metadata(args.input)

    transformation, results = lock(metadata)
    write_metadata(transformation, "transformation.csv")
    write_metadata(results, "results.csv")

if __name__ == '__main__':
    main()
