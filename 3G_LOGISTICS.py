import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURASI ---
# GANTI link di bawah ini dengan URL Web App (ujungnya /exec) yang kamu dapatkan dari Google Apps Script
API_URL = st.secrets["API_URL"]

# 1. Konfigurasi Halaman
try:
    from PIL import Image
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="wide")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

# 2. Header Banner
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)
else:
    st.title("🚚 3G LOGISTICS")

# 3. Sidebar
with st.sidebar:
    if os.path.exists("FAVICON.png"):
        st.image("FAVICON.png", width=100)
    st.title("PT. GAMA GEMAH GEMILANG")
    st.divider()
    menu = st.radio("Navigasi", ["🏠 Dashboard", "📝 Input Paket Baru", "🔍 Lacak Resi"])

# --- FUNGSI DATABASE ---
def ambil_data_cloud():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            # Baris pertama adalah Header, sisanya adalah Data
            return pd.DataFrame(data[1:], columns=data[0])
    except:
        return pd.DataFrame()

# --- LOGIKA MENU ---
if menu == "🏠 Dashboard":
    st.subheader("Data Pengiriman di Google Sheets")
    df = ambil_data_cloud()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if st.button("Refresh Data"):
            st.rerun()
    else:
        st.warning("Gagal mengambil data atau spreadsheet masih kosong.")

elif menu == "📝 Input Paket Baru":
    st.subheader("Form Input Pengiriman")
    with st.form("form_input"):
        resi = st.text_input("Nomor Resi", value=f"3G-{datetime.now().strftime('%d%H%M')}")
        penerima = st.text_input("Nama Penerima")
        layanan = st.selectbox("Layanan", ["Regular", "Express", "Kargo"])
        status = "Booking"
        
        if st.form_submit_button("Kirim ke Google Sheets"):
            payload = {
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "resi": resi,
                "penerima": penerima,
                "layanan": layanan,
                "status": status
            }
            try:
                res = requests.post(API_URL, json=payload)
                if res.text == "Success":
                    st.success(f"Data Resi {resi} Berhasil Disimpan!")
                else:
                    st.error("Gagal menyimpan. Pastikan Deployment Apps Script sudah 'Anyone'.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

from fpdf import FPDF
import base64

# --- FUNGSI BUAT PDF ---
def buat_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header - Gunakan gambar HEADER INVOICE jika ada
    if os.path.exists("HEADER INVOICE.png"):
        pdf.image("HEADER INVOICE.png", x=10, y=8, w=190)
        pdf.ln(40) # Kasih jarak setelah gambar
    else:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "INVOICE PENGIRIMAN - 3G LOGISTICS", ln=True, align='C')
        pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Tanggal: {data['waktu']}", ln=True)
    pdf.cell(190, 10, f"No. Resi: {data['resi']}", ln=True)
    pdf.ln(5)
    
    # Tabel Sederhana
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(95, 10, "Penerima", 1, 0, 'C', True)
    pdf.cell(95, 10, "Layanan", 1, 1, 'C', True)
    
    pdf.cell(95, 10, data['penerima'], 1, 0, 'C')
    pdf.cell(95, 10, data['layanan'], 1, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 10, "Terima kasih telah menggunakan jasa PT. GAMA GEMAH GEMILANG. Barang Anda akan segera kami proses sesuai dengan layanan yang dipilih.")

    # Stempel / Tanda Tangan jika ada
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=140, y=pdf.get_y() + 5, w=40)

    return pdf.output(dest='S').encode('latin-1')

# --- DALAM MENU INPUT PAKET (BAGIAN SUBMIT) ---
# (Cari bagian "if submit:" di kode sebelumnya, lalu sesuaikan seperti ini)

if submit:
    payload = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "resi": resi,
        "penerima": penerima,
        "layanan": layanan,
        "status": status
    }
    
    res = requests.post(API_URL, json=payload)
    if res.text == "Success":
        st.success(f"Data Resi {resi} Berhasil Disimpan!")
        
        # Buat PDF
        pdf_data = buat_pdf(payload)
        
        # Tombol Download PDF
        st.download_button(
            label="📥 Cetak Invoice (PDF)",
            data=pdf_data,
            file_name=f"Invoice_{resi}.pdf",
            mime="application/pdf"
        )
        

elif menu == "🔍 Lacak Resi":
    st.subheader("Cari Status Paket")
    cari = st.text_input("Masukkan No. Resi")
    if st.button("Lacak"):
        df = ambil_data_cloud()
        if not df.empty:
            hasil = df[df['Resi'].astype(str) == cari]
            if not hasil.empty:
                st.success(f"Status: {hasil.iloc[0]['Status']}")
                st.table(hasil)
            else:
                st.error("Data tidak ditemukan.")

st.divider()
st.caption("© 2026 3G LOGISTICS | Sistem Logistik Terintegrasi")


