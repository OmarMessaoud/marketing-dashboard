import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Marketing Dashboard", page_icon="📊", layout="wide")

st.title("📊 Marketing Analytics Dashboard")
st.markdown("*Track CTR, CPC, ROI, and Profit*")
st.markdown("---")

with st.sidebar:
    st.header("📁 Data Source")
    
    @st.cache_data
    def load_data():
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        channels = ['Google Ads', 'Facebook Ads', 'LinkedIn Ads']
        targeting = ['Demographic', 'Behavioral', 'Geographic']
        data = []
        for date in dates[:100]:
            for channel in channels:
                impressions = np.random.randint(1000, 50000)
                clicks = int(impressions * np.random.uniform(0.01, 0.05))
                conversions = int(clicks * np.random.uniform(0.05, 0.15))
                spend = np.random.uniform(100, 2000)
                data.append({
                    'Date': date, 'Channel': channel, 'Targeting': np.random.choice(targeting),
                    'Impressions': impressions, 'Clicks': clicks, 
                    'Conversions': conversions, 'Spend': spend
                })
        df = pd.DataFrame(data)
        df['CTR'] = (df['Clicks'] / df['Impressions'] * 100).round(2)
        df['CPC'] = (df['Spend'] / df['Clicks']).round(2)
        df['Conversion_Rate'] = (df['Conversions'] / df['Clicks'] * 100).round(2)
        df['ROI'] = ((df['Conversions'] * 50) / df['Spend']).round(2)
        return df
    
    data_option = st.radio("Choose:", ["Use Sample Data", "Upload CSV"])
    
    if data_option == "Use Sample Data":
        df = load_data()
        st.success("Sample data ready!")
    else:
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            df.columns = df.columns.str.lower()
            df['CTR'] = (df['clicks'] / df['impressions'] * 100).round(2)
            df['CPC'] = (df['spend'] / df['clicks']).round(2)
            df['Conversion_Rate'] = (df['conversions'] / df['clicks'] * 100).round(2)
            df['ROI'] = ((df['conversions'] * 50) / df['spend']).round(2)
            st.success(f"Loaded {len(df)} records!")
        else:
            st.info("Upload a CSV file")
            st.stop()
    
    st.markdown("---")
    channels = st.multiselect("Select Channels", df['Channel'].unique(), default=df['Channel'].unique()[:2])
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        date_range = st.date_input("Date Range", [df['Date'].min(), df['Date'].max()])
        filtered = df[(df['Channel'].isin(channels)) & (df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))]
    else:
        filtered = df[df['Channel'].isin(channels)]

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("CTR", f"{filtered['CTR'].mean():.2f}%")
with col2: st.metric("CPC", f"${filtered['CPC'].mean():.2f}")
with col3: st.metric("Conversion Rate", f"{filtered['Conversion_Rate'].mean():.2f}%")
with col4: st.metric("ROI", f"{filtered['ROI'].mean():.2f}x")

st.markdown("---")
st.subheader("CTR Trend")
if 'Date' in filtered.columns:
    fig1 = px.line(filtered.groupby('Date')['CTR'].mean().reset_index(), x='Date', y='CTR', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

st.subheader("Performance by Channel")
fig2 = px.bar(x=filtered.groupby('Channel')['ROI'].mean().sort_values(), y=filtered.groupby('Channel')['ROI'].mean().sort_values().index, orientation='h')
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Spend vs ROI")
fig3 = px.scatter(filtered, x='Spend', y='ROI', color='Channel')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.dataframe(filtered)
csv = filtered.to_csv(index=False)
st.download_button("📥 Download Data", csv, f"data_{datetime.now().strftime('%Y%m%d')}.csv")
