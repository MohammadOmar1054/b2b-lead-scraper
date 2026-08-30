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

MAX_COMPANIES = 30
MAX_PEOPLE_PER_COMPANY = 2


# ============================================================
# API HELPER
# ============================================================

def prospeo_request(endpoint, payload):

    url = f"{BASE_URL}/{endpoint}"

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


# ============================================================
# SEARCH COMPANIES
# ============================================================

def search_companies():

    print("\nSearching for Indian companies...\n")

    payload = {
        "page": 1,

        "filters": {
            "company_location_search": {
                "include": ["India"]
            }
        }
    }

    result = prospeo_request(
        "search-company",
        payload
    )

    if not result:
        return []

    companies = []

    for item in result.get("results", []):

        company = item.get("company", {})

        companies.append({
            "company_id": company.get("company_id"),
            "company_name": company.get("name"),
            "website": company.get("website"),
            "domain": company.get("domain"),
            "description": company.get("description"),

            "city": (
                company.get("location") or {}
            ).get("city"),

            "state": (
                company.get("location") or {}
            ).get("state"),

            "country": (
                company.get("location") or {}
            ).get("country"),
        })

    return companies[:MAX_COMPANIES]

# ============================================================
# SEARCH PEOPLE
# ============================================================

def search_people(company_id):

    payload = {
        "page": 1,

        "filters": {

            "company": {
                "company_oids": {
                    "include": [company_id]
                }
            },

            "person_job_title": {
                "include": [
                    "owner",
                    "founder",
                    "director",
                    "manager"
                ],

                "match_mode": "SMART"
            },

            "max_person_per_company": MAX_PEOPLE_PER_COMPANY
        }
    }

    result = prospeo_request(
        "search-person",
        payload
    )

    if not result:
        return []

    return result.get("results", [])


# ============================================================
# EXTRACT RECORD
# ============================================================

def create_record(person_result, company):

    person = person_result.get(
        "person",
        {}
    )

    person_location = (
        person.get("location") or {}
    )

    record = {

        "Business Name":
            company.get("company_name"),

        "Contact Person":
            person.get("full_name"),

        "Job Title":
            person.get("job_title"),

        "Phone":
            "",

        "Email":
            "",

        "Address":
            "",

        "City":
            person_location.get("city")
            or company.get("city"),

        "State":
            person_location.get("state")
            or company.get("state"),

        "Country":
            person_location.get("country")
            or company.get("country"),

        "Website":
            company.get("website"),

        "Domain":
            company.get("domain"),

        "Source":
            "Prospeo API"
    }

    return record


# ============================================================
# SAVE EXCEL
# ============================================================

def save_excel(records):

    if not records:
        print("\nNo records found.")
        return

    df = pd.DataFrame(records)

    # Remove completely duplicated records
    df = df.drop_duplicates(
        subset=[
            "Business Name",
            "Contact Person"
        ]
    )

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

    print("\n================================")
    print("SCRAPING COMPLETE")
    print("================================")

    print(
        f"Records exported: {len(df)}"
    )

    print(
        f"Excel file: {output_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("================================")
    print("INDIA TRAVEL AGENT DATABASE")
    print("================================")

    companies = search_companies()

    print(
        f"\nCompanies found: {len(companies)}"
    )

    records = []

    for index, company in enumerate(
        companies,
        start=1
    ):

        print(
            f"\n[{index}/{len(companies)}] "
            f"{company['company_name']}"
        )

        company_id = company.get(
            "company_id"
        )

        if not company_id:
            continue

        people = search_people(
            company_id
        )

        print(
            f"People found: {len(people)}"
        )

        for person in people:

            record = create_record(
                person,
                company
            )

            records.append(record)

        # Avoid hammering the API.
        time.sleep(1)


    save_excel(records)


if __name__ == "__main__":
    main()