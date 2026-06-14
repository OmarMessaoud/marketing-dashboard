import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Customer Marketing Dashboard", page_icon="📊", layout="wide")

st.title("📊 Customer Marketing Analytics Dashboard")
st.markdown("*Analyze customer demographics, purchase behavior & campaign response*")
st.markdown("---")

with st.sidebar:
    st.header("📁 Data Source")
    
    @st.cache_data
    def load_data():
        # Try to load the uploaded or existing CSV
        import os
        if os.path.exists('marketing_data.csv'):
            df = pd.read_csv('marketing_data.csv')
        else:
            # Create sample if no file
            st.warning("Using sample data. Please upload your CSV.")
            return create_sample_data()
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Calculate derived metrics
        if 'Income' in df.columns:
            df['Income'] = pd.to_numeric(df['Income'], errors='coerce')
        
        # Calculate total spending
        spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']
        existing_spend = [col for col in spend_cols if col in df.columns]
        if existing_spend:
            df['Total_Spending'] = df[existing_spend].sum(axis=1)
        
        # Calculate total purchases
        purchase_cols = ['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases']
        existing_purchases = [col for col in purchase_cols if col in df.columns]
        if existing_purchases:
            df['Total_Purchases'] = df[existing_purchases].sum(axis=1)
        
        # Calculate age
        if 'Year_Birth' in df.columns:
            current_year = datetime.now().year
            df['Age'] = current_year - df['Year_Birth']
            df['Age_Group'] = pd.cut(df['Age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        
        # Campaign response (1 if responded to any campaign)
        campaign_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'Response']
        existing_campaigns = [col for col in campaign_cols if col in df.columns]
        if existing_campaigns:
            df['Responded_Any'] = df[existing_campaigns].sum(axis=1) > 0
        
        return df
    
    def create_sample_data():
        """Fallback sample data"""
        np.random.seed(42)
        n = 500
        data = {
            'Income': np.random.normal(50000, 20000, n),
            'Age': np.random.normal(45, 15, n),
            'Total_Spending': np.random.normal(1000, 500, n),
            'NumWebPurchases': np.random.poisson(3, n),
            'NumStorePurchases': np.random.poisson(4, n),
            'Response': np.random.choice([0,1], n, p=[0.85, 0.15])
        }
        return pd.DataFrame(data)
    
    # Data loading
    data_option = st.radio("Choose data source:", ["Upload CSV", "Use Sample Data"])
    
    if data_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload marketing_data.csv", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} customer records!")
        else:
            st.info("👆 Please upload your CSV file")
            st.stop()
    else:
        df = load_data()
        st.success("Sample data loaded")
    
    st.markdown("---")
    st.header("🔍 Filters")
    
    # Demographic filters
    if 'Education' in df.columns:
        education = st.multiselect("Education Level:", df['Education'].unique(), default=df['Education'].unique()[:3])
    else:
        education = []
    
    if 'Marital_Status' in df.columns:
        marital = st.multiselect("Marital Status:", df['Marital_Status'].unique(), default=df['Marital_Status'].unique()[:3])
    else:
        marital = []
    
    if 'Country' in df.columns:
        country = st.multiselect("Country:", df['Country'].unique(), default=df['Country'].unique()[:3])
    else:
        country = []
    
    # Income filter
    if 'Income' in df.columns:
        min_income = float(df['Income'].min())
        max_income = float(df['Income'].max())
        income_range = st.slider("Income Range ($):", min_income, max_income, (min_income, max_income))
    else:
        income_range = (0, 100000)
    
    # Apply filters
    filtered_df = df.copy()
    if education:
        filtered_df = filtered_df[filtered_df['Education'].isin(education)]
    if marital:
        filtered_df = filtered_df[filtered_df['Marital_Status'].isin(marital)]
    if country:
        filtered_df = filtered_df[filtered_df['Country'].isin(country)]
    if 'Income' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Income'] >= income_range[0]) & (filtered_df['Income'] <= income_range[1])]

