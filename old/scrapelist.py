import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

# Initialize Selenium WebDriver
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Existing brand scraping code
url = "https://www.sizecharter.com/brands/"
headers = {"User-Agent": "Mozilla/5.0..."}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
brand_urls = ["https://www.sizecharter.com" + a['href'] 
             for a in soup.find('ul', id='list').find_all('a')]

# New code for tab navigation and CSV saving
for brand_url in brand_urls:
    try:
        driver.get(brand_url)
        brand_name = driver.find_element(By.TAG_NAME, 'h1').text.strip().replace('/', '-')
        
        # Create CSV structure
        csv_file = f"{brand_name}_size_chart.csv"
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Gender', 'Size', 'Measurement', 'Chest', 'Waist', 'Hip'])

            # Check for gender tabs
            for gender in ['Men', 'Women']:
                try:
                    tab = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, gender))
                    )
                    tab.click()
                    time.sleep(1)  # Allow chart to load

                    # Extract size table data
                    table = driver.find_element(By.CSS_SELECTOR, 'table.size-chart')
                    rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = [cell.text for cell in row.find_elements(By.TAG_NAME, 'td')]
                        writer.writerow([gender] + cells)

                except Exception as e:
                    print(f"No {gender} sizes found for {brand_name}")
                    continue

        print(f"Saved: {csv_file}")

    except Exception as e:
        print(f"Failed to process {brand_url}: {str(e)}")

driver.quit()
