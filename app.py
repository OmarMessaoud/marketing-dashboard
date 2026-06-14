"""
Maven Marketing Customer Analytics Dashboard
Analyzes customer profiles, campaign performance, and purchase behavior
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Maven Marketing Analytics",
    page_icon="📊",
    layout="wide"
)

# Load the fixed dataset
@st.cache_data
def load_data():
    """Load the Maven Marketing customer data"""
    df = pd.read_csv('marketing_data.csv')
    
    # Clean column names (remove spaces)
    df.columns = df.columns.str.strip()
    
    # Convert date column
    if 'Dt_Customer' in df.columns:
        df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'])
    
    # Handle missing values in Income
    if 'Income' in df.columns:
        df['Income'] = pd.to_numeric(df['Income'], errors='coerce')
        # Fill missing Income with median
        df['Income'].fillna(df['Income'].median(), inplace=True)
    
    # Calculate derived metrics
    # Total spending across all products
    spend_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 
                  'MntFishProducts', 'MntSweetProducts', 'MntGoldProds']
    df['Total_Spending'] = df[spend_cols].sum(axis=1)
    
    # Total purchases across channels
    purchase_cols = ['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases']
    df['Total_Purchases'] = df[purchase_cols].sum(axis=1)
    
    # Age calculation
    current_year = datetime.now().year
    df['Age'] = current_year - df['Year_Birth']
    df['Age_Group'] = pd.cut(df['Age'], bins=[0, 30, 40, 50, 60, 100], 
                              labels=['<30', '30-39', '40-49', '50-59', '60+'])
    
    # Campaign response (accepted any campaign)
    campaign_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 
                     'AcceptedCmp4', 'AcceptedCmp5']
    df['Accepted_Any_Campaign'] = df[campaign_cols].sum(axis=1) > 0
    
    # Children in home
    df['Total_Children'] = df['Kidhome'] + df['Teenhome']
    
    return df

# Load data
df = load_data()

# Sidebar filters
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000001/marketing.png", width=80)
    st.markdown("# Maven Marketing")
    st.markdown("### Customer Analytics Dashboard")
    st.markdown("---")
    
    # Filters
    st.markdown("## 🔍 Filters")
    
    # Education filter
    if 'Education' in df.columns:
        education_options = ['All'] + sorted(df['Education'].dropna().unique().tolist())
        selected_education = st.selectbox("Education Level:", education_options)
    
    # Marital status filter
    if 'Marital_Status' in df.columns:
        marital_options = ['All'] + sorted(df['Marital_Status'].dropna().unique().tolist())
        selected_marital = st.selectbox("Marital Status:", marital_options)
    
    # Country filter
    if 'Country' in df.columns:
        country_options = ['All'] + sorted(df['Country'].dropna().unique().tolist())
        selected_country = st.selectbox("Country:", country_options)
    
    # Age group filter
    age_groups = ['All', '<30', '30-39', '40-49', '50-59', '60+']
    selected_age_group = st.selectbox("Age Group:", age_groups)
    
    st.markdown("---")
    st.caption(f"Total Customers: {len(df):,}")

# Apply filters
filtered_df = df.copy()
if selected_education != 'All':
    filtered_df = filtered_df[filtered_df['Education'] == selected_education]
if selected_marital != 'All':
    filtered_df = filtered_df[filtered_df['Marital_Status'] == selected_marital]
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]
if selected_age_group != 'All':
    filtered_df = filtered_df[filtered_df['Age_Group'] == selected_age_group]

# Main Dashboard
st.title("📊 Maven Marketing Customer Analytics")
st.markdown("*Comprehensive analysis of customer profiles, campaign performance, and purchase behavior*")
st.markdown("---")

# ==================== Q1: NULL VALUES & OUTLIERS ====================
st.header("📋 1. Data Quality Analysis")
st.markdown("*Null values and outlier detection*")

col_null1, col_null2, col_null3 = st.columns(3)

with col_null1:
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    st.metric("Total Missing Values", f"{total_nulls:,}", 
              delta="0 is perfect" if total_nulls == 0 else "Needs cleaning")

with col_null2:
    null_cols = null_counts[null_counts > 0]
    st.metric("Columns with Nulls", len(null_cols))

with col_null3:
    if 'Income' in df.columns:
        income_outliers = len(df[df['Income'] > df['Income'].quantile(0.99)])
        st.metric("Income Outliers (Top 1%)", income_outliers)

with st.expander("🔍 View Null Value Details"):
    if total_nulls > 0:
        null_df = pd.DataFrame({
            'Column': null_counts.index,
            'Missing Values': null_counts.values,
            '% Missing': (null_counts.values / len(df) * 100).round(2)
        })
        null_df = null_df[null_df['Missing Values'] > 0]
        st.dataframe(null_df, use_container_width=True)
        st.info("✅ Income nulls have been filled with median values")
    else:
        st.success("✅ No missing values found in the dataset!")

st.markdown("---")

# ==================== Q2: FACTORS RELATED TO WEB PURCHASES ====================
st.header("💻 2. Factors Related to Web Purchases")
st.markdown("*Correlation analysis with NumWebPurchases*")

if 'NumWebPurchases' in filtered_df.columns:
    col_web1, col_web2 = st.columns(2)
    
    with col_web1:
        # Correlation heatmap
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
        web_corr = filtered_df[numeric_cols].corr()['NumWebPurchases'].sort_values(ascending=False)
        web_corr_df = web_corr.reset_index()
        web_corr_df.columns = ['Factor', 'Correlation']
        web_corr_df = web_corr_df[web_corr_df['Factor'] != 'NumWebPurchases']
        web_corr_df = web_corr_df.head(10)
        
        fig_web = px.bar(web_corr_df, x='Correlation', y='Factor', 
                         orientation='h', title='Top Factors Correlated with Web Purchases',
                         color='Correlation', color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_web, use_container_width=True)
    
    with col_web2:
        st.markdown("**Key Insights:**")
        top_factors = web_corr_df.head(3)
        for _, row in top_factors.iterrows():
            strength = "Strong" if abs(row['Correlation']) > 0.3 else "Moderate" if abs(row['Correlation']) > 0.2 else "Weak"
            direction = "positive" if row['Correlation'] > 0 else "negative"
            st.markdown(f"""
            - **{row['Factor']}**: {row['Correlation']:.3f} ({strength} {direction} correlation)
            """)

st.markdown("---")

# ==================== Q3: MOST SUCCESSFUL CAMPAIGN ====================
st.header("🎯 3. Marketing Campaign Performance")
st.markdown("*Which campaign was most successful?*")

campaign_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']
campaign_names = ['Campaign 1', 'Campaign 2', 'Campaign 3', 'Campaign 4', 'Campaign 5']

if all(col in df.columns for col in campaign_cols):
    col_camp1, col_camp2 = st.columns(2)
    
    with col_camp1:
        # Acceptance rates
        acceptance_rates = [df[col].mean() * 100 for col in campaign_cols]
        campaign_df = pd.DataFrame({
            'Campaign': campaign_names,
            'Acceptance Rate (%)': acceptance_rates
        })
        
        fig_camp = px.bar(campaign_df, x='Campaign', y='Acceptance Rate (%)',
                         title='Campaign Acceptance Rates',
                         color='Acceptance Rate (%)', 
                         color_continuous_scale='Viridis')
        st.plotly_chart(fig_camp, use_container_width=True)
    
    with col_camp2:
        # Best campaign
        best_campaign_idx = acceptance_rates.index(max(acceptance_rates))
        best_campaign = campaign_names[best_campaign_idx]
        best_rate = max(acceptance_rates)
        
        st.metric("🏆 Most Successful Campaign", best_campaign, f"{best_rate:.2f}% acceptance")
        
        st.markdown("**Campaign Performance Summary:**")
        for i, (name, rate) in enumerate(zip(campaign_names, acceptance_rates)):
            bar = "█" * int(rate / 2)
            st.markdown(f"- **{name}**: {bar} {rate:.1f}%")
        
        # Response to last campaign
        if 'Response' in df.columns:
            last_response = df['Response'].mean() * 100
            st.metric("📧 Last Campaign Response", f"{last_response:.2f}%")

st.markdown("---")

# ==================== Q4: AVERAGE CUSTOMER PROFILE ====================
st.header("👤 4. Average Customer Profile")
st.markdown("*Who is the typical Maven Marketing customer?*")

col_avg1, col_avg2, col_avg3, col_avg4 = st.columns(4)

with col_avg1:
    avg_age = filtered_df['Age'].mean()
    st.metric("Average Age", f"{avg_age:.0f} years")

with col_avg2:
    if 'Income' in filtered_df.columns:
        avg_income = filtered_df['Income'].mean()
        st.metric("Average Income", f"${avg_income:,.0f}")

with col_avg3:
    avg_spend = filtered_df['Total_Spending'].mean()
    st.metric("Average Total Spend", f"${avg_spend:,.0f}")

with col_avg4:
    if 'Total_Children' in filtered_df.columns:
        avg_kids = filtered_df['Total_Children'].mean()
        st.metric("Average Children", f"{avg_kids:.1f}")

# Customer profile visualization
col_profile1, col_profile2 = st.columns(2)

with col_profile1:
    # Education distribution
    if 'Education' in filtered_df.columns:
        edu_counts = filtered_df['Education'].value_counts().reset_index()
        edu_counts.columns = ['Education', 'Count']
        fig_edu = px.pie(edu_counts, values='Count', names='Education', 
                         title='Customer Education Distribution',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_edu, use_container_width=True)

with col_profile2:
    # Marital status distribution
    if 'Marital_Status' in filtered_df.columns:
        marital_counts = filtered_df['Marital_Status'].value_counts().reset_index()
        marital_counts.columns = ['Marital Status', 'Count']
        fig_marital = px.bar(marital_counts, x='Marital Status', y='Count',
                            title='Customer Marital Status',
                            color='Marital Status')
        st.plotly_chart(fig_marital, use_container_width=True)

st.markdown("**Demographic Summary:**")
col_demo1, col_demo2, col_demo3 = st.columns(3)

with col_demo1:
    if 'Country' in filtered_df.columns:
        top_country = filtered_df['Country'].value_counts().index[0]
        st.info(f"🌍 Most Common Country: **{top_country}**")

with col_demo2:
    if 'Education' in filtered_df.columns:
        top_edu = filtered_df['Education'].value_counts().index[0]
        st.info(f"🎓 Most Common Education: **{top_edu}**")

with col_demo3:
    if 'Age_Group' in filtered_df.columns:
        top_age = filtered_df['Age_Group'].value_counts().index[0]
        st.info(f"📊 Most Common Age Group: **{top_age}**")

st.markdown("---")

# ==================== Q5: BEST PERFORMING PRODUCTS ====================
st.header("🛒 5. Product Performance Analysis")
st.markdown("*Which products generate the most revenue?*")

product_cols = ['MntWines', 'MntFruits', 'MntMeatProducts', 'MntFishProducts', 
                'MntSweetProducts', 'MntGoldProds']
product_names = ['Wines', 'Fruits', 'Meat', 'Fish', 'Sweet Products', 'Gold Products']

if all(col in filtered_df.columns for col in product_cols):
    col_prod1, col_prod2 = st.columns(2)
    
    with col_prod1:
        # Total revenue by product
        product_revenue = [filtered_df[col].sum() for col in product_cols]
        product_df = pd.DataFrame({
            'Product': product_names,
            'Total Revenue ($)': product_revenue
        }).sort_values('Total Revenue ($)', ascending=True)
        
        fig_prod = px.bar(product_df, x='Total Revenue ($)', y='Product',
                         orientation='h', title='Total Revenue by Product Category',
                         color='Total Revenue ($)', color_continuous_scale='Viridis')
        st.plotly_chart(fig_prod, use_container_width=True)
    
    with col_prod2:
        # Average spend per customer
        avg_product_spend = [filtered_df[col].mean() for col in product_cols]
        avg_product_df = pd.DataFrame({
            'Product': product_names,
            'Average Spend ($)': avg_product_spend
        }).sort_values('Average Spend ($)', ascending=False)
        
        fig_avg = px.bar(avg_product_df, x='Product', y='Average Spend ($)',
                        title='Average Spend per Customer by Product',
                        color='Average Spend ($)', color_continuous_scale='Plasma')
        st.plotly_chart(fig_avg, use_container_width=True)
    
    # Best and worst products
    best_product = product_names[product_revenue.index(max(product_revenue))]
    worst_product = product_names[product_revenue.index(min(product_revenue) if min(product_revenue) > 0 else 0)]
    
    col_best1, col_best2 = st.columns(2)
    with col_best1:
        st.success(f"🏆 **Best Performing Product:** {best_product}")
        st.caption(f"Generates ${max(product_revenue):,.0f} total revenue")
    with col_best2:
        st.warning(f"⚠️ **Lowest Performing Product:** {worst_product}")
        st.caption(f"Generates ${min(product_revenue):,.0f} total revenue")

st.markdown("---")

# ==================== Q6: CHANNEL PERFORMANCE ====================
st.header("📢 6. Channel Performance Analysis")
st.markdown("*Which channels are underperforming?*")

channel_cols = ['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases']
channel_names = ['Web Purchases', 'Catalog Purchases', 'Store Purchases']

if all(col in filtered_df.columns for col in channel_cols):
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        # Total purchases by channel
        channel_totals = [filtered_df[col].sum() for col in channel_cols]
        channel_df = pd.DataFrame({
            'Channel': channel_names,
            'Total Purchases': channel_totals
        })
        
        fig_ch = px.pie(channel_df, values='Total Purchases', names='Channel',
                       title='Purchase Distribution by Channel',
                       color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_ch, use_container_width=True)
    
    with col_ch2:
        # Average purchases per customer
        channel_avg = [filtered_df[col].mean() for col in channel_cols]
        avg_channel_df = pd.DataFrame({
            'Channel': channel_names,
            'Average Purchases per Customer': channel_avg
        })
        
        fig_avg_ch = px.bar(avg_channel_df, x='Channel', y='Average Purchases per Customer',
                           title='Average Purchases per Customer by Channel',
                           color='Channel')
        st.plotly_chart(fig_avg_ch, use_container_width=True)
    
    # Identify underperforming channel
    min_channel_idx = channel_totals.index(min(channel_totals))
    underperforming = channel_names[min_channel_idx]
    
    st.info(f"⚠️ **Underperforming Channel Alert:** {underperforming} has the lowest total purchases ({min(channel_totals):,} total)")
    
    # Recommendations
    st.markdown("### 💡 Channel Optimization Recommendations")
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    
    with col_rec1:
        st.markdown("**📱 Web Channel**")
        if channel_names[0] == underperforming:
            st.warning("Needs improvement")
        else:
            st.success("Strong performance")
    
    with col_rec2:
        st.markdown("**📖 Catalog Channel**")
        if channel_names[1] == underperforming:
            st.warning("Consider digital transformation")
        else:
            st.success("Good engagement")
    
    with col_rec3:
        st.markdown("**🏪 Store Channel**")
        if channel_names[2] == underperforming:
            st.warning("Consider promotions")
        else:
            st.success("Solid performance")

st.markdown("---")

# ==================== EXTRA: CUSTOMER SEGMENTATION ====================
st.header("🎯 Customer Segmentation Insights")

col_seg1, col_seg2 = st.columns(2)

with col_seg1:
    # Spending by income bracket
    if 'Income' in filtered_df.columns and 'Total_Spending' in filtered_df.columns:
        filtered_df['Income_Bracket'] = pd.cut(filtered_df['Income'], 
                                                bins=[0, 30000, 60000, 90000, 200000],
                                                labels=['Low', 'Medium', 'High', 'Very High'])
        spend_by_income = filtered_df.groupby('Income_Bracket')['Total_Spending'].mean().reset_index()
        
        fig_income = px.bar(spend_by_income, x='Income_Bracket', y='Total_Spending',
                           title='Average Spending by Income Bracket',
                           color='Total_Spending', color_continuous_scale='Greens')
        st.plotly_chart(fig_income, use_container_width=True)

with col_seg2:
    # Campaign response by education
    if 'Education' in filtered_df.columns and 'Accepted_Any_Campaign' in filtered_df.columns:
        response_by_edu = filtered_df.groupby('Education')['Accepted_Any_Campaign'].mean().reset_index()
        response_by_edu['Response Rate'] = response_by_edu['Accepted_Any_Campaign'] * 100
        
        fig_resp = px.bar(response_by_edu, x='Education', y='Response Rate',
                         title='Campaign Response Rate by Education',
                         color='Response Rate', color_continuous_scale='Reds')
        st.plotly_chart(fig_resp, use_container_width=True)

# ==================== DATA DOWNLOAD ====================
st.markdown("---")
st.header("💾 Export Analysis")

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    csv = filtered_df.to_csv(index=False)
    st.download_button("📥 Download Filtered Customer Data", csv,
                      f"maven_customers_{datetime.now().strftime('%Y%m%d')}.csv",
                      mime="text/csv")

with col_exp2:
    # Summary statistics
    if st.button("📊 Generate Summary Report"):
        st.subheader("Numerical Summary Statistics")
        numeric_summary = filtered_df.select_dtypes(include=[np.number]).describe()
        st.dataframe(numeric_summary, use_container_width=True)

# Raw data view
with st.expander("🔍 View Raw Customer Data"):
    st.dataframe(filtered_df, use_container_width=True, height=400)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Maven Marketing Analytics Dashboard | Built with Streamlit</p>
    <p>💡 <strong>Business Insights:</strong> Use filters to segment customers and discover patterns</p>
</div>
""", unsafe_allow_html=True)
