import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


def create_sum_orders_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").order_item_id.sum(
    ).sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = df.groupby(
        by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id",
                      "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_approved_at", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

    min_date = all_df["order_approved_at"].min()
    max_date = all_df["order_approved_at"].max()


# CATATAN :
# Pada Google Colab telah dijelaskan bahwa terdapat kolom order_approved_at dan order_estimated_delivery_date bernilai null, diasumsikan bahwa
# barang tersebut belum diproses oleh penjual sehingga belum dapat dikirim.

# Untuk mengatasi hal tersebut, maka saya men set nilai yang null tersebut menjadi 0. Kemudian angka 0 tersebut akan ditafsirkan sebagai nilai default pada tanggal yaitu tanggal 1-1-1970


# Untuk itu, maka sebaiknya dibuat rentang waktunya itu mulai dari 2017 - 2018
# Namun perlu diperhatika lagi bahwa, tidak semua tanggal memiliki orderan. Jadi ketika start_date, dan end_date nya di set pada tanggal yang tidak memiliki orderan, maka website akan menampilkan error


with st.sidebar:
    st.image("layout.png")

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

sum_order_items_df = create_sum_orders_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Americano Collection Dashboard :sparkles:')


# 1. PRODUK APA YANG PALING BANYAK DIMINATI
st.subheader("Produk Paling Banyak Diminati")

fig, ax = plt.subplots(figsize=(35, 15))

colors = ["#0463e4", "#acccf8", "#acccf8", "#acccf8", "#acccf8",
          "#acccf8", "#acccf8", "#acccf8", "#acccf8", "#acccf8"]
sns.barplot(x="order_item_id", y="product_category_name",
            data=sum_order_items_df.head(5), palette=colors)
ax.set_ylabel(None)
ax.set_xlabel("Number of Sales", fontsize=30)
ax.set_title("Best Performing Product", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)


# 2. BAGAIMANA DEMOGRAFI CUSTOMER BERDASARKAN NEGARA
st.subheader("Demografi Customer Berdasarkan Negara")

fig = plt.figure(figsize=(50, 20))
ax = sns.barplot(
    y="customer_count",
    x="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors
)
plt.title("Number of Customer by Gender", loc="center", fontsize=30)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=30)
plt.tick_params(axis='y', labelsize=30)
st.pyplot(fig)


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(50, 20))
rfm_df['customer_id_short'] = all_df['customer_id'].str[:10]
colors = ["#0463e4", "#0463e4", "#0463e4", "#0463e4", "#0463e4"]


st.subheader("Seberapa Sering dan Berapa Banyak Uang Yang Dihabiskan Customer")
# 3. Seberapa sering Customer Melakukan Transaksi?
sns.barplot(y="frequency", x="customer_id_short", data=rfm_df.sort_values(
    by="frequency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Frequency", loc="center", fontsize=40)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].tick_params(axis='y', labelsize=30)

# 4. Berapa Banyak Uang Yang Dihabiskan Customer Dalam Beberapa Bulan Terakhir?
sns.barplot(y="monetary", x="customer_id_short", data=rfm_df.sort_values(
    by="monetary", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Monetary", loc="center", fontsize=40)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].tick_params(axis='y', labelsize=30)

# Menampilkan judul keseluruhan
plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=50)

# Menampilkan plot dalam aplikasi Streamlit
st.pyplot(fig)
