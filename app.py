import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# Set up the Streamlit page
st.set_page_config(page_title="PPP Salary Converter", page_icon="💱", layout="wide")

# Custom CSS to improve the app's appearance
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .output-text {
        font-size: 20px;
        font-weight: bold;
        color: #1E88E5;
    }
    .learn-more-button button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title and description
st.title("Purchasing Power Parity Salary Converter 💸")
st.markdown("Convert your salary from one currency to another using PPP")

@st.cache_data
def parse_xml(file_path):
    """Parses the XML file to extract the latest PPP factors and countries."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    ppp_factors = {}
    country_latest_ppp = {}

    # Iterate through each record in the XML file
    for record in root.findall(".//record"):
        country = record.find(".//field[@name='Country or Area']").text.strip()
        year = int(record.find(".//field[@name='Year']").text)
        value = record.find(".//field[@name='Value']").text

        # Only add if the value exists and track the latest year for each country
        if value:
            value = float(value)
            if country not in country_latest_ppp or year > country_latest_ppp[country]:
                country_latest_ppp[country] = year
                ppp_factors[country] = value

    return ppp_factors

@st.cache_data
def load_currency_codes(file_path):
    """Loads the currency codes from a CSV file."""
    df = pd.read_csv(file_path)

    # Normalize the country names to lowercase for case-insensitive matching
    df['Entity'] = df['Entity'].str.strip().str.lower()

    # Create a dictionary mapping lowercase country name to currency code
    currency_codes = dict(zip(df['Entity'], df['AlphabeticCode']))
    
    return currency_codes

# Load PPP factors and currency codes
ppp_factors = parse_xml('ppp_value.xml')
currency_codes = load_currency_codes('currencyCodes.csv')

# Function to convert salary using PPP
def convert_salary_ppp(salary, source_country, target_country):
    source_ppp = ppp_factors[source_country]
    target_ppp = ppp_factors[target_country]

    # Convert source salary to USD equivalent using PPP
    usd_equivalent = salary / source_ppp

    # Convert USD equivalent to target currency using PPP
    target_salary = usd_equivalent * target_ppp

    return target_salary

# Input fields
source_country = st.selectbox(
    "Select your Source Country",
    ["Select your country"] + list(ppp_factors.keys()),  # Add placeholder
)

# Check if a valid country is selected
if source_country != "Select your country":
    # Convert the selected country name to lowercase to match the CSV file's format
    source_country_lower = source_country.lower()

    # Fetch the corresponding currency code for the selected country in lowercase
    source_currency = currency_codes.get(source_country_lower, "Unknown")
else:
    source_currency = ""

salary = st.number_input(
    f"Salary in {source_country}'s Local Currency ({source_currency})",
    min_value=0.00,
    step=0.01,
    value=0.00 if source_country == "Select your country" else None,  # Empty by default
)

target_country = st.selectbox(
    "Select your Target Country",
    ["Select your country"] + list(ppp_factors.keys()),  # Add placeholder
)

# Check if a valid target country is selected
if target_country != "Select your country":
    # Convert the selected target country name to lowercase to match the CSV file's format
    target_country_lower = target_country.lower()

    # Fetch the corresponding currency code for the selected target country in lowercase
    target_currency = currency_codes.get(target_country_lower, "Unknown")
else:
    target_currency = ""

# Convert button
if st.button("Convert", key="convert_button") and source_country != "Select your country" and target_country != "Select your country" and salary > 0:
    converted_amount = convert_salary_ppp(salary, source_country, target_country)

    # Display results
    st.markdown("### Output:")
    st.markdown(
        f'<p class="output-text">You require a salary of {converted_amount:.2f} {target_currency} in {target_country} to live a similar quality of life as you would with a salary of {salary:.2f} {source_currency} in {source_country}.</p>',
        unsafe_allow_html=True,
    )

st.markdown("   ")
st.markdown("   ")
st.markdown("   ")

# Initialize session state for learn more button
if "learn_more" not in st.session_state:
    st.session_state["learn_more"] = False

# Learn More toggle button
if st.button(
    "Learn More", key="learn-more-button", help="Click to learn more about PPP"
):
    st.session_state["learn_more"] = not st.session_state["learn_more"]

# Toggle display of Learn More section
if st.session_state["learn_more"]:
    st.markdown(
    """
    The foreign exchange rate shows that 80,000 Euros can be converted into 100,000 US Dollars. However, it doesn't indicate whether 100,000 USD in the United States can provide the same lifestyle as 80,000 Euros does in France. To figure out how much you'd need in the U.S. to match the purchasing power in France, a different method is required.

    This is where [Purchasing Power Parity (PPP)](https://en.wikipedia.org/wiki/Purchasing_power_parity) comes in. Converting your salary using PPP, instead of the exchange rate, helps to give you a better approximation of what your standard of living would be like in two different countries. This can be handy to know if you're planning on moving, a remote worker, sending money abroad, or many other things.
    """
)

# Disclaimer
st.markdown("---")
st.caption(
    "Disclaimer: PPP conversion factors are based on World Bank data. This tool is for informational purposes only."
)

st.write("Made with ❤️ by [Jess John](https://jessjohn.tech)")
