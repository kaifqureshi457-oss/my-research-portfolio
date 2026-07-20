import streamlit as st
import joblib
import pandas as pd
import requests

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

# ---------- Helper: live air quality lookup (free, no API key needed) ----------
def get_live_aqi(city_name):
    """Looks up a city's coordinates, then fetches current PM2.5, NO2, and
    European AQI from Open-Meteo's free air quality API."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1},
            timeout=10
        ).json()
        if not geo.get("results"):
            return None
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        matched_name = geo["results"][0]["name"]
        country = geo["results"][0].get("country", "")

        air = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "pm2_5,nitrogen_dioxide,european_aqi"
            },
            timeout=10
        ).json()
        current = air.get("current", {})
        current["matched_name"] = matched_name
        current["country"] = country
        return current
    except Exception:
        return None


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

    # NO2 chart -- only appears if the column has data for this city
    if "NO2" in city_df.columns and city_df["NO2"].notna().any():
        st.write(f"### NO2 Trends for {city}, {country}")
        st.line_chart(city_df.set_index("Year")["NO2"])
    else:
        st.caption("No NO2 measurements available for this city in the dataset.")

    with st.expander("Compare multiple cities"):
        compare_cities = st.multiselect("Select cities to compare", options=sorted(df["City"].unique()))
        if compare_cities:
            compare_df = df[df["City"].isin(compare_cities)]
            pivoted = compare_df.pivot_table(index="Year", columns="City", values="PM2.5")
            st.line_chart(pivoted)

    st.divider()
    st.write("### Live AQI Right Now")
    st.caption("Pick any city in the world -- this pulls a real-time reading, not historical data.")
    live_city = st.text_input("Enter a city name for a live reading", value=city)
    if st.button("Get Live AQI"):
        live = get_live_aqi(live_city)
        if live:
            st.success(f"Showing live data for {live.get('matched_name')}, {live.get('country')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Live PM2.5 (μg/m³)", live.get("pm2_5"))
            c2.metric("Live NO2 (μg/m³)", live.get("nitrogen_dioxide"))
            c3.metric("Live European AQI", live.get("european_aqi"))
        else:
            st.error("Couldn't find that city -- try a nearby major city name instead.")

    st.caption(
        "Air quality data sources: primary research dataset (2018-2022, expanded coverage) "
        "and World Health Organization, WHO Ambient Air Quality Database (2024 update, V6.1). "
        "WHO data licensed under CC BY-NC-SA 3.0 IGO. Live readings powered by Open-Meteo "
        "(open-meteo.com), a free, no-key-required weather and air quality API."
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

    st.divider()
    st.subheader("Or check live pollutant levels for a real city")
    live_city2 = st.text_input("City name", value="Delhi", key="tab4_city")
    if st.button("Fetch live levels", key="tab4_fetch"):
        live2 = get_live_aqi(live_city2)
        if live2:
            st.success(f"Live data for {live2.get('matched_name')}, {live2.get('country')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("PM2.5 (μg/m³)", live2.get("pm2_5"))
            c2.metric("NO2 (μg/m³)", live2.get("nitrogen_dioxide"))
            c3.metric("European AQI", live2.get("european_aqi"))
        else:
            st.error("City not found -- try a nearby major city name.")
