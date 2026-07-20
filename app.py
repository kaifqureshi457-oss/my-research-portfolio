import streamlit as st
import joblib
import pandas as pd
import requests

# Load the model
model = joblib.load("aqi_model.pkl")

st.set_page_config(page_title="Kaif Qureshi Research", layout="wide")
st.title("Research Portfolio: Sustainable Policy & Carbon Finance")
st.subheader("Author: Kaif Qureshi")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Interactive Data Explorer",
    "Air Quality Research",
    "Carbon Credits Research",
    "AQI Forecast",
    "Solar & Carbon Analysis"
])

# ---------- Helper: geocode a city name to lat/lon (free, no key) ----------
def geocode_city(city_name):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1},
            timeout=10
        ).json()
        if not geo.get("results"):
            return None
        r = geo["results"][0]
        return {"lat": r["latitude"], "lon": r["longitude"],
                "name": r["name"], "country": r.get("country", "")}
    except Exception:
        return None


# ---------- Helper: live air quality lookup (free, no API key needed) ----------
def get_live_aqi(city_name):
    """Looks up a city's coordinates, then fetches current PM2.5, NO2, and
    US AQI (0-500 scale, close to India's CPCB AQI formula) from
    Open-Meteo's free air quality API."""
    loc = geocode_city(city_name)
    if not loc:
        return None
    try:
        air = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "current": "pm2_5,nitrogen_dioxide,us_aqi"
            },
            timeout=10
        ).json()
        current = air.get("current", {})
        current["matched_name"] = loc["name"]
        current["country"] = loc["country"]
        return current
    except Exception:
        return None


# ---------- Helper: solar PV generation estimate (free, no key -- PVGIS, EU JRC) ----------
def get_solar_estimate(lat, lon, peak_power_kw, system_loss_pct=14):
    """Calls the EU Joint Research Centre's PVGIS PVcalc tool to estimate
    annual solar PV energy generation for a grid-tied system at this location."""
    try:
        resp = requests.get(
            "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc",
            params={
                "lat": lat,
                "lon": lon,
                "peakpower": peak_power_kw,
                "loss": system_loss_pct,
                "outputformat": "json"
            },
            timeout=15
        ).json()
        totals = resp.get("outputs", {}).get("totals", {}).get("fixed", {})
        return totals  # contains E_y (kWh/year), E_d (kWh/day avg), etc.
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
    st.caption(
        "Pick any city in the world -- this pulls a real-time reading, not historical data. "
        "AQI shown uses the US EPA 0-500 scale, which India's CPCB AQI formula is closely modeled on."
    )
    live_city = st.text_input("Enter a city name for a live reading", value=city)
    if st.button("Get Live AQI"):
        live = get_live_aqi(live_city)
        if live:
            st.success(f"Showing live data for {live.get('matched_name')}, {live.get('country')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Live PM2.5 (μg/m³)", live.get("pm2_5"))
            c2.metric("Live NO2 (μg/m³)", live.get("nitrogen_dioxide"))
            c3.metric("Live US AQI", live.get("us_aqi"))
        else:
            st.error("Couldn't find that city -- try a nearby major city name instead.")

    with st.expander("Methodology & data sources"):
        st.markdown(
            "**Historical data (2018-2022):** compiled from a primary research dataset "
            "and the World Health Organization's Ambient Air Quality Database (2024 update, "
            "V6.1), which reports annual mean ground-station concentrations of PM2.5, PM10 and "
            "NO2 for over 7,000 human settlements. WHO updates this database roughly every "
            "2-3 years, so 2022 is the most recent verified annual figure available at time "
            "of writing. WHO data licensed under CC BY-NC-SA 3.0 IGO.\n\n"
            "**Live readings:** provided by Open-Meteo's Air Quality API, which uses the "
            "Copernicus Atmosphere Monitoring Service (CAMS) model rather than a single "
            "ground sensor. Estimates may differ from official national monitors (e.g. "
            "CPCB in India) due to differing methodology, station density, and averaging area; "
            "this is expected and does not indicate an error in either source."
        )


with tab2:
    st.header("Report: Urban Air Quality Transitions")
    with open("kaif_qureshi_report.pdf", "rb") as f:
        st.download_button("Download Air Quality Report", f, "kaif_qureshi_report.pdf")
    st.write("This research explores how governance capacity dictates air quality recovery.")
    with st.expander("Methodology & data sources"):
        st.markdown(
            "Findings are based on a comparative analysis of urban air quality governance "
            "across five global cities, drawing on publicly available regulatory records "
            "and ambient air quality monitoring data. Full methodology, city selection "
            "criteria, and limitations are detailed in the downloadable report above."
        )


with tab3:
    st.header("Report: Carbon Credits & Sustainability")
    with open("carbon_credits_report.pdf", "rb") as f:
        st.download_button("Download Carbon Credits Report", f, "carbon_credits_report.pdf")
    st.write("This study models how CCP-labelled carbon revenue makes rural microgrids viable.")
    with st.expander("Methodology & data sources"):
        st.markdown(
            "This research models the financial impact of Core Carbon Principles (CCP) "
            "labelled carbon credit revenue on the payback period of rural solar microgrid "
            "projects. The finding that CCP-labelled credits can reduce payback periods from "
            "approximately 8-10 years to 4-5 years is drawn from the author's own financial "
            "modelling in the linked SSRN paper -- see the calculator below for an interactive "
            "version of this analysis applied to a user-specified system."
        )


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
            c3.metric("US AQI", live2.get("us_aqi"))
        else:
            st.error("City not found -- try a nearby major city name.")

    with st.expander("Methodology & data sources"):
        st.markdown(
            "The predictor is a RandomForestRegressor trained on paired PM2.5, NO2, and AQI "
            "observations. It estimates AQI from pollutant concentrations you enter -- it does "
            "not fetch live data itself. Use the live lookup above for real-time readings."
        )


