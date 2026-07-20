import streamlit as st
import joblib
import pandas as pd

# Load the model
model = joblib.load("aqi_model.pkl")

st.set_page_config(page_title="Kaif Qureshi Research", layout="wide")
st.title("Research Portfolio: Sustainable Policy & Carbon Finance")
st.subheader("Author: Kaif Qureshi")

tab1, tab2, tab3, tab4 = st.tabs([
    "Interactive Data Explorer",
    "Air Quality Research",
    "Carbon Credits Research",
    "AQI Forecast"
])

with tab1:
    st.header("Global Air Quality & Carbon Data")

    df = pd.read_csv("data.csv")

    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("Select Country", options=sorted(df["Country"].unique()))
    with col2:
        city_options = sorted(df.loc[df["Country"] == country, "City"].unique())
        city = st.selectbox("Select City", options=city_options)

    city_df = df[df["City"] == city].sort_values("Year")

    st.write(f"### PM2.5 Trends for {city}, {country}")
    st.line_chart(city_df.set_index("Year")["PM2.5"])

    with st.expander("Compare multiple cities"):
        compare_cities = st.multiselect("Select cities to compare", options=sorted(df["City"].unique()))
        if compare_cities:
            compare_df = df[df["City"].isin(compare_cities)]
            pivoted = compare_df.pivot_table(index="Year", columns="City", values="PM2.5")
            st.line_chart(pivoted)

    st.caption(
        "Air quality data source: World Health Organization, "
        "WHO Ambient Air Quality Database (2024 update, V6.1). "
        "Licensed under CC BY-NC-SA 3.0 IGO."
    )

with tab2:
    st.header("Report: Urban Air Quality Transitions")
    with open("kaif_qureshi_report.pdf", "rb") as f:
        st.download_button("Download Air Quality Report", f, "kaif_qureshi_report.pdf")
    st.write("This research explores how governance capacity dictates air quality recovery.")

with tab3:
    st.header("Report: Carbon Credits & Sustainability")
    with open("carbon_credits_report.pdf", "rb") as f:
        st.download_button("Download Carbon Credits Report", f, "carbon_credits_report.pdf")
    st.write("This study models how CCP-labelled carbon revenue makes rural microgrids viable.")

with tab4:
    st.header("AQI Predictor")
    st.write("Estimate Air Quality Index from pollutant concentrations using a trained Random Forest model.")

    col1, col2 = st.columns(2)
    with col1:
        pm25_input = st.slider("PM2.5 (μg/m³)", 0.0, 300.0, 25.0, step=0.5)
    with col2:
        no2_input = st.slider("NO2 (μg/m³)", 0.0, 200.0, 20.0, step=0.5)

    predicted_aqi = model.predict([[pm25_input, no2_input]])[0]

    st.metric("Predicted AQI", f"{predicted_aqi:.0f}")

    if predicted_aqi <= 50:
        st.success("Good")
    elif predicted_aqi <= 100:
        st.warning("Moderate")
    elif predicted_aqi <= 150:
        st.warning("Unhealthy for Sensitive Groups")
    else:
        st.error("Unhealthy")

    st.caption("Model: RandomForestRegressor trained on PM2.5 + NO2 → AQI")
