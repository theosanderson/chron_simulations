import argparse
import pandas as pd

def process_file(file_name):
    # Read the file using pandas
    df = pd.read_csv(file_name, sep="\t")

    # Calculate the total number of lines
    total_lines = df.shape[0]
    print(total_lines)

    # Convert date column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Add a column for the year and fractional part of the year
    df['year_fraction'] = df['date'].dt.year + (df['date'].dt.dayofyear - 1) / 365

    # Output the node and year fraction
    for index, row in df.iterrows():
        print(row['strain'], '\t', round(row['year_fraction'], 2))

# Define and parse command line arguments
parser = argparse.ArgumentParser(description='Process a file to count lines and calculate year fractions.')
parser.add_argument('file_name', type=str, help='Name of the file to process')

args = parser.parse_args()

# Call the function with your file name
process_file(args.file_name)
