# Data Filtering & FMCSA Lead Extraction Tool

## Overview
This project includes two main tools:
1. **Safer Web.py** – A lead extraction tool that scrapes carrier data from the **FMCSA Safer Company** database.
2. **Filter.py** – A GUI-based application that filters extracted data for better insights.

## Features
### **1. Safer Web.py (FMCSA Lead Extraction Tool)**
- Extracts **carrier leads** from the **FMCSA Safer Company database**.
- Captures important details such as:
  - MC Number
  - Entity Type (Carrier/Broker)
  - USDOT Number
  - Legal Name
  - MCS-150 Form Date
  - Operation Classification
  - Cargo Carried
  - Phone Number
  - Email Address
  - Business Address
- Saves extracted leads into a CSV file for easy access.

### **2. Filter.py (CSV Data Filter Tool)**
- Loads a CSV file via a **user-friendly GUI**.
- Removes:
  - Rows where **any field contains "Not Found"**.
  - The **Address** column (since it is not needed for lead generation).
- Filters data based on:
  - **Cargo Carried**:
    - Includes only companies that handle:
      - **General Freight**
      - **Mobile Homes**
      - **Oilfield Equipment**
      - **Passengers**
      - **Garbage/Refuse**
  - **MCS-150 Form Date**:
    - Allows filtering data based on a **date range**.
- Saves the **filtered leads** into a new CSV file.

## Installation
### Prerequisites
- Python 3.x
- Google Chrome (for Selenium)
- Chrome WebDriver (automatically managed by WebDriver Manager)

### Install Dependencies
Run the following command to install all required Python packages:
```sh
pip install -r requirements.txt
