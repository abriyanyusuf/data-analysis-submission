import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')



# Load cleaned data

merge_df = pd.read_csv("merged_df.csv")


# Filter data
min_date = pd.to_datetime(merge_df["order_purchase_timestamp"].min())  # Convert to datetime
max_date = pd.to_datetime(merge_df["order_purchase_timestamp"].max())  # Convert to datetime

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://w7.pngwing.com/pngs/486/458/png-transparent-web-development-e-commerce-logo-electronic-business-ecommerce.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

merge_df['order_purchase_timestamp'] = pd.to_datetime(merge_df['order_purchase_timestamp'])

# Use correct variable name here
main_df = merge_df[(merge_df["order_purchase_timestamp"] >= str(start_date)) &
                   (merge_df["order_purchase_timestamp"] <= str(end_date))]

# st.dataframe(main_df)

##Function Create Top Order
def create_customer_by_city(df) :
    customer_by_city = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    customer_by_city.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return customer_by_city


def create_recency_df(df):
    recency = df.groupby('customer_unique_id', as_index=False)['order_purchase_timestamp'].max()
    recency.rename(columns={'order_purchase_timestamp': 'LastPurchaseDate'}, inplace=True)
    recent_date = df['order_purchase_timestamp'].dt.date.max()
    recency['Recency'] = recency['LastPurchaseDate'].dt.date.apply(lambda x: (recent_date - x).days)
    return recency
def create_frequency_df(df):
    frequency = df.groupby(["customer_unique_id"]).agg({"order_id": "nunique"}).reset_index()
    frequency.rename(columns={'order_id': 'Frequency'}, inplace=True)

    return frequency

def create_monetary_df(df):
    monetary = df.groupby('customer_unique_id', as_index=False)['payment_value'].sum()
    monetary.rename(columns={'payment_value': 'Monetary'}, inplace=True)
    return monetary


# # Menyiapkan berbagai dataframe
bystate_df = create_customer_by_city(main_df)
bystate_df_sorted = bystate_df.sort_values(by='customer_count', ascending=False).head(10)
recency_df = create_recency_df(main_df)
frequency_df = create_frequency_df(main_df)
monetary_df = create_monetary_df(main_df)

rfm = recency_df.merge(frequency_df, on='customer_unique_id')
rfm = rfm.merge(monetary_df, on='customer_unique_id').drop(columns='LastPurchaseDate')

# plot number of daily orders (2021)
st.header('E-Commerce Dataset Dashboard')


# customer demographic
st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

with col1:
    total_customer = bystate_df.customer_count.sum()
    st.metric("Total orders", value=total_customer)


fig, ax = plt.subplots(figsize=(20, 10))

# Use a different palette or let Seaborn choose the default
# You can try using 'viridis' as an example of a predefined palette
sns.barplot(y = bystate_df_sorted.customer_city[:20],
x = bystate_df_sorted.customer_count[:20])

ax.set_title("20 Daftar Teratas Kota Asal Pelanggan", loc="center", fontsize=30)
ax.set_ylabel("Kota", fontsize=22)
ax.set_xlabel("Total Pelanggan", fontsize=22)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")

col1, col2 = st.columns(2)



with col1:
    avg_frequency = round(frequency_df.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col2:
    avg_frequency = format_currency(monetary_df.Monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]



sns.barplot(x="Frequency", y="customer_unique_id", data=rfm.sort_values(by="Frequency", ascending=False).head(10), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Frequency", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(x="Monetary", y="customer_unique_id", data=rfm.sort_values(by="Monetary", ascending=False).head(10), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Monetary", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

# Adjust layout to prevent overlap and add space above suptitle
plt.tight_layout(rect=[0, 0.00000000001, 1, 0.95])

st.pyplot(fig)
