import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI API & HALAMAN ---
# GANTI DENGAN URL WEB APP GOOGLE APPS SCRIPT KAMU
API_URL = st.secrets["API_URL"]
try:
    from PIL import Image
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="wide")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

# --- 2. FUNGSI PENDUKUNG ---

def ambil_data_cloud():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame()

def buat_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Invoice (Banner)
    if os.path.exists("HEADER INVOICE.png"):
        pdf.image("HEADER INVOICE.png", x=10, y=8, w=190)
        pdf.ln(40)
    else:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "INVOICE PENGIRIMAN - 3G LOGISTICS", ln=True, align='C')
        pdf.ln(10)

    # Isi Detail
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Tanggal: {data['waktu']}", ln=True)
    pdf.cell(190, 10, f"No. Resi  : {data['resi']}", ln=True)
    pdf.ln(5)
    
    # Tabel
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(95, 10, "Penerima", 1, 0, 'C', True)
    pdf.cell(95, 10, "Layanan", 1, 1, 'C', True)
    
    pdf.cell(95, 10, data['penerima'], 1, 0, 'C')
    pdf.cell(95, 10, data['layanan'], 1, 1, 'C')
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 8, "Terima kasih telah menggunakan jasa PT. GAMA GEMAH GEMILANG. Paket Anda akan segera kami proses.")

    # Stempel/Tanda Tangan
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=140, y=pdf.get_y() + 5, w=40)

    return pdf.output(dest='S').encode('latin-1')

# --- 3. TAMPILAN UTAMA ---

if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=120)
    st.title("3G LOGISTICS")
    st.write("PT. GAMA GEMAH GEMILANG")
    st.divider()
    menu = st.radio("Menu Utama", ["🏠 Dashboard", "📝 Input Paket", "🔍 Lacak Resi"])

# --- 4. LOGIKA MENU ---

if menu == "🏠 Dashboard":
    st.subheader("Data Pengiriman Real-time")
    df = ambil_data_cloud()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if st.button("🔄 Refresh Data"):
            st.rerun()
    else:
        st.info("Belum ada data di Google Sheets.")

elif menu == "📝 Input Paket":
    st.subheader("Form Input Pengiriman Baru")
    with st.form("input_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No. Resi", value=f"3G-{datetime.now().strftime('%d%H%M')}")
            penerima = st.text_input("Nama Penerima")
        with c2:
            layanan = st.selectbox("Layanan", ["Regular", "Express", "Kargo"])
            status = "Booking"
        
        submitted = st.form_submit_button("Simpan & Buat Invoice")
        
        if submitted:
            if not penerima:
                st.error("Nama penerima tidak boleh kosong!")
            else:
                payload = {
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "resi": resi,
                    "penerima": penerima,
                    "layanan": layanan,
                    "status": status
                }
                
                # Kirim ke Google Sheets
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.text == "Success":
                        st.success(f"Berhasil! Data Resi {resi} tersimpan.")
                        
                        # Generate PDF
                        pdf_data = buat_pdf(payload)
                        st.download_button(
                            label="📥 Download Invoice (PDF)",
                            data=pdf_data,
                            file_name=f"Invoice_{resi}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("Gagal menyimpan ke Google Sheets.")
                except Exception as e:
                    st.error(f"Error: {e}")

elif menu == "🔍 Lacak Resi":
    st.subheader("Tracking Paket")
    cari = st.text_input("Masukkan No. Resi")
    if st.button("Cari"):
        df = ambil_data_cloud()
        if not df.empty:
            hasil = df[df['Resi'].astype(str) == cari]
            if not hasil.empty:
                st.success(f"Status Saat Ini: **{hasil.iloc[0]['Status']}**")
                st.table(hasil)
            else:
                st.error("Nomor resi tidak ditemukan.")

st.divider()
st.caption("© 2026 PT. GAMA GEMAH GEMILANG | 3G LOGISTICS")

