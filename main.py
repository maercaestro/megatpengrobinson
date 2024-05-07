import requests
import numpy as np
import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
from PIL import Image

# Define fetch_chemical_data function to retrieve chemical data from the website
def fetch_chemical_data(selected_chem_value):
    # Define the URL of the website you want to scrape
    url = 'https://webbook.nist.gov/chemistry/fluid/'

    # Send a GET request to the URL
    response = requests.get(url)

    data = []  # List to store tuples of option value and text

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
        
            # Extract and store the option value and text in the data list
            for option in options:
                data.append((option['value'], option.text))
        else:
            st.error('Select tag not found on the webpage.')
    else:
        st.error('Failed to retrieve the webpage.')

    # Convert the list of tuples into a DataFrame
    df = pd.DataFrame(data, columns=['Value', 'Text'])

    return df

# Define calculate_acentric_factor function to calculate acentric factor using Joback method
def calculate_acentric_factor(MW, Tb, Tc, Pc, Vc):
    """
    Calculate the acentric factor using the Joback method.
    
    Parameters:
        MW (float): Molecular weight of the substance.
        Tb (float): Boiling point temperature (in K).
        Tc (float): Critical temperature (in K).
        Pc (float): Critical pressure (in bar).
        Vc (float): Critical molar volume (in cm^3/mol).
    
    Returns:
        float: Acentric factor (ω).
    """
    # Calculate reduced temperature and reduced pressure
    Tr = Tb / Tc
    Pr = Pc / 1e5 / (8.314 * Tc / Pc) / Vc
    
    # Calculate acentric factor using the Joback method
    omega = 1 + (1 - Tr)**(2/7) * (0.480 + 1.574 * Tr + 0.176 * Tr**2) / Pr**0.5
    
    return omega

# Define peng_robinson function to calculate molar volume using Peng-Robinson equation of state
def peng_robinson(T, P, Tc, Pc, omega):
    """
    Calculate molar volume using Peng-Robinson equation of state.
    
    Args:
        T (float): Temperature in Kelvin
        P (float): Pressure in bar
        Tc (float): Critical temperature in Kelvin
        Pc (float): Critical pressure in bar
        omega (float): Acentric factor
        
    Returns:
        v (float): Molar volume in cubic meters per mole
    """
    Tr = T / Tc
    Pr = P / Pc
    
    # Calculate parameters a and b
    a = 0.45724 * R**2 * Tc**2 / Pc
    b = 0.07780 * R * Tc / Pc
    
    # Calculate correction factor alpha
    alpha = (1 + (0.37464 + 1.54226 * omega - 0.26992 * omega**2) * (1 - (T / Tc)**0.5))**2
    
    # Solve cubic equation for molar volume
    A = a * alpha * P / (R**2 * T**2)
    B = b * P / (R * T)
    
    # Calculate coefficients for cubic equation
    coefficients = [1, -(1 - B), (A - 2*B - 3*B**2), -(A*B - B**2 - B**3)]
    
    try:
        # Find roots of the polynomial equation
        roots = np.roots(coefficients)
        
        # Select the real root
        v = np.real(roots[np.isreal(roots)])[0]
        
        return v
    except ValueError as e:
        st.error(f"Error finding roots: {e}")
        return None

# Constants
R = 8.314  # Universal gas constant in J/(mol*K)

# Scraping NIST for chemical data
url = 'https://webbook.nist.gov/chemistry/fluid/'

# Send a GET request
response = requests.get(url)

# Check request status
if response.status_code == 200:
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find select tag
    select_tag = soup.find('select', id="ID")
    
    # Check select tag
    if select_tag:
        # Find select options
        options = select_tag.find_all('option')
        
        # Extract text
        chem_data = [(option['value'], option.text) for option in options]
        
        # Create DataFrame
        chem_df = pd.DataFrame(chem_data, columns=['Value', 'Text'])
    
    else:
        st.error('Select tag not found on the webpage.')
else:
    st.error('Failed to retrieve the webpage.')

# Prepare image
image = Image.open('MEGATLogo.png')
# Define scale factor
scale_factor = 0.25  

# Calculate new dimensions based on scale factor
new_width = int(image.width * scale_factor)
new_height = int(image.height * scale_factor)

# Resize image
resized_image = image.resize((new_width, new_height))

# Prepare page layout for Streamlit

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Chemical Data", "Peng-Robinson"])

# Chemical Data Page
if page == "Chemical Data":
    st.image(resized_image)
    st.title("MEGAT Chemical Data Retrieval")
    # Dropdown to select a chemical
    selected_chem_text = st.selectbox("Select a chemical", list(chem_df['Text']))

    # Get the corresponding chemical value for the selected chemical text
    selected_chem_value = chem_df.loc[chem_df['Text'] == selected_chem_text, 'Value'].iloc[0]
    # Remove 'C'
    selected_chem_value = selected_chem_value[1:]

    # Button to trigger API call
    if st.button("Fetch Data"):
        df_chemical = fetch_chemical_data(selected_chem_value)
        if df_chemical is not None:
            st.write("Retrieved Data:")
            st.write(df_chemical)

# Peng-Robinson Page
elif page == "Peng-Robinson":
    st.image(resized_image)
    st.title("Peng-Robinson Equation of State")
    st.write("This page allows you to calculate the molar volume using the Peng-Robinson equation of state.")
    # Input fields for pressure and temperature
    pressure = st.number_input("Enter Pressure (bar)", min_value=0.0)
    temperature = st.number_input("Enter Temperature (K)", min_value=0.0)

    # Dropdown to select a chemical
    selected_chem_text = st.selectbox("Select a chemical", list(chem_df['Text']))

    # Get the corresponding chemical value for the selected chemical text
    selected_chem_value = chem_df.loc[chem_df['Text'] == selected_chem_text, 'Value'].iloc[0]
    # Remove 'C'
    selected_chem_value = selected_chem_value[1:]

    if st.button("Calculate Molar Volume"):

        # Call API
        df_chemical = fetch_chemical_data(selected_chem_value)

        if df_chemical is not None and temperature is not None and pressure is not None:
            # Check if required columns are present in the DataFrame
            required_columns = ['temperature_critical.value', 'temperature_boil.value', 'molecular_weight', 'pressure_critical.value', 'volume_critical.value']
            if all(col in df_chemical.columns for col in required_columns):
                # Extract data from DataFrame
                Tc = df_chemical['temperature_critical.value'].iloc[0]
                Tb = df_chemical['temperature_boil.value'].iloc[0]
                MW = df_chemical['molecular_weight'].iloc[0]
                Pc = df_chemical['pressure_critical.value'].iloc[0]
                Vc = df_chemical['volume_critical.value'].iloc[0]
                T = temperature
                P = pressure

                # Calculate omega
                omega = calculate_acentric_factor(MW=MW, Tb=Tb, Tc=Tc, Pc=Pc, Vc=Vc)
                molvalue = peng_robinson(T=T, P=P, Tc=Tc, Pc=Pc, omega=omega)

                st.write(f"Molar volume is {molvalue}")
            else:
                st.error("One or more required columns are missing in the chemical data.")
        else:
            st.error("Not enough input.")
