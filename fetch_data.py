
"""
fetch_data.py - Week 8: get data from an API and save it as DATA/raw.csv.

Run it: python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests

# Settings

# The URL of the GitHub API that provides Python organisation repositories
URL = "https://api.github.com/orgs/python/repos"

# Ask the API to return up to 100 repositories
PARAMS = {"per_page": 100}

# The API returns a list directly, so no records key is needed
RECORDS_KEY = None

# Rename the original API column names to shorter, easier names
RENAME = {
    "stargazers_count": "stars",
    "forks_count": "forks",
    "open_issues_count": "open_issues"
}

# Select only the columns needed for the coursework
KEEP = [
    "name",
    "language",
    "stars",
    "forks",
    "open_issues"
]

# The repository name must be present in every record
MUST_HAVE = ["name"]

# Set the location where the downloaded CSV file will be saved
RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


# Functions

def get_data(url, params):
    """Ask the API for data and return the JSON reply."""
    try:
        # Send a request to the API and wait up to 15 seconds
        response = requests.get(url, params=params, timeout=15)

        # Check whether the API request was successful
        response.raise_for_status()

        # Convert the API response into Python data
        return response.json()

    except requests.RequestException as error:
        # Display an error message if the request fails
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the JSON reply into a pandas table."""

    # Get the records from the API response
    records = data[records_key] if records_key else data

    # Convert the records into a pandas DataFrame
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Rename, keep and clean the columns."""

    # Rename the columns using the RENAME dictionary
    df = df.rename(columns=RENAME)

    # Keep only the columns listed in KEEP
    df = df[KEEP]

    # Remove records that do not have a repository name
    df = df.dropna(subset=MUST_HAVE)

    return df


def save_data(df, path):
    """Save the table as a CSV file."""

    # Create the DATA folder if it does not already exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save the DataFrame as a CSV file without row numbers
    df.to_csv(path, index=False)

    # Display how many records were saved
    print(f"Saved {len(df)} rows to {path}")


# Run the program

if __name__ == "__main__":

    # Get the data from the GitHub API
    data = get_data(URL, PARAMS)

    # Continue only if the API request was successful
    if data is not None:

        # Convert the API data into a DataFrame
        table = make_table(data, RECORDS_KEY)

        # Clean the DataFrame
        table = tidy_data(table)

        # Display the first five rows
        print(table.head())

        # Save the cleaned data as raw.csv
        save_data(table, RAW_FILE)
