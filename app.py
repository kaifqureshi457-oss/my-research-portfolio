import streamlit as st
import joblib
import pandas as pd

# Load the model
model = joblib.load("aqi_model.pkl")

st.set_page_config(page_title="Kaif Qureshi Research", layout="wide")
st.title("Research Portfolio: Sustainable Policy & Carbon Finance")
st.subheader("Author: Kaif Qureshi")

tab1, tab2, tab3 = st.tabs(["Interactive Data Explorer", "Air Quality Research", "Carbon Credits Research"])

with tab1:
    st.header("Global Air Quality & Carbon Data")
    
    # Load data from the CSV file
    df = pd.read_csv("data.csv")
    
    # Automatically get the list of city names from the columns
    city_options = [col for col in df.columns if col != "Year"]
    
    # --- ADD THIS LINE ---
    city = st.selectbox("Select City", options=city_options)
    
    # Now it knows what 'city' is!
    st.write(f"### PM2.5 Trends for {city}")
    st.line_chart(df.set_index("Year")[city])

with tab2:
    st.header("Report: Urban Air Quality Transitions")
    with open("kaif_qureshi_report.pdf", "rb") as f:
        st.download_button("Download Air Quality Report", f, "kaif_qureshi_report.pdf")
    st.write("This research explores how governance capacity dictates air quality recovery[cite: 1].")

with tab3:
    st.header("Report: Carbon Credits & Sustainability")
    with open("carbon_credits_report.pdf", "rb") as f:
        st.download_button("Download Carbon Credits Report", f, "carbon_credits_report.pdf")
    st.write("This study models how CCP-labelled carbon revenue makes rural microgrids viable[cite: 2].")