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
    city = st.selectbox("Select City", ["Delhi", "London", "New York", "Beijing", "Tokyo"])
    
    # PM2.5 Data from your research[cite: 1]
    data = {
        "Year": [2018, 2019, 2020, 2022],
        "London": [14.5, 13.1, 9.2, 10.4],
        "Delhi": [115.0, 108.4, 95.2, 98.6],
        "New York": [12.1, 11.2, 8.4, 9.1],
        "Beijing": [90.0, 85.2, 62.1, 70.3],
        "Tokyo": [13.2, 12.4, 10.1, 11.2]
    }
    df = pd.DataFrame(data)
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