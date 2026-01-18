import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI API ---
# Ganti dengan URL Google Apps Script kamu
API_URL = "URL_WEB_APP_KAMU"

st.set_page_config(page_title="3G LOGISTICS - Invoice System", layout="wide")

# --- 2. FUNGSI TERBILANG ---
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
    
    # Header Perusahaan
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 7, "PT. GAMA GEMAH GEMILANG", ln=True)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(130, 4, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik, Jawa Timur. Telp 031-79973432")
    pdf.ln(5)
    
    # Info Customer
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 6, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 6, "INVOICE", 0, 1, 'R')
    pdf.set_font("Arial", size=9)
    pdf.cell(100, 6, "", 0)
    pdf.cell(90, 6, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(5)
    
    # Tabel Header
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    headers = ["Date of Load", "Product Description", "Origin", "Destination", "Harga", "Weight", "Total"]
    widths = [25, 55, 20, 20, 20, 20, 30]
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1, 0, 'C', True)
    pdf.ln()
    
    # Tabel Isi
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(55, 10, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['harga']:,}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,}", 1, 1, 'C')
    
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(50, 10, f"Rp {data['total']:,}", 1, 1, 'C', True)
    
    pdf.ln(2)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 5, f"Terbilang: {terbilang(data['total'])} Rupiah")

    # Info Bank
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA)", ln=True)
    pdf.cell(190, 5, "6720422334", ln=True)
    pdf.cell(190, 5, "A/N ADITYA GAMA SAPUTRI", ln=True)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(190, 5, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200", ln=True)
    
    # Tanda Tangan
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

# --- 4. TAMPILAN UTAMA ---
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

st.title("📝 Buat Invoice Baru")

if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None

# FORM INPUT
with st.form("form_invoice_3g"):
    cust_name = st.text_input("Customer Name (Penerima)")
    prod_desc = st.text_input("Product Description")
    c1, c2, c3, c4 = st.columns(4)
    with c1: origin = st.text_input("Origin")
    with c2: destination = st.text_input("Destination")
    with c3: price = st.number_input("Harga", value=8500)
    with c4: weight = st.number_input("Weight (Kg)", value=1)
    
    submitted = st.form_submit_button("Lihat Preview & Simpan")

    if submitted:
        if not cust_name or not prod_desc:
            st.error("Nama Customer dan Deskripsi wajib diisi!")
        else:
            st.session_state.preview_data = {
                "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                "penerima": cust_name,
                "deskripsi": prod_desc,
                "asal": origin,
                "tujuan": destination,
                "harga": price,
                "berat": weight,
                "total": price * weight
            }
            try:
                requests.post(API_URL, json=st.session_state.preview_data)
            except:
                pass

# --- 5. PREVIEW & DOWNLOAD ---
if st.session_state.preview_data is not None:
    d = st.session_state.preview_data
    st.divider()
    st.subheader("🔍 Preview Invoice")
    
    with st.container(border=True):
        st.write(f"**PT. GAMA GEMAH GEMILANG**")
        col_1, col_2 = st.columns(2)
        with col_1: st.write(f"**Customer:** {d['penerima']}")
        with col_2: st.write(f"**Tanggal:** {d['waktu_tgl']}")
        
        st.table(pd.DataFrame([d]))
        st.write(f"### Total Bayar: Rp {d['total']:,}")
        st.write(f"*Terbilang: {terbilang(d['total'])} Rupiah*")

    pdf_bytes = buat_pdf_custom(d)
    st.download_button(
        label="📥 Download Invoice PDF",
        data=pdf_bytes,
        file_name=f"Invoice_{d['penerima']}.pdf",
        mime="application/pdf"
    )
