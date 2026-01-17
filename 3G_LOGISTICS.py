import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# GANTI DENGAN URL DARI GOOGLE APPS SCRIPT KAMU
API_URL = "https://script.google.com/macros/s/AKfycbzV9hmyRqF5JErjh7aILmUTWbwVchR8a9MrKbZSzUE8FTuP2uYVlYEadxILqav8wbPn/exec"

st.set_page_config(page_title="3G LOGISTICS", layout="wide")

if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

menu = st.sidebar.radio("Menu", ["Dashboard", "Input Paket"])

if menu == "Dashboard":
    st.subheader("Data Pengiriman")
    # Mengambil data dari Google Sheet lewat Apps Script
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0]) # Baris 1 sebagai judul kolom
        st.dataframe(df, use_container_width=True)

elif menu == "Input Paket":
    with st.form("input_form"):
        resi = st.text_input("No Resi", value=f"3G-{datetime.now().strftime('%d%H%M')}")
        penerima = st.text_input("Penerima")
        layanan = st.selectbox("Layanan", ["Regular", "Express"])
        
        if st.form_submit_button("Simpan"):
            payload = {
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "resi": resi,
                "penerima": penerima,
                "layanan": layanan,
                "status": "Proses"
            }
            # Kirim data ke Apps Script
            requests.post(API_URL, json=payload)
            st.success("Data Berhasil Terkirim!")
