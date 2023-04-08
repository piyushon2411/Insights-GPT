import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from selenium.common.exceptions import NoSuchElementException

def _get_button_xpath_attributes(button):
    attributes = []
    for key, value in button.attrs.items():
        if isinstance(value, list):
            value = " ".join(value)
        value = value.replace("'", "\\'")
        attributes.append(f"@{key}='{value}'")
    return "[" + " and ".join(attributes) + "]"

def get_buttons_from_url(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    buttons = soup.find_all(["button", "input"])

    button_locations = []
    for button in buttons:
        button_xpath = '//' + button.name + _get_button_xpath_attributes(button)
        try:
            selenium_button = driver.find_element(By.XPATH, button_xpath)
            location = driver.execute_script("return arguments[0].getBoundingClientRect().top;", selenium_button)
            button_locations.append((button, location))
        except NoSuchElementException:
            pass

    driver.quit()
    return button_locations

url = "https://www.example.com"
button_locations = get_buttons_from_url(url)
for button, location in button_locations:
    print(button, location)




def is_valid_button(button):
    exclude_texts = ['cancel', 'close']
    button_text = button.text.strip().lower() if button.name == 'button' else button.get('value', '').strip().lower()

    if not button_text or len(button_text) < 2 or button_text in exclude_texts:
        return False

    parent_elements = ['modal', 'popup', 'dialog']
    for parent in parent_elements:
        if button.find_parents(attrs={'class': lambda x: x and parent in x.lower()}):
            return False

    return True


def extract_button_text(button_locations):
    button_texts = []

    # Loop through the button_locations and check if the button is valid
    for button, location in button_locations:
        if is_valid_button(button):
            button_text = button.text.strip() if button.name == 'button' else button.get('value', '').strip()
            button_texts.append((button_text, location))

    return button_texts


def save_button_texts_to_csv(domain, button_texts):
    file_name = f"CTA Names and Locations for {domain}.csv"

    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["CTA Names", "Location from Top (px)"])

        # Save both the button text and location in the CSV file
        for text, location in button_texts:
            csv_writer.writerow([text, location])

    print(f"CTA names and locations saved to '{file_name}'")


if __name__ == "__main__":
    url = input("Enter the URL: ")
    button_locations = get_buttons_from_url(url)
    button_texts = extract_button_text(button_locations)

    domain = urlparse(url).netloc
    save_button_texts_to_csv(domain, button_texts)
