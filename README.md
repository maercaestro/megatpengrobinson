# MEGAT Peng Robinson Demonstration

![MEGAT Logo](MEGATLogo.png)

This repository demonstrates the application of the Peng-Robinson equation of state for calculating molar volume and provides chemical data retrieval functionalities using Streamlit.

## Introduction
The Peng-Robinson equation of state is a widely used thermodynamic model for describing the behavior of pure fluids and mixtures. It provides a relationship between pressure, temperature, and molar volume, offering insights into the phase behavior of substances.

## Acentric Factor Calculation
The acentric factor $(\omega\)$ is a dimensionless quantity used in thermodynamics to characterize the non-ideality of a fluid. It is calculated using the Joback method, which involves the critical properties of the substance. The formula for calculating the acentric factor is as follows:

$\omega = 1 + \left( 1 - \frac{T_b}{T_c} \right)^{\frac{2}{7}} \left(0.480 + 1.574 \frac{T_b}{T_c} + 0.176 \left( \frac{T_b}{T_c} \right)^2 \right) \left( \frac{P_c}{P} \right)^{0.5} \$

## Peng-Robinson Equation of State
The Peng-Robinson equation of state predicts the molar volume of a substance at given pressure and temperature conditions. It considers the critical properties of the substance, such as critical temperature $(\(T_c\))$, critical pressure $(\(P_c\))$, and acentric factor $(\(\omega\))$. The equation is as follows:

$\ P = \frac{R T}{v - b} - \frac{a}{v(v + b) + b(v - b)} \$

Where:
- $P$ is the pressure (bar)
- $T$ is the temperature (K)
- $v$ is the molar volume (m³/mol)
- $R$ is the universal gas constant (J/(mol·K))
- $a$  and  $b$ are parameters derived from critical properties and acentric factor

## Usage
The Streamlit application provided in this repository allows users to:
1. Retrieve chemical data from the National Institute of Standards and Technology (NIST) database.
2. Perform Peng-Robinson calculations to determine the molar volume of a substance at specified pressure and temperature conditions.

## Code Overview
The repository contains the following main components:
- **Data Retrieval:** Utilizes the NIST API to fetch chemical data based on the selected chemical compound.
- **Acentric Factor Calculation:** Implements the Joback method to calculate the acentric factor of a substance.
- **Peng-Robinson Calculation:** Implements the Peng-Robinson equation of state to determine the molar volume of a substance.
- **Streamlit Application:** Provides a user-friendly interface for chemical data retrieval and Peng-Robinson calculations.

## Dependencies
- requests
- numpy
- streamlit
- pandas
- beautifulsoup4
- pillow

## Instructions
1. Clone the repository to your local machine.
2. Install the dependencies listed in the `requirements.txt` file.
3. Run the Streamlit application using the command `streamlit run main.py`.
4. Navigate through the sidebar to access the desired functionality.

## Contributors
- Abu Huzaifah Bidin

## License
This project is licensed under the [MIT License](LICENSE).
