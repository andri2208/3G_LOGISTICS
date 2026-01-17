import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_gsheets import GSheetsConnection

# --- SETTING DASAR ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# URL (Pastikan URL ini benar)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzXgo5VKAEzx3WhjB4RIq91oG-N5dKA3sAHGCTNaUOj_f6CGRDHSe12UOL9aZYCuKk_/exec"

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        # Membaca data dengan pembersihan spasi di nama kolom
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["➕ Input Data", "📂 Database", "🧾 Invoice"])

# --- TAB 1: INPUT ---
with tab1:
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi_input = st.text_input("No Resi")
            pengirim = st.text_input("Nama Pengirim")
            produk = st.text_input("Barang")
        with c2:
            org = st.text_input("Asal")
            dst = st.text_input("Tujuan")
            kolli = st.number_input("Kolli", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0, step=100)
            berat = st.number_input("Berat (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("SIMPAN DATA"):
            if resi_input and pengirim:
                payload = {
                    "Tanggal": tgl.strftime('%d/%m/%Y'),
                    "Resi": str(resi_input),
                    "Pengirim": str(pengirim),
                    "Produk": str(produk),
                    "Origin": str(org),
                    "Destination": str(dst),
                    "Kolli": str(int(kolli)),
                    "Harga": str(int(harga)),
                    "Berat": str(float(berat))
                }
                res = requests.post(APPS_SCRIPT_URL, json=payload)
                if res.status_code == 200:
                    st.success(f"Berhasil simpan Resi: {resi_input}")
                    st.cache_data.clear()
                else:
                    st.error("Gagal terhubung ke Google Sheets.")
            else:
                st.warning("Mohon isi No Resi dan Nama Pengirim.")

# --- TAB 2: DATABASE ---
with tab2:
    df = fetch_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Database kosong atau kolom tidak ditemukan.")

# --- TAB 3: INVOICE (ANTI KEYERROR) ---
with tab3:
    df_inv = fetch_data()
    
    # Cek apakah kolom 'Resi' ada di database
    if not df_inv.empty and 'Resi' in df_inv.columns:
        resi_list = df_inv['Resi'].dropna().unique()
        pilih = st.selectbox("Cari No Resi untuk Invoice", resi_list)
        
        if pilih:
            d = df_inv[df_inv['Resi'] == pilih].iloc[0]
            
            # Perbaikan Harga (Logic Anti-40)
            h_raw = str(d.get('Harga', '0')).split('.')[0]
            h_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
            
            berat_val = pd.to_numeric(d.get('Berat', 0), errors='coerce')
            total = h_fix * (float(berat_val) if not pd.isna(berat_val) else 0.0)
            
            st.markdown(f"""
            ### INVOICE: {d.get('Resi', '-')}
            **Customer:** {d.get('Pengirim', '-')}  
            **Rute:** {d.get('Origin', '-')} ke {d.get('Destination', '-')}
            
            | Deskripsi | Qty | Berat | Harga | Total |
            | :--- | :--- | :--- | :--- | :--- |
            | {d.get('Produk','-')} | {d.get('Kolli',0)} | {berat_val} Kg | Rp {h_fix:,} | **Rp {total:,}** |
            """)
            st.info("Gunakan Ctrl+P untuk print.")
    else:
        st.error("Data tidak ditemukan. Pastikan header 'Resi' ada di Google Sheets.")
