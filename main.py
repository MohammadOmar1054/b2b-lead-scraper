import os
import time
import requests
import pandas as pd

from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("PROSPEO_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "PROSPEO_API_KEY was not found in your .env file."
    )

BASE_URL = "https://api.prospeo.io"

HEADERS = {
    "X-KEY": API_KEY,
    "Content-Type": "application/json"
}

# Keep this LOW for the demonstration.
# Prospeo search returns max 25 results per page.
MAX_PAGES = 1

# Enrichment is a separate API operation/credit.
MAX_ENRICHMENTS = 25


# ============================================================
# API REQUEST
# ============================================================

def prospeo_request(endpoint, payload):

    url = f"{BASE_URL}/{endpoint}"

    try:

        response = requests.post(
            url,
            headers=HEADERS,
            json=payload,
            timeout=60
        )

        print(
            f"{endpoint}: HTTP {response.status_code}"
        )

        if response.status_code != 200:

            print(response.text)

            return None

        return response.json()

    except requests.RequestException as error:

        print(
            f"Request failed: {error}"
        )

        return None


# ============================================================
# SEARCH PEOPLE
# ============================================================

def search_people_by_title(page=1):

    print(
        f"\nSearching people - page {page}..."
    )

    payload = {

        "page": page,

        "filters": {

            "person_job_title": {

                "include": [

                    # "owner",
                    # "founder",
                    # "co-founder",
                    # "director",
                    "travel agent",
                    "travel consultant",
                    "travel manager"

                ],

                "match_mode": "CONTAINS"
            },

            "person_location_search": {

                "include": [
                    "India"
                ]
            }
        }
    }

    return prospeo_request(
        "search-person",
        payload
    )


# ============================================================
# ENRICH PERSON
# ============================================================

def enrich_person(person_id):

    payload = {
        "data": {
            "person_id": person_id
        }
    }

    return prospeo_request(
        "enrich-person",
        payload
    )


# ============================================================
# EXTRACT BASIC SEARCH DATA
# ============================================================

def extract_basic_record(search_result):

    person = search_result.get(
        "person",
        {}
    )

    company = search_result.get(
        "company",
        {}
    )

    person_location = (
        person.get("location")
        or {}
    )

    company_location = (
        company.get("location")
        or {}
    )

    return {

        "Person ID":
            person.get("person_id"),

        "Contact Person":
            person.get("full_name"),

        "Job Title":
            person.get("current_job_title")
            or person.get("job_title"),

        "Business Name":
            company.get("name"),

        "Phone":
            "",

        "Email":
            "",

        "Address":
            company_location.get("raw_address")
            or "",

        "City":
            person_location.get("city")
            or company_location.get("city")
            or "",

        "State":
            person_location.get("state")
            or company_location.get("state")
            or "",

        "Country":
            person_location.get("country")
            or company_location.get("country")
            or "",

        "Website":
            company.get("website")
            or "",

        "Domain":
            company.get("domain")
            or "",

        "LinkedIn":
            person.get("linkedin_url")
            or "",

        "Source":
            "Prospeo API"
    }


# ============================================================
# ADD ENRICHED DATA
# ============================================================

def add_enrichment(record, enrichment_result):

    if not enrichment_result:
        return record

    person = enrichment_result.get(
        "person",
        {}
    )

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    email_data = person.get(
        "email"
    )

    if isinstance(email_data, dict):

        record["Email"] = (
            email_data.get("email")
            or email_data.get("value")
            or ""
        )

    elif isinstance(email_data, str):

        record["Email"] = email_data


    # --------------------------------------------------------
    # MOBILE
    # --------------------------------------------------------

    mobile_data = person.get(
        "mobile"
    )

    if isinstance(mobile_data, dict):

        record["Phone"] = (
            mobile_data.get("mobile")
            or mobile_data.get("phone")
            or mobile_data.get("value")
            or ""
        )

    elif isinstance(mobile_data, str):

        record["Phone"] = mobile_data


    # --------------------------------------------------------
    # FALLBACK PHONE FIELDS
    # --------------------------------------------------------

    if not record["Phone"]:

        record["Phone"] = (
            person.get("phone")
            or person.get("mobile_number")
            or ""
        )


    # --------------------------------------------------------
    # LINKEDIN
    # --------------------------------------------------------

    if not record["LinkedIn"]:

        record["LinkedIn"] = (
            person.get("linkedin_url")
            or ""
        )


    return record


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(records):

    if not records:

        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Remove duplicate people
    if "Person ID" in df.columns:

        df = df.drop_duplicates(
            subset=["Person ID"]
        )

    else:

        df = df.drop_duplicates(
            subset=[
                "Contact Person",
                "Business Name"
            ]
        )

    # Clean whitespace
    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# SAVE EXCEL
# ============================================================

def save_excel(df):

    if df.empty:

        print(
            "\nNo records to save."
        )

        return

    os.makedirs(
        "output",
        exist_ok=True
    )

    output_file = (
        "output/travel_agents.xlsx"
    )

    df.to_excel(
        output_file,
        index=False
    )

    print(
        "\n========================================"
    )

    print(
        "EXCEL EXPORT COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"Records exported: {len(df)}"
    )

    print(
        f"File: {output_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "INDIA TRAVEL AGENT DATABASE"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    all_records = []

    for page in range(
        1,
        MAX_PAGES + 1
    ):

        result = search_people_by_title(
            page
        )

        if not result:

            print(
                "\nSearch failed."
            )

            return


        results = result.get(
            "results",
            []
        )

        print(
            f"Search returned "
            f"{len(results)} people."
        )


        # ----------------------------------------------------
        # PROCESS SEARCH RESULTS
        # ----------------------------------------------------

        for result_item in results:

            record = extract_basic_record(
                result_item
            )

            person_id = record.get(
                "Person ID"
            )

            print(
                f"\nFound: "
                f"{record['Contact Person']}"
            )

            print(
                f"Company: "
                f"{record['Business Name']}"
            )

            print(
                f"Title: "
                f"{record['Job Title']}"
            )


            # ------------------------------------------------
            # ENRICH
            # ------------------------------------------------

            if person_id:

                print(
                    "Enriching contact..."
                )

                enrichment = enrich_person(
                    person_id
                )

                record = add_enrichment(
                    record,
                    enrichment
                )

                print(
                    f"Email: "
                    f"{record['Email'] or 'N/A'}"
                )

                print(
                    f"Phone: "
                    f"{record['Phone'] or 'N/A'}"
                )

                # Don't hammer the API.
                time.sleep(1)


            all_records.append(
                record
            )


    # --------------------------------------------------------
    # CLEAN
    # --------------------------------------------------------

    print(
        "\nCleaning data..."
    )

    df = clean_data(
        all_records
    )


    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    save_excel(
        df
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()