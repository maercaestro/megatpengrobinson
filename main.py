import requests
import numpy as np
import streamlit as st
import pandas as pd
import re
from bs4 import BeautifulSoup
from PIL import Image


#define semua function kat sini dulu
#function untuk call API

def fetch_chemical_data(selected_chem_value):
    api_url = f'https://nist-api.fly.dev/crawl.json?spider_name=webbook_nist&start_requests=true&crawl_args={{"search_by":"cas", "cas":"{selected_chem_value}"}}'
    response = requests.get(api_url)
    if response.status_code == 200:
        json_data = response.json()
        df_chemical = pd.json_normalize(json_data['items'])
        return df_chemical
    else:
        st.error("Failed to retrieve data from the API. Please try again later.")

#function peng robinson
#sebab takde accentric factor (omega), kena kira pakai critical temperature and pressure

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

#baru carik peng-robinson
# Constants
R = 8.314  # Universal gas constant in J/(mol*K)

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
      

#scrap nist untuk semua list chemical
url = 'https://webbook.nist.gov/chemistry/fluid/'

# hantar GET request
response = requests.get(url)

# tengok request status
if response.status_code == 200:
    # parse
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # carik select tag
    select_tag = soup.find('select', id="ID")
    
    # cek select tag
    if select_tag:
        # cari select options
        options = select_tag.find_all('option')
        
        # extract text
        chem_data = [(option['value'], option.text) for option in options]
        
        # create df
        chem_df = pd.DataFrame(chem_data, columns=['Value', 'Text'])
    
    else:
        st.error('Select tag not found on the webpage.')
else:
    st.error('Failed to retrieve the webpage.')

#prepare image siap2
image=Image.open('MEGATLogo.png')
# Define the scale factor
scale_factor = 0.25  

# Calculate the new dimensions based on the scale factor
new_width = int(image.width * scale_factor)
new_height = int(image.height * scale_factor)

# Resize the image
resized_image = image.resize((new_width, new_height))

#prepare page layouT untuk streamlit

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Chemical Data", "Peng-Robinson"])

# page 1, Chemical Data Page
if page == "Chemical Data":

    st.image(resized_image)
    st.title("MEGAT Chemical Data Retrieval")
    # Dropdown to select a chemical
    selected_chem_text = st.selectbox("Select a chemical", list(chem_df['Text']))

    # Get the corresponding chemical value for the selected chemical text
    selected_chem_value = chem_df.loc[chem_df['Text'] == selected_chem_text, 'Value'].iloc[0]
    # buang C
    selected_chem_value = selected_chem_value[1:]

    # Button to trigger API call
    if st.button("Fetch Data"):
        df_chemical = fetch_chemical_data(selected_chem_value)
        if df_chemical is not None:
            st.write("Retrieved Data:")
            st.write(df_chemical)

# page 2, Peng-Robinson 
elif page == "Peng-Robinson":
    st.image(resized_image)
    st.title("Peng-Robinson Equation of State")
    st.write("This page allows you to calculate the mole value using the Peng-Robinson equation of state.")
    # Add input fields for pressure and temperature
    pressure = st.number_input("Enter Pressure (bar)", min_value=0.0)
    temperature = st.number_input("Enter Temperature (K)", min_value=0.0)

    # Dropdown to select a chemical
    selected_chem_text = st.selectbox("Select a chemical", list(chem_df['Text']))

    # Get the corresponding chemical value for the selected chemical text
    selected_chem_value = chem_df.loc[chem_df['Text'] == selected_chem_text, 'Value'].iloc[0]
    # buang C
    selected_chem_value = selected_chem_value[1:]

    

    if st.button("Calculate Mole Value"):

        # call API first
        df_chemical = fetch_chemical_data(selected_chem_value)

        if df_chemical is not None and temperature is not None and pressure is not None:
            # Check if the required columns are present in the DataFrame
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

                st.write(f"Mole value is {molvalue}")
            else:
                st.error("One or more required columns are missing in the chemical data.")
        else:
            st.error("Not enough input.")






