import requests
import streamlit as st
from bs4 import BeautifulSoup

# Define the URL of the website you want to scrape
url = 'https://webbook.nist.gov/chemistry/fluid/'

# Send a GET request to the URL
response = requests.get(url)

chem_dict = {}
# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the <select> tag by its ID or class name, or any other identifying attribute
    select_tag = soup.find('select', id="ID")
    
    # Check if the <select> tag was found
    if select_tag:
        # Find all <option> tags within the <select> tag
        options = select_tag.find_all('option')
        
        # Extract and print the text content of each <option> tag
        for option in options:
            chem_dict[option['value']] = option.text  # Corrected line: store option value and text in dictionary
    else:
        print('Select tag not found on the webpage.')
else:
    print('Failed to retrieve the webpage.')

print(chem_dict)