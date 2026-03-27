import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "https://ai-based-customer-support-backend.onrender.com"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Customer Support Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Support AI Dashboard")
st.markdown("### 🚀 Smart Ticketing & Analytics System")
st.markdown("---")

# =========================
# CUSTOMER QUERY INPUT
# =========================
st.markdown("## 🧾 Raise a Support Ticket")

with st.form("ticket_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Customer Name")
    with col2:
        product = st.text_input("💻 Product")

    issue = st.text_area("📝 Describe your issue")

    submit = st.form_submit_button("🚀 Submit Ticket")

    if submit:
        data = {
            "customer_name": name,
            "product": product,
            "issue": issue
        }

        try:
            response = requests.post(f"{API_URL}/new-ticket", data=data)

            if response.status_code == 200:
                result = response.json()

                # 🔥 HANDLE ERROR SAFELY
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success("✅ Ticket Created Successfully!")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 🤖 AI Response")
                        st.info(result.get("response", "No response generated"))

                    with col2:
                        st.markdown("### 📊 Analysis")
                        st.metric("Sentiment", result.get("sentiment", "N/A"))
                        st.metric("Priority", result.get("priority", "N/A"))

                    st.cache_data.clear()

            else:
                st.error("❌ Failed to create ticket")

        except Exception as e:
            st.error(f"API Error: {e}")

st.markdown("---")

# =========================
# FETCH DATA
# =========================
@st.cache_data
def get_data():
    try:
        tickets_res = requests.get(f"{API_URL}/tickets")
        insights_res = requests.get(f"{API_URL}/insights")
        sentiment_res = requests.get(f"{API_URL}/sentiment")

        if tickets_res.status_code != 200:
            return pd.DataFrame(), {}, {}

        tickets = tickets_res.json()
        insights = insights_res.json() if insights_res.status_code == 200 else {}
        sentiment = sentiment_res.json() if sentiment_res.status_code == 200 else {}

        df = pd.DataFrame(tickets)

        # 🔥 CLEAN NONE VALUES FOR UI
        df = df.fillna("Unknown")

        return df, insights, sentiment

    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame(), {}, {}

df, insights, sentiment = get_data()

if df.empty:
    st.warning("⚠️ No data available. Check API.")
    st.stop()

# =========================
# FILTERS SIDEBAR
# =========================
st.sidebar.header("🔍 Filters")

ticket_type = st.sidebar.selectbox(
    "📂 Ticket Type", ["All"] + sorted(df["ticket_type"].unique().tolist())
)
priority = st.sidebar.selectbox(
    "⚡ Priority", ["All"] + sorted(df["ticket_priority"].unique().tolist())
)
product_filter = st.sidebar.selectbox(
    "💻 Product", ["All"] + sorted(df["product_purchased"].unique().tolist())
)
customer = st.sidebar.selectbox(
    "👤 Customer", ["All"] + sorted(df["customer_name"].unique().tolist())
)

# =========================
# APPLY FILTERS
# =========================
filtered_df = df.copy()

if ticket_type != "All":
    filtered_df = filtered_df[filtered_df["ticket_type"] == ticket_type]

if priority != "All":
    filtered_df = filtered_df[filtered_df["ticket_priority"] == priority]

if product_filter != "All":
    filtered_df = filtered_df[filtered_df["product_purchased"] == product_filter]

if customer != "All":
    filtered_df = filtered_df[filtered_df["customer_name"] == customer]

# =========================
# KPI CARDS
# =========================
st.markdown("## 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📄 Total Tickets", len(filtered_df))
col2.metric("⚠️ High Priority", int(filtered_df['is_high_priority'].sum()))
col3.metric("⏱ Avg Resolution Time", 0)
col4.metric("⭐ Avg Satisfaction", 0)

st.markdown("---")

# =========================
# SENTIMENT PIE
# =========================
st.subheader("😊 Sentiment Distribution")

if not filtered_df.empty:
    fig1 = px.pie(
        filtered_df,
        names="sentiment",
        title="Sentiment Distribution"
    )
    st.plotly_chart(fig1, use_container_width=True)

# =========================
# PRIORITY PIE
# =========================
st.subheader("⚡ Priority Distribution")

fig2 = px.pie(
    filtered_df,
    names="ticket_priority",
    title="priority distribution"
)
st.plotly_chart(fig2, use_container_width=True)

# =========================
# TREND
# =========================
st.subheader("📈 Tickets Over Time")

if 'date_of_purchase' in filtered_df.columns:
    df_date = filtered_df.copy()
    df_date['date'] = pd.to_datetime(df_date['date_of_purchase'], errors='coerce').dt.date

    trend = df_date.groupby('date').size().reset_index(name='Tickets')

    fig3 = px.line(trend, x='date', y='Tickets', title="Tickets Trend")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# =========================
# TABLE
# =========================
st.subheader("📋 Tickets Data")
st.dataframe(filtered_df, use_container_width=True)

# =========================
# EXTRA ANALYSIS
# =========================
st.markdown("## 🔍 Top 10 Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Tickets by Product")
    fig4 = px.bar(filtered_df["product_purchased"].value_counts().head(10))
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader("👤 Tickets by Customer")
    fig5 = px.bar(filtered_df["customer_name"].value_counts().head(10))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.markdown("### 🤖 AI-Powered Customer Support System | FastAPI + ML + Streamlit")