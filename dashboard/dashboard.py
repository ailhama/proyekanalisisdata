import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# # load dataset

day_df = pd.read_csv("https://raw.githubusercontent.com/ailhama/proyekanalisisdata/main/dashboard/day2.csv")
hour_df = pd.read_csv("https://raw.githubusercontent.com/ailhama/proyekanalisisdata/main/dashboard/hour2.csv")
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
st.set_page_config(page_title="Dashboard Analisis Data Bikeshare dataset", page_icon=":bar_chart:", initial_sidebar_state="expanded")

# # create helper functions
def create_peminjam_bulanan_df(day_df):
    peminjam_bulanan_df = day_df.resample(rule='M', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    peminjam_bulanan_df.index = peminjam_bulanan_df.index.strftime('%b-%y')
    peminjam_bulanan_df = peminjam_bulanan_df.reset_index()
    peminjam_bulanan_df.rename(columns={
        "dteday": "yearmonth",
        "cnt": "total_peminjam",
        "casual": "peminjam_biasa",
        "registered": "peminjam_terdaftar"
    }, inplace=True)
    
    return peminjam_bulanan_df

def create_peminjam_musim_df(day_df):
    peminjam_musim_df = day_df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    peminjam_musim_df = peminjam_musim_df.reset_index()
    peminjam_musim_df.rename(columns={
        "cnt": "total_rides",
        "casual": "peminjam_biasa",
        "registered": "peminjam_terdaftar"
    }, inplace=True)
    
    peminjam_musim_df = pd.melt(peminjam_musim_df,
                                      id_vars=['season'],
                                      value_vars=['peminjam_biasa', 'peminjam_terdaftar'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    peminjam_musim_df['season'] = pd.Categorical(peminjam_musim_df['season'],
                                             categories=['Semi', 'Panas', 'Gugur', 'Dingin'])
    
    peminjam_musim_df = peminjam_musim_df.sort_values('season')
    
    return peminjam_musim_df

def create_peminjam_cuaca_df(day_df):
    peminjam_cuaca_df = day_df.groupby("weathersit").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    peminjam_cuaca_df = peminjam_cuaca_df.reset_index()
    peminjam_cuaca_df.rename(columns={
        "cnt": "total_rides",
        "casual": "peminjam_biasa",
        "registered": "peminjam_terdaftar"
    }, inplace=True)
    
    peminjam_cuaca_df = pd.melt(peminjam_cuaca_df,
                                      id_vars=['weathersit'],
                                      value_vars=['peminjam_biasa', 'peminjam_terdaftar'],
                                      var_name='type_of_rides',
                                      value_name='count_rides')
    
    peminjam_cuaca_df['weathersit'] = pd.Categorical(peminjam_cuaca_df['weathersit'],
                                             categories=['Cerah','berkabut/kabut','hujan ringan/hujan salju ringan','hujan lebat/salju lebat'])
    peminjam_cuaca_df = peminjam_cuaca_df.sort_values('weathersit')
    
    return peminjam_cuaca_df

# make filter components (komponen filter)

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# # ----- SIDEBAR -----

with st.sidebar:
    # add capital bikeshare logo
    st.image("https://raw.githubusercontent.com/ailhama/proyekanalisisdata/main/images/logo.jpg")

# mengambil start_date & end_date dari date_input
start_date = st.sidebar.date_input("Pilih Tanggal Awal", min_value=day_df['dteday'].min(), max_value=day_df['dteday'].max(), value=day_df['dteday'].min())
end_date = st.sidebar.date_input("Pilih Tanggal Akhir", min_value=day_df['dteday'].min(), max_value=day_df['dteday'].max(), value=day_df['dteday'].max())

main_df_day = day_df.loc[
    (day_df["dteday"] >= pd.Timestamp(start_date)) &
    (day_df["dteday"] <= pd.Timestamp(end_date))
]
main_df_hour = hour_df.loc[
    (hour_df["dteday"] >= pd.Timestamp(start_date)) &
    (hour_df["dteday"] <= pd.Timestamp(end_date))
]

# Mengonversi nilai start_date dan end_date menjadi tipe data datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# assign main_df ke helper functions yang telah dibuat sebelumnya
peminjam_bulanan_df = create_peminjam_bulanan_df(main_df_day)
peminjam_musim_df = create_peminjam_musim_df(main_df_day)
peminjam_cuaca_df = create_peminjam_cuaca_df(main_df_day)


# # ----- MAINPAGE -----
st.title("Dashboard Proyek Analisis Data Bike-Sharing")
st.markdown("##")

col1, col2, col3 = st.columns(3)

with col1:
    total_semua_peminjam = main_df_day['cnt'].sum()
    st.metric("Total Peminjam", value=total_semua_peminjam)
with col2:
    total_peminjam_biasa = main_df_day['casual'].sum()
    st.metric("Total Peminjam Biasa", value=total_peminjam_biasa)
with col3:
    total_peminjam_terdaftar = main_df_day['registered'].sum()
    st.metric("Total Peminjam Terdaftar", value=total_peminjam_terdaftar)

st.markdown("---")

# # ----- CHART -----
fig = px.line(peminjam_bulanan_df,
              x='yearmonth',
              y=['peminjam_biasa', 'peminjam_terdaftar', 'total_peminjam'],
              color_discrete_sequence=px.colors.qualitative.G10,
              markers=True,
              title="Total Jumlah Peminjaman dalam bulan").update_layout(xaxis_title='Bulan', yaxis_title='Total Peminjam')

st.plotly_chart(fig, use_container_width=True)

# Membuat palet warna kustom
custom_palette = sns.color_palette("Paired")

# Konversi palet warna kustom menjadi format Plotly Express
custom_palette_hex = custom_palette.as_hex()

fig1 = px.bar(peminjam_cuaca_df,
              x='weathersit',
              y=['count_rides'],
              color='type_of_rides',
              barmode='group',
              color_discrete_sequence=custom_palette_hex,
              title='Total Jumlah Peminjaman berdasarkan Cuaca').update_layout(xaxis_title='Cuaca', yaxis_title='Total Peminjam')

fig2 = px.bar(peminjam_musim_df,
              x='season',
              y=['count_rides'],
              color='type_of_rides',
              barmode='group',
              color_discrete_sequence=custom_palette_hex,
              title='Total Jumlah Peminjaman berdasarkan Musim').update_layout(xaxis_title='Musim', yaxis_title='Total Peminjam')

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

st.caption('Copyright (c), Dibuat Oleh Audi Ilham Atmaja')
