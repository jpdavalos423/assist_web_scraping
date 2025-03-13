#!/usr/bin/env python3

import os
import sys
import json
import csv

def load_articulations(json_path="results/articulations.json"):
    """
    Loads 'articulations.json' that your existing code produces.
    The data is typically a list of dicts like:
    [
      {
        "Receiving Courses": <OR/AND structure or 'Not Articulated'>,
        "Sending Courses": ...
      },
      ...
    ]
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def flatten_or_structure(course_data):
    """
    Takes the existing structure of 'Receiving Courses' or 'Sending Courses'
    and converts it into a list of OR blocks as strings.

    e.g.,
    - "Not Articulated" => ["Not Articulated"]
    - ["MATH 1A - Calculus", "MATH 1B - Calculus"] => single OR block => ["MATH 1A - Calculus; MATH 1B - Calculus"]
    - [ ["CIS 22A"], ["CIS 22B", "CIS 22C"] ] => => 2 OR blocks => 
         ["CIS 22A", "CIS 22B - Programming; CIS 22C - Programming"]

    We join AND sets with "; ".
    We produce one string per OR block.
    """
    if course_data == "Not Articulated":
        return ["Not Articulated"]
    if not course_data:
        return []

    # If it's a single list => AND
    # If it's a list of lists => OR
    # We'll check the first element
    if isinstance(course_data, list):
        if not course_data:
            return []
        first = course_data[0]
        # If first is itself a list => OR structure
        if isinstance(first, list):
            # e.g. [ ["CIS 22A"], ["CIS 22B", "CIS 22C"] ]
            blocks = []
            for or_block in course_data:
                # or_block is an AND group => join with "; "
                blocks.append("; ".join(or_block))
            return blocks
        else:
            # e.g. ["MATH 1A", "MATH 1B"] => single AND => one OR block
            return ["; ".join(course_data)]

    # If we somehow have a string or something else, just return it
    return [str(course_data)]

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_process_columns.py '<UC Name>' [optional_output_csv_path]")
        sys.exit(1)

    uc_name = sys.argv[1]  # The UC name to store in the CSV's first column
    output_csv = "results/final_articulations.csv"
    if len(sys.argv) >= 3:
        output_csv = sys.argv[2]

    # 1) Load the articulation data from your existing code's JSON
    articulations = load_articulations("results/articulations.json")

    # We'll parse each articulation to see how many OR blocks exist for receiving & sending
    # so we can figure out how many columns we need in total.
    max_receiving = 0
    max_sending = 0

    # We'll store an intermediate structure: list of (receivingBlocks, sendingBlocks)
    parsed_data = []

    for art in articulations:
        receiving_data = art.get("Receiving Courses", [])
        sending_data = art.get("Sending Courses", [])

        # Flatten them into lists of strings (OR blocks)
        receiving_blocks = flatten_or_structure(receiving_data)
        sending_blocks = flatten_or_structure(sending_data)

        max_receiving = max(max_receiving, len(receiving_blocks))
        max_sending = max(max_sending, len(sending_blocks))

        parsed_data.append((receiving_blocks, sending_blocks))

    # 2) Build columns => "UC Name", "Receiving #1", "Receiving #2", ..., "Sending #1", "Sending #2", ...
    # We'll produce:
    #   col_names = ["UC Name"] + ["Receiving #i" for i in range(1, max_receiving+1)] 
    #                               + ["Sending #j" for j in range(1, max_sending+1)]

    col_names = ["UC Name"]
    for i in range(1, max_receiving + 1):
        col_names.append(f"Receiving #{i}")
    for j in range(1, max_sending + 1):
        col_names.append(f"Sending #{j}")

    # 3) For each articulation, produce one row with that many columns
    all_rows = []
    for (receiving_blocks, sending_blocks) in parsed_data:
        row = [uc_name]  # first cell is UC Name
        # receiving
        for i in range(max_receiving):
            val = receiving_blocks[i] if i < len(receiving_blocks) else ""
            row.append(val)
        # sending
        for j in range(max_sending):
            val = sending_blocks[j] if j < len(sending_blocks) else ""
            row.append(val)

        all_rows.append(row)

    # 4) Write it out
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(all_rows)

    print(f"✅ Created {output_csv} with {len(all_rows)} rows.")
    print(f"Columns: {', '.join(col_names)}")

if __name__ == "__main__":
    main()