with tab5:
    st.header("Solar PV Potential & Carbon Credit Payback Calculator")
    st.write(
        "Combines a real solar generation estimate for any location with the payback-period "
        "impact of carbon credit financing, based on findings from the author's rural solar "
        "microgrid research."
    )

    st.subheader("1. Solar generation potential")
    solar_city = st.text_input("City or location", value="Lucknow", key="solar_city")
    peak_power = st.number_input(
        "System size (kWp, peak power)", min_value=1.0, max_value=1000.0, value=5.0, step=0.5
    )

    # Realistic India installed-cost range per kWp for grid-tied rooftop solar.
    # Used only to auto-suggest a starting system cost below -- always editable.
    COST_PER_KWP_LOW = 45000
    COST_PER_KWP_HIGH = 65000

    if st.button("Estimate solar generation"):
        loc = geocode_city(solar_city)
        if not loc:
            st.error("Couldn't find that location -- try a nearby major city name.")
        else:
            totals = get_solar_estimate(loc["lat"], loc["lon"], peak_power)
            if totals and "E_y" in totals:
                st.success(f"Estimate for {loc['name']}, {loc['country']} -- {peak_power} kWp system")
                c1, c2 = st.columns(2)
                c1.metric("Estimated annual generation", f"{totals['E_y']:.0f} kWh/year")
                c2.metric("Estimated daily average", f"{totals.get('E_d', 0):.1f} kWh/day")
                st.session_state["annual_kwh"] = totals["E_y"]
                # Auto-suggest a system cost tied to the actual system size entered,
                # using the midpoint of the realistic India ₹/kWp range.
                suggested_cost = peak_power * (COST_PER_KWP_LOW + COST_PER_KWP_HIGH) / 2
                st.session_state["suggested_cost"] = suggested_cost
                st.caption(
                    f"Typical installed cost in India for a {peak_power:.1f} kWp system: "
                    f"roughly ₹{peak_power * COST_PER_KWP_LOW:,.0f}–₹{peak_power * COST_PER_KWP_HIGH:,.0f} "
                    f"(₹45,000–65,000 per kWp). The field below is pre-filled with the midpoint -- "
                    f"replace it with a real installer quote if you have one."
                )
            else:
                st.error("Couldn't retrieve a solar estimate for this location right now.")

    st.divider()
    st.subheader("2. Payback period: with vs. without carbon credit financing")

    default_kwh = st.session_state.get("annual_kwh", 7000.0)
    default_cost = st.session_state.get("suggested_cost", peak_power * (COST_PER_KWP_LOW + COST_PER_KWP_HIGH) / 2)

    annual_generation = st.number_input(
        "Annual generation (kWh/year) -- auto-filled from above if calculated",
        min_value=0.0, value=float(default_kwh), step=100.0
    )
    system_cost = st.number_input(
        "Total system cost (₹) -- auto-suggested from system size above, edit if you have a real quote",
        min_value=1000.0, value=float(default_cost), step=5000.0
    )
    tariff = st.number_input("Avoided electricity cost (₹ per kWh)", min_value=0.1, value=7.0, step=0.5)

    if st.button("Calculate payback"):
        annual_savings = annual_generation * tariff
        if annual_savings <= 0:
            st.error("Annual savings must be greater than zero to calculate payback.")
        else:
            baseline_payback = system_cost / annual_savings
            # Range reflects the 8-10yr -> 4-5yr reduction documented in the author's
            # SSRN paper on CCP-labelled carbon credit financing for rural solar microgrids.
            improvement_factor_low, improvement_factor_high = 0.45, 0.55
            with_credits_low = baseline_payback * improvement_factor_low
            with_credits_high = baseline_payback * improvement_factor_high

            c1, c2 = st.columns(2)
            c1.metric("Payback without carbon credits", f"{baseline_payback:.1f} years")
            c2.metric(
                "Estimated payback with CCP-labelled credits",
                f"{with_credits_low:.1f}-{with_credits_high:.1f} years"
            )
            st.caption(
                "The 'with credits' range applies the proportional payback reduction "
                "(roughly 45-55% of baseline) documented in the author's research on rural "
                "solar microgrids financed with CCP-labelled carbon credits. This is a "
                "directional estimate scaled from that finding, not a project-specific quote -- "
                "actual results depend on credit price, verification costs, and buyer demand "
                "at time of sale."
            )

    with st.expander("Methodology & data sources"):
        st.markdown(
            "**Solar estimate:** generation figures come from PVGIS (Photovoltaic Geographical "
            "Information System), maintained by the European Commission's Joint Research "
            "Centre, using satellite-derived irradiance data for the entered coordinates. "
            "Assumes a fixed-mounted, grid-tied system with a default 14% system loss.\n\n"
            "**System cost estimate:** the auto-suggested cost uses a typical India grid-tied "
            "rooftop solar installed-cost range of ₹45,000-65,000 per kWp (panels, inverter, "
            "and installation), a general market range rather than a specific vendor quote. "
            "Always editable -- replace with a real quote when available.\n\n"
            "**Payback calculator:** baseline payback is a simple system-cost-over-annual-"
            "savings calculation using the inputs above. The carbon-credit-adjusted range is "
            "derived from the proportional reduction reported in the author's SSRN paper on "
            "CCP-labelled carbon credit financing for rural solar microgrids (payback reduced "
            "from roughly 8-10 years to 4-5 years in the cases studied), not a universal "
            "formula -- treat it as an illustrative, research-grounded estimate."
        )
