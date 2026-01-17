import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_gsheets import GSheetsConnection
import base64

# --- SETTING DASAR ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# Masukkan URL Anda di sini
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9le3yTcQn3TAevrbOi1s7X-wGJKd-o7n1lN4o8yp7KvmOAHX9GhoGLU8x67IrZWDl/exec"

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
    # Menghapus spasi di nama kolom agar tidak KeyError
    df.columns = df.columns.str.strip()
    return df

tab1, tab2, tab3 = st.tabs(["➕ Input", "📂 Data", "🧾 Invoice"])

with tab1:
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("No Resi")
            pengirim = st.text_input("Nama Pengirim")
            produk = st.text_input("Barang")
        with c2:
            org = st.text_input("Asal")
            dst = st.text_input("Tujuan")
            kolli = st.number_input("Kolli", min_value=1)
            harga = st.number_input("Harga (Contoh: 4000)", min_value=0)
            berat = st.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN"):
            payload = {
                "Tanggal": tgl.strftime('%d/%m/%Y'), "Resi": resi, "Pengirim": pengirim,
                "Produk": produk, "Origin": org, "Destination": dst,
                "Kolli": int(kolli), "Harga": int(harga), "Berat": float(berat)
            }
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("Berhasil!")
                st.cache_data.clear()

with tab2:
    df = fetch_data()
    st.dataframe(df)

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty:
        pilih = st.selectbox("Cari Resi", df_inv['Resi'].unique())
        d = df_inv[df_inv['Resi'] == pilih].iloc[0]
        
        # LOGIKA PERBAIKAN HARGA (Paling Penting)
        # Ambil angka saja, buang titik/koma desimal yang merusak ribuan
        h_raw = str(d['Harga']).split('.')[0]
        h_fix = int("".join(filter(str.isdigit, h_raw)))
        
        total = h_fix * float(d['Berat'])
        
        st.markdown(f"""
        ### INVOICE # {d['Resi']}
        ---
        **Pengirim:** {d['Pengirim']} | **Tujuan:** {d['Destination']}
        
        | Deskripsi | Qty | Berat | Harga | Total |
        | :--- | :--- | :--- | :--- | :--- |
        | {d['Produk']} | {d['Kolli']} | {d['Berat']} Kg | Rp {h_fix:,} | **Rp {total:,}** |
        """)
