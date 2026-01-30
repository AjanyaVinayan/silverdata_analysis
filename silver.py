import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd

st.set_page_config(page_title="Silver Price Calculator", layout="wide")

st.title("Silver Price Calculator & Dashboard")

# Load data
@st.cache_data
def load_historical_data():
    try:
        data = pd.read_csv("historical_silver_price.csv")
        return data
    except FileNotFoundError:
        st.error("historical_silver_price.csv not found.")
        return None

@st.cache_data
def load_state_data():
    try:
        data = pd.read_csv("state_wise_silver_purchased_kg.csv")
        return data
    except FileNotFoundError:
        st.error("state_wise_silver_purchased_kg.csv not found.")
        return None

historical_data = load_historical_data()
state_data = load_state_data()

CURRENCY_RATES = {
    "INR": 1,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095
}

page = st.sidebar.radio("Select Page:", ["Calculator", "Analysis", "Dashboard"])

# ==================== CALCULATOR ====================
if page == "Calculator":
    st.header("Silver Price Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        weight_unit = st.radio("Weight Unit:", ["Grams", "Kilograms"])
        weight = st.number_input("Enter Weight:", min_value=0.0, step=0.1)
        weight_grams = weight * 1000 if weight_unit == "Kilograms" else weight
        price_per_gram = st.number_input("Price per Gram (INR):", min_value=0.0, step=1.0, value=6500.0)
    
    with col2:
        selected_currency = st.selectbox("Currency:", list(CURRENCY_RATES.keys()))
    
    total_cost_inr = weight_grams * price_per_gram
    total_cost_converted = total_cost_inr * CURRENCY_RATES[selected_currency]
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Weight", f"{weight_grams:.2f} g")
    with col2:
        st.metric("Cost (INR)", f"₹ {total_cost_inr:,.2f}")
    with col3:
        st.metric(f"Cost ({selected_currency})", f"{total_cost_converted:,.2f}")
    
    st.divider()
    st.subheader("Historical Silver Price Chart")
    
    price_filter = st.selectbox("Price Range:", ["All", "≤ 20,000", "20,000-30,000", "≥ 30,000"])
    
    if historical_data is not None and "Silver_Price_INR_per_kg" in historical_data.columns:
        filtered = historical_data.copy()
        
        if price_filter == "≤ 20,000":
            filtered = filtered[filtered['Silver_Price_INR_per_kg'] <= 20000]
        elif price_filter == "20,000-30,000":
            filtered = filtered[(filtered['Silver_Price_INR_per_kg'] >= 20000) & (filtered['Silver_Price_INR_per_kg'] <= 30000)]
        elif price_filter == "≥ 30,000":
            filtered = filtered[filtered['Silver_Price_INR_per_kg'] >= 30000]
        
        fig, ax = plt.subplots()
        ax.plot(filtered['Silver_Price_INR_per_kg'], marker='o')
        ax.set_ylabel("Price (INR/kg)")
        ax.set_title("Silver Price Trend")
        st.pyplot(fig)

# ==================== ANALYSIS ====================
elif page == "Analysis":
    st.header("Historical Analysis")
    
    if historical_data is not None and "Silver_Price_INR_per_kg" in historical_data.columns:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Price", f"₹ {historical_data['Silver_Price_INR_per_kg'].mean():,.0f}")
        with col2:
            st.metric("Max Price", f"₹ {historical_data['Silver_Price_INR_per_kg'].max():,.0f}")
        with col3:
            st.metric("Min Price", f"₹ {historical_data['Silver_Price_INR_per_kg'].min():,.0f}")
        with col4:
            st.metric("Total Records", len(historical_data))
        
        st.divider()
        
        st.subheader("Price Distribution")
        ranges = ["≤ 20k", "20k-30k", "≥ 30k"]
        counts = [
            len(historical_data[historical_data['Silver_Price_INR_per_kg'] <= 20000]),
            len(historical_data[(historical_data['Silver_Price_INR_per_kg'] > 20000) & (historical_data['Silver_Price_INR_per_kg'] < 30000)]),
            len(historical_data[historical_data['Silver_Price_INR_per_kg'] >= 30000])
        ]
        fig, ax = plt.subplots()
        ax.bar(ranges, counts, color='steelblue')
        ax.set_ylabel("Count")
        ax.set_title("Records by Price Range")
        st.pyplot(fig)
        
        st.divider()
        st.subheader("Data Preview")
        st.dataframe(historical_data.head(10))

# ==================== DASHBOARD ====================
elif page == "Dashboard":
    st.header("Silver Sales Dashboard")
    
    if state_data is not None:
        # Top 5 States
        st.subheader("Top 5 States with Highest Silver Purchases")
        
        top5 = state_data.nlargest(5, 'Silver_Purchased_kg')
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(top5['State'], top5['Silver_Purchased_kg'], color='steelblue')
        ax.set_ylabel("Silver Purchase (kg)")
        ax.set_title("Top 5 States")
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
        st.dataframe(top5)
        
        st.divider()
        
   
      
 
        
        # All States Data
        st.subheader("All States Silver Purchases Data")
        
        sorted_data = state_data.sort_values('Silver_Purchased_kg', ascending=False)
        st.dataframe(sorted_data)
        
        st.divider()
        
        # State-wise Distribution
        st.subheader("State-wise Distribution")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.barh(sorted_data['State'], sorted_data['Silver_Purchased_kg'], color='steelblue')
        ax.set_xlabel("Silver Purchase (kg)")
        ax.set_title("All States Silver Purchases")
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)
        
        st.divider()
        
        