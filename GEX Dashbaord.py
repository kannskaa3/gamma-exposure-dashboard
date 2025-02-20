import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Streamlit App Title
st.title("📊 0DTE Gamma Exposure Dashboard")
st.sidebar.header("🔎 Select Your Ticker")

ticker = st.sidebar.text_input("Enter Ticker (e.g., SPY, QQQ)", "SPY")

# Fetch Gamma Data Function
def fetch_gamma_data(ticker):
    """Fetch gamma exposure data from Unusual Whales API"""
    api_key = st.secrets["api_keys"]["unusual_whales"]
    api_url = f"https://api.unusualwhales.com/v1/options/gamma/{ticker}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Failed to retrieve data.")
        return None

# Fetch Data
data = fetch_gamma_data(ticker)

if data is not None:
    # Display DataFrame
    st.write("### Gamma Exposure Data", data)

    # Plot Gamma Exposure Chart
    fig = px.line(data, x='strike_price', y='gamma_exposure',
                  title=f"Gamma Exposure for {ticker}",
                  labels={'gamma_exposure': 'Gamma Exposure', 'strike_price': 'Strike Price'})
    fig.add_hline(y=0, line_dash='dash', annotation_text='Zero Gamma Level', annotation_position='bottom right')
    st.plotly_chart(fig)

    # Key Trading Insights
    gamma_flip = data[data['gamma_exposure'] < 0]['strike_price'].min()
    high_gamma = data[data['gamma_exposure'] > data['gamma_exposure'].quantile(0.95)]['strike_price'].min()

    st.write(f"📍 **Gamma Flip Level:** {gamma_flip}")
    st.write(f"📍 **High Gamma Resistance:** {high_gamma}")

    # Trade Signals
    st.subheader("🔔 Trade Signals")
    current_price = st.sidebar.number_input("Enter Current Price", min_value=0.0, format="%.2f")

    if current_price < gamma_flip:
        st.warning("⚠️ Market in negative gamma zone! Expect higher volatility. Consider breakout trades.")
    elif current_price > high_gamma:
        st.success("✅ Market is pinned by high gamma. Mean reversion trades are favorable.")
    else:
        st.info("📊 Market is stable. Monitor for potential shifts.")
else:
    st.error("No data available for the selected ticker.")
