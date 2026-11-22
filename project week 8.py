
"""
fetch_data.py - Week 8: Get data from an API and save it as DATA/raw.csv.

Run it using: python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

# This is the web address of the GitHub API.
# It provides information about repositories owned by the Python organisation.
URL = "https://api.github.com/orgs/python/repos"

# This tells the API to return up to 100 repositories.
PARAMS = {"per_page": 100}

# The API returns a list of repositories directly.
# Therefore, we do not need to look for a records key.
RECORDS_KEY = None

# This dictionary changes the original API column name
# stargazers_count to the shorter name stars.
RENAME = {
    "stargazers_count": "stars"
}

# These are the five columns we want to keep in our final dataset.
KEEP = [
    "name",
    "language",
    "stars",
    "forks",
    "open_issues"
]

# This column is required.
# Records without a repository name will be removed.
MUST_HAVE = ["name"]

# This creates the file path where the CSV data will be saved.
# The file will be stored inside the DATA folder.
RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def get_data(url, params):
    """Get data from the GitHub API."""

    try:
        # Send a request to the API using the URL and parameters.
        # The timeout prevents the program from waiting forever.
        response = requests.get(url, params=params, timeout=15)

        # Check whether the request was successful.
        # If there is an error, Python will raise an exception.
        response.raise_for_status()

        # Convert the API response from JSON into Python data.
        return response.json()

    except requests.RequestException as error:
        # Display an error message if the request fails.
        print("Could not get the data:", error)

        # Return None to show that no data was received.
        return None


def make_table(data, records_key):
    """Convert the API data into a pandas DataFrame."""

    # If a records key exists, get the records using that key.
    # Otherwise, use the data directly because the API returns a list.
    records = data[records_key] if records_key else data

    # Convert the list of repository records into a DataFrame.
    # This allows us to organise and work with the data using pandas.
    df = pd.json_normalize(records, sep="_")

    # Return the DataFrame so another function can clean it.
    return df


def tidy_data(df):
    """Select and clean the required columns."""

    # Select only the five original columns needed from the API.
    # We use stargazers_count here because it is the original API name.
    df = df[
        [
            "name",
            "language",
            "stargazers_count",
            "forks",
            "open_issues"
        ]
    ]

    # Rename stargazers_count to stars using the RENAME dictionary.
    df = df.rename(columns=RENAME)

    # Keep only the five columns listed in KEEP.
    df = df[KEEP]

    # Remove records where the repository name is missing.
    df = df.dropna(subset=MUST_HAVE)

    # Return the cleaned DataFrame.
    return df


def save_data(df, path):
    """Save the cleaned DataFrame as a CSV file."""

    # Create the DATA folder if it does not already exist.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save the DataFrame as a CSV file.
    # index=False prevents pandas from adding row numbers.
    df.to_csv(path, index=False)

    # Display the number of records saved and the file location.
    print(f"Saved {len(df)} rows to {path}")


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

# This checks whether the file is being run directly.
if __name__ == "__main__":

    # Step 1: Get repository data from the GitHub API.
    data = get_data(URL, PARAMS)

    # Step 2: Continue only if the API returned data successfully.
    if data is not None:

        # Step 3: Convert the API data into a pandas DataFrame.
        table = make_table(data, RECORDS_KEY)

        # Step 4: Clean the DataFrame and keep the required columns.
        table = tidy_data(table)

        # Step 5: Display the first five rows of the cleaned data.
        print(table.head())

        # Step 6: Save the cleaned data into DATA/raw.csv.
        save_data(table, RAW_FILE)