# Main dashboard
st.header("📈 Key Customer Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_income = filtered_df['Income'].mean() if 'Income' in filtered_df.columns else 0
    st.metric("Average Income", f"${avg_income:,.0f}")

with col2:
    if 'Total_Spending' in filtered_df.columns:
        avg_spend = filtered_df['Total_Spending'].mean()
        st.metric("Average Total Spend", f"${avg_spend:,.0f}")
    else:
        st.metric("Average Total Spend", "N/A")

with col3:
    if 'Responded_Any' in filtered_df.columns:
        response_rate = filtered_df['Responded_Any'].mean() * 100
        st.metric("Campaign Response Rate", f"{response_rate:.1f}%")
    elif 'Response' in filtered_df.columns:
        response_rate = filtered_df['Response'].mean() * 100
        st.metric("Last Campaign Response", f"{response_rate:.1f}%")
    else:
        st.metric("Response Rate", "N/A")

with col4:
    if 'Age' in filtered_df.columns:
        avg_age = filtered_df['Age'].mean()
        st.metric("Average Age", f"{avg_age:.0f} years")

st.markdown("---")

# Charts Section
st.header("📊 Customer Analytics")

# Row 1: Demographics
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    if 'Education' in filtered_df.columns and 'Income' in filtered_df.columns:
        edu_income = filtered_df.groupby('Education')['Income'].mean().sort_values(ascending=False).reset_index()
        fig1 = px.bar(edu_income, x='Education', y='Income', title='Average Income by Education',
                      color='Education', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    if 'Marital_Status' in filtered_df.columns and 'Total_Spending' in filtered_df.columns:
        marital_spend = filtered_df.groupby('Marital_Status')['Total_Spending'].mean().sort_values(ascending=False).reset_index()
        fig2 = px.bar(marital_spend, x='Marital_Status', y='Total_Spending', title='Average Spending by Marital Status',
                      color='Marital_Status', color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

# Row 2: Spending breakdown
st.subheader("💰 Purchase Category Breakdown")

# Get spending columns
spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']
existing_spend_cols = [col for col in spend_cols if col in filtered_df.columns]

if existing_spend_cols:
    spend_avg = filtered_df[existing_spend_cols].mean().reset_index()
    spend_avg.columns = ['Category', 'Average Amount']
    
    fig3 = px.bar(spend_avg, x='Category', y='Average Amount', 
                  title='Average Spending by Product Category',
                  color='Category', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig3, use_container_width=True)

# Row 3: Purchase behavior
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    purchase_cols = ['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases']
    existing_purchase_cols = [col for col in purchase_cols if col in filtered_df.columns]
    
    if existing_purchase_cols:
        purchase_avg = filtered_df[existing_purchase_cols].mean().reset_index()
        purchase_avg.columns = ['Channel', 'Average Purchases']
        
        fig4 = px.pie(purchase_avg, values='Average Purchases', names='Channel',
                      title='Purchase Channel Distribution',
                      color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig4, use_container_width=True)

with col_chart4:
    if 'Age_Group' in filtered_df.columns and 'Total_Spending' in filtered_df.columns:
        age_spend = filtered_df.groupby('Age_Group')['Total_Spending'].mean().reset_index()
        fig5 = px.line(age_spend, x='Age_Group', y='Total_Spending', 
                       title='Spending by Age Group', markers=True)
        st.plotly_chart(fig5, use_container_width=True)

# Row 4: Campaign analysis
if 'Responded_Any' in filtered_df.columns or 'Response' in filtered_df.columns:
    st.subheader("🎯 Campaign Response Analysis")
    
    col_camp1, col_camp2 = st.columns(2)
    
    with col_camp1:
        if 'Income' in filtered_df.columns:
            response_col = 'Responded_Any' if 'Responded_Any' in filtered_df.columns else 'Response'
            income_by_response = filtered_df.groupby(response_col)['Income'].mean().reset_index()
            income_by_response[response_col] = income_by_response[response_col].map({0: 'No Response', 1: 'Responded'})
            
            fig6 = px.bar(income_by_response, x=response_col, y='Income', 
                          title='Income Comparison: Responders vs Non-Responders',
                          color=response_col, color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
            st.plotly_chart(fig6, use_container_width=True)
    
    with col_camp2:
        if existing_spend_cols:
            response_col = 'Responded_Any' if 'Responded_Any' in filtered_df.columns else 'Response'
            spend_by_response = filtered_df.groupby(response_col)['Total_Spending'].mean().reset_index()
            spend_by_response[response_col] = spend_by_response[response_col].map({0: 'No Response', 1: 'Responded'})
            
            fig7 = px.bar(spend_by_response, x=response_col, y='Total_Spending',
                          title='Spending Comparison: Responders vs Non-Responders',
                          color=response_col, color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
            st.plotly_chart(fig7, use_container_width=True)

# Row 5: Correlation heatmap
numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) > 1:
    st.subheader("🔗 Correlation Analysis")
    
    # Limit to first 8 numeric columns for readability
    corr_cols = numeric_cols[:8]
    corr_matrix = filtered_df[corr_cols].corr()
    
    fig8 = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                     title="Feature Correlations",
                     color_continuous_scale='RdBu_r')
    st.plotly_chart(fig8, use_container_width=True)

# Data Export
st.markdown("---")
st.header("💾 Export Data")

col_export1, col_export2 = st.columns(2)

with col_export1:
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Filtered Data (CSV)", csv,
                      f"customer_data_{datetime.now().strftime('%Y%m%d')}.csv",
                      mime="text/csv")

with col_export2:
    if st.button("📊 Generate Summary Statistics"):
        st.subheader("Summary Statistics")
        st.dataframe(filtered_df.describe(), use_container_width=True)

# Raw data view
with st.expander("🔍 View Raw Customer Data"):
    st.dataframe(filtered_df, use_container_width=True, height=400)

st.markdown("---")
st.markdown("📌 **Insights Tip:** Use filters to segment customers by demographics. Hover over charts for details.")
