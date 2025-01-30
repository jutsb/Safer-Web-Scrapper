from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup

# Ask for MC number range
start_mc = int(input("Enter starting MC number: "))
end_mc = int(input("Enter ending MC number: "))

# Start WebDriver
driver = webdriver.Chrome()

# FMCSA URLs
snapshot_url = "https://safer.fmcsa.dot.gov/CompanySnapshot.aspx"
overview_url_template = "https://ai.fmcsa.dot.gov/SMS/Carrier/{}/CarrierRegistration.aspx"

# Output file
output_file = (f"{start_mc} to {end_mc}.csv")

# List to store extracted data
data = []

# Iterate through MC numbers
for mc_number in range(start_mc, end_mc + 1):
    print(f"🔍 Searching MC Number: {mc_number}...")

    try:
        # Open FMCSA Company Snapshot
        driver.get(snapshot_url)
        wait = WebDriverWait(driver, 10)

        # Click the "MC Number" radio button
        mc_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='MC_MX']")))
        driver.execute_script("arguments[0].click();", mc_radio)

        # Find the MC input field and enter the MC number
        mc_input = wait.until(EC.visibility_of_element_located((By.NAME, "query_string")))
        mc_input.clear()
        mc_input.send_keys(str(mc_number))
        mc_input.send_keys(Keys.RETURN)

        # Wait for the results page to load
        time.sleep(3)

        # Parse the results page
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract Entity Type
        entity_type_element = soup.find("a", href="saferhelp.aspx#EntityType")
        entity_type = entity_type_element.find_next("td").text.strip() if entity_type_element else "Not Found"

        # Extract USDOT Number
        usdot_element = soup.find("a", class_="querylabel", href="saferhelp.aspx#USDOTID")
        usdot_number = usdot_element.find_next("td").text.strip() if usdot_element else "Not Found"

        # Extract Legal Name
        name_element = soup.find(text="Legal Name:")
        legal_name = name_element.find_next().text.strip() if name_element else "Not Found"

        # Extract MCS-150 Form Date
        mcs_date_element = soup.find(text="MCS-150 Form Date:")
        mcs_date = mcs_date_element.find_next().text.strip() if mcs_date_element else "Not Found"

        # Extract Operation Classification (Only items with "X")
        op_class = []
        op_class_section = soup.find("table", summary="Operation Classification")
        if op_class_section:
            rows = op_class_section.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 1 and cells[0].text.strip() == "X":
                    op_class.append(cells[1].text.strip())
        op_class = ", ".join(op_class) if op_class else "Not Found"

        # Extract Cargo Carried (Only items with "X")
        cargo_carried = []
        cargo_section = soup.find("table", summary="Cargo Carried")
        if cargo_section:
            rows = cargo_section.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) > 1 and cells[0].text.strip() == "X":
                    cargo_carried.append(cells[1].text.strip())
        cargo_carried = ", ".join(cargo_carried) if cargo_carried else "Not Found"

        print(f"✅ Found: {legal_name}, USDOT: {usdot_number}")

        # Open Carrier Registration Page for additional details
        if usdot_number != "Not Found":
            overview_url = overview_url_template.format(usdot_number)
            driver.get(overview_url)

            # Wait for the page to load
            time.sleep(3)

            # Parse overview page
            overview_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Extract Phone Number
            phone = "Not Found"
            phone_element = overview_soup.find("span", class_="dat", text=lambda x: x and "-" in x)
            if phone_element:
                phone = phone_element.text.strip()

            # Extract Email Address
            email = "Not Found"
            email_element = overview_soup.find("span", class_="dat", text=lambda x: x and "@" in x)
            if email_element:
                email = email_element.text.strip()

            # Extract Address
            address = "Not Found"
            address_label = overview_soup.find("label", text="Address:")
            if address_label:
                address = address_label.find_next("span", class_="dat").text.strip()

            print(f"📞 Phone: {phone}, 📧 Email: {email}, 📍 Address: {address}")
        else:
            phone = email = address = "Not Found"

        # Store the data
        data.append([mc_number, entity_type, usdot_number, legal_name, mcs_date, op_class, cargo_carried, phone, email, address])

    except Exception as e:
        print(f"⚠️ Error processing MC {mc_number}: {e}")

# Save to CSV
df = pd.DataFrame(data, columns=["MC Number", "Entity Type", "USDOT Number", "Legal Name", "MCS-150 Form Date",
                                 "Operation Classification", "Cargo Carried", "Phone", "Email", "Address"])
df.to_csv(output_file, index=False)
print(f"✅ Data saved to {output_file}")

# Close WebDriver
driver.quit()
