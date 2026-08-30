# B2B Travel Agent Data Scraper

A Python-based data collection pipeline that uses the Prospeo API to identify travel-industry professionals in India and export structured business and contact data to an Excel file.

## Features

* Search people by job title
* Filter results by location and company industry
* Retrieve associated company information
* Optional contact enrichment
* Basic data cleaning and deduplication
* Excel export using Pandas and OpenPyXL

## Tech Stack

* Python 3.14+
* Requests
* Pandas
* OpenPyXL
* python-dotenv
* Prospeo API

## Project Structure

```text
b2b-lead-scraper/
├── main.py
├── .env
├── requirements.txt
└── output/
    └── travel_agents.xlsx
```

## Setup

Install dependencies:

```bash
pip install requests pandas openpyxl python-dotenv
```

Create a `.env` file:

```env
PROSPEO_API_KEY=your_api_key
```

Run the scraper:

```bash
python main.py
```

The generated dataset is saved to:

```text
output/travel_agents.xlsx
```

## Data Fields

The output may contain:

* Contact Person
* Job Title
* Business Name
* Phone
* Email
* Address
* City
* State
* Country
* Website
* Domain
* Person ID
* Company ID
* Source

Availability of individual fields depends on the data returned and permitted by the Prospeo API.

## Workflow

```text
Prospeo API
    |
    v
Person Search
    |
    v
Industry and Location Filtering
    |
    v
Company and Person Data
    |
    v
Data Cleaning
    |
    v
Deduplication
    |
    v
Excel Export
```

## Notes

The system is intended as a proof-of-concept for automated B2B data collection. API usage, enrichment, redistribution, and data export must comply with the Prospeo API terms and applicable data-protection requirements.