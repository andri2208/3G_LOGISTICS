import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI ---
# Ganti dengan URL dari Google Apps Script kamu
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec" 

st.set_page_config(page_title="3G LOGISTICS - Invoice System", layout="wide")

# --- 2. FUNGSI TERBILANG (Sesuai dokumen) ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return ""

# --- 3. FUNGSI PDF (Format PT. GAMA GEMAH GEMILANG) ---
def buat_pdf_custom(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Perusahaan [cite: 1, 2]
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 7, "PT. GAMA GEMAH GEMILANG", ln=True)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(130, 4, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik, Jawa Timur. Telp 031-79973432")
    pdf.ln(5)
    
    # Customer Info [cite: 3, 4, 5]
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 6, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 6, "INVOICE", 0, 1, 'R')
    pdf.set_font("Arial", size=9)
    pdf.cell(100, 6, "", 0)
    pdf.cell(90, 6, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(5)
    
    # Tabel Header [cite: 6]
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    headers = ["Date of Load", "Product Description", "Origin", "Destination", "Harga", "Weight", "Total"]
    widths = [25, 55, 20, 20, 20, 20, 30]
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1, 0, 'C', True)
    pdf.ln()
    
    # Tabel Isi [cite: 6]
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(55, 10, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['harga']:,.0f}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C')
    
    # Pembayaran [cite: 7, 8, 9, 10, 11]
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(190, 10, f"Terbilang: {terbilang(data['total'])} Rupiah", ln=True)

    # Info Bank [cite: 12, 13, 14, 15, 16]
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA)", ln=True)
    pdf.cell(190, 5, "6720422334", ln=True)
    pdf.cell(190, 5, "A/N ADITYA GAMA SAPUTRI", ln=True)
    pdf.cell(190, 5, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200", ln=True)
    
    # Tanda Tangan [cite: 17, 18, 19, 20]
    pdf.ln(10)
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. TAMPILAN APLIKASI ---
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

st.title("📝 Buat Invoice Baru")

# Pastikan session state selalu ada
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None

# Form Input
with st.container(border=True):
    with st.form("main_form"):
        cust = st.text_input("Customer Name (Penerima)") [cite: 3]
        desc = st.text_input("Product Description") [cite: 6]
        c1, c2, c3, c4 = st.columns(4)
        with c1: ori = st.text_input("Origin (Asal)") [cite: 6]
        with c2: dest = st.text_input("Destination (Tujuan)") [cite: 6]
        with c3: hrg = st.number_input("Harga Satuan", value=8500) [cite: 6]
        with c4: wgt = st.number_input("Weight (Kg)", value=1) [cite: 6]
        
        btn_submit = st.form_submit_button("Lihat Preview & Simpan")
        
        if btn_submit:
            # Data diproses ke session state hanya jika tombol ditekan
            st.session_state.preview_data = {
                "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                "penerima": cust,
                "deskripsi": desc,
                "asal": ori,
                "tujuan": dest,
                "harga": hrg,
                "berat": wgt,
                "total": hrg * wgt
            }
            # Kirim data ke database Google Sheets
            try:
                requests.post(API_URL, json=st.session_state.preview_data)
            except:
                st.error("Gagal terhubung ke database.")

# --- 5. HALAMAN PREVIEW (Ditampilkan hanya jika preview_data tidak None) ---
if st.session_state.preview_data is not None:
    # Ambil data dari session state ke variabel lokal
    data_inv = st.session_state.preview_data
    
    st.divider()
    st.subheader("🔍 Preview Invoice")
    
    with st.container(border=True):
        st.write(f"**PT. GAMA GEMAH GEMILANG**") [cite: 1]
        col_x, col_y = st.columns(2)
        with col_x:
            st.write(f"**Customer:** {data_inv['penerima']}") [cite: 3]
        with col_y:
            st.write(f"**Tanggal:** {data_inv['waktu_tgl']}") [cite: 5]
        
        # Tabel Ringkasan
        st.table(pd.DataFrame([data_inv]))
        st.write(f"### Total Bayar: Rp {data_inv['total']:,.0f}") [cite: 8, 9]
        st.write(f"*Terbilang: {terbilang(data_inv['total'])} Rupiah*") [cite: 10, 11]

    # Tombol Download PDF (Sesuai source 1-20)
    pdf_bytes = buat_pdf_custom(data_inv)
    st.download_button(
        label="📥 Download Invoice PDF",
        data=pdf_bytes,
        file_name=f"Invoice_{data_inv['penerima']}.pdf",
        mime="application/pdf"
    )
