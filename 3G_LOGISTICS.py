import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

# URL yang Anda berikan
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9le3yTcQn3TAevrbOi1s7X-wGJKd-o7n1lN4o8yp7KvmOAHX9GhoGLU8x67IrZWDl/exec"

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        # ttl=0 supaya data selalu paling baru
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip() # Hapus spasi di nama kolom
        return df
    except:
        return pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["➕ Tambah Data", "📂 Database", "🧾 Cetak Invoice"])

# --- TAB 1: INPUT ---
with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("Nomor Resi")
            customer = st.text_input("Nama Customer")
            produk = st.text_input("Deskripsi Barang")
        with col2:
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
            kolli = st.number_input("Kolli", min_value=1, step=1)
            harga = st.number_input("Harga Satuan (Input 4000)", min_value=0, step=100)
            berat = st.number_input("Berat (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("🚀 SIMPAN KE GOOGLE SHEETS"):
            if resi and customer:
                payload = {
                    "Tanggal": tgl.strftime('%d-%b-%y'),
                    "Resi": str(resi),
                    "Pengirim": str(customer),
                    "Produk": str(produk),
                    "Origin": str(origin),
                    "Destination": str(dest),
                    "Kolli": str(int(kolli)),
                    "Harga": str(int(harga)),
                    "Berat": str(float(berat))
                }
                try:
                    resp = requests.post(APPS_SCRIPT_URL, json=payload)
                    if resp.status_code == 200:
                        st.success(f"✅ Data {resi} Berhasil Disimpan!")
                        st.cache_data.clear()
                    else:
                        st.error("Gagal Simpan. Cek Deployment Apps Script Anda.")
                except Exception as e:
                    st.error(f"Koneksi Error: {e}")
            else:
                st.warning("Resi dan Nama Customer wajib diisi!")

# --- TAB 2: DATABASE ---
with tab2:
    df = fetch_data()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Database masih kosong. Pastikan Header di Google Sheet sudah benar.")

# --- TAB 3: INVOICE ---
with tab3:
    df_inv = fetch_data()
    # Pengecekan kolom 'Resi' untuk menghindari KeyError
    if not df_inv.empty and 'Resi' in df_inv.columns:
        resi_list = df_inv['Resi'].dropna().unique()
        pilih_resi = st.selectbox("Pilih Nomor Resi", resi_list)
        
        if pilih_resi:
            d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
            
            # --- LOGIKA HARGA ANTI-40 ---
            # Kita bersihkan semua titik/koma yang bikin 4000 jadi 40.0
            h_raw = str(d.get('Harga', '0')).split('.')[0]
            h_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
            
            b_val = pd.to_numeric(d.get('Berat', 0), errors='coerce')
            total = h_fix * (float(b_val) if not pd.isna(b_val) else 0.0)
            
            st.markdown(f"""
            <div style="border: 2px solid #1a3d8d; padding: 20px; border-radius: 10px;">
                <h2 style="color: #1a3d8d; margin-top: 0;">INVOICE #{d['Resi']}</h2>
                <hr>
                <p><b>Customer:</b> {d['Pengirim']}</p>
                <p><b>Barang:</b> {d['Produk']} ({d['Kolli']} Kolli)</p>
                <p><b>Rute:</b> {d['Origin']} ➡ {d['Destination']}</p>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f0f2f6;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Berat</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Harga Satuan</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Total Tagihan</th>
                    </tr>
                    <tr style="text-align: center;">
                        <td style="padding: 10px; border: 1px solid #ddd;">{b_val} Kg</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">Rp {h_fix:,.0f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; color: #d62828;">Rp {total:,.0f}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Kolom 'Resi' tidak ditemukan. Cek baris pertama Google Sheets Anda.")
