import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Function to format numbers into WhatsApp format
def format_number(number):
    if len(number) == 10:  # Ensure it's a 10-digit number
        return f"+91 {number[:5]} {number[5:]}"
    return number

# Load the Excel file
df = pd.read_excel(r"C:\Users\gurse\Documents\phones_to_accept.xlsx")  # Path to your Excel file

# Drop duplicates and convert numbers to formatted set
numbers_to_accept = set(format_number(str(num)) for num in df['Phone'].drop_duplicates().tolist())

# Path to your ChromeDriver
driver_path = r"C:\Users\gurse\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # Full path to the executable

# Check if the ChromeDriver file exists
if not os.path.isfile(driver_path):
    raise FileNotFoundError(f"ChromeDriver executable not found at {driver_path}")

# Function to get all phone number elements from the page
def get_all_phone_number_elements(driver):
    try:
        # Retrieve all potential phone number elements
        phone_number_elements = driver.find_elements(By.XPATH, '//span[contains(@class, "x1iyjqo2") and contains(@class, "x1n2onr6")]')
        return phone_number_elements
    except Exception as e:
        print(f"Error retrieving phone number elements: {e}")
        return []

# Function to accept the request for a specific phone number
def accept_request_for_phone_number(driver, phone_number_element, numbers_to_accept):
    try:
        phone_number = phone_number_element.text.strip()
        if phone_number in numbers_to_accept:
            print(f"Accepting request for {phone_number}...")
            
            # Locate the accept button relative to the phone number element
            parent_div = phone_number_element.find_element(By.XPATH, './ancestor::div[5]')
            accept_button_xpath = './/div[@role="button" and @aria-label="Approve"]'
            accept_button = parent_div.find_element(By.XPATH, accept_button_xpath)
            accept_button.click()
            print(f"Accepted request for {phone_number}")
            time.sleep(1)  # Adjust sleep time if necessary
        else:
            print(f"{phone_number} is not in the list. Skipping.")
    except Exception as e:
        print(f"Could not accept request for {phone_number}: {e}")

# Main function to process invites
def process_invites(driver, numbers_to_accept):
    already_tried = set()
    while True:
        try:
            phone_number_elements = get_all_phone_number_elements(driver)
            if not phone_number_elements:
                print("No phone number elements found.")
                break
            
            for phone_number_element in phone_number_elements:
                phone_number = phone_number_element.text.strip()
                if phone_number in already_tried:
                    print(f"Already tried for {phone_number}. Skipping.")
                    continue
                
                accept_request_for_phone_number(driver, phone_number_element, numbers_to_accept)
                already_tried.add(phone_number)

            # Ask if the user wants to reprocess a new group
            if input("Do you want to process another group? (Press Enter to continue or type 'exit' to stop): ").lower() == 'exit':
                break
        except Exception as e:
            print(f"Error during processing: {e}")
            break

# Initialize the ChromeDriver with the Service class
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service)

# Open WhatsApp Web
driver.get('https://web.whatsapp.com')
input("Scan the QR code to log in to WhatsApp and press Enter")

# Main loop for rerunning the script
while True:
    print("Manually navigate to the accepting page and press Enter when ready.")
    input("Press Enter to continue...")

    # Process invites
    process_invites(driver, numbers_to_accept)
    
    # Ask if the user wants to start the process again for a new group
    if input("Do you want to start over for another group? (Press Enter to restart or type 'exit' to stop): ").lower() == 'exit':
        break

# Close the browser once done
driver.quit()
