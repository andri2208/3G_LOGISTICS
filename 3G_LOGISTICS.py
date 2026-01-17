import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI ---
# Pastikan URL Web App Apps Script kamu sudah benar
API_URL = "https://script.google.com/macros/s/AKfycbzV9hmyRqF5JErjh7aILmUTWbwVchR8a9MrKbZSzUE8FTuP2uYVlYEadxILqav8wbPn/exec" 

try:
    from PIL import Image
    favicon = Image.open("FAVICON.png")
    st.set_page_config(page_title="3G LOGISTICS", page_icon=favicon, layout="wide")
except:
    st.set_page_config(page_title="3G LOGISTICS", page_icon="🚚", layout="wide")

# --- 2. FUNGSI CETAK PDF SESUAI CONTOH ---
def buat_pdf_custom(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Perusahaan
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 7, "PT. GAMA GEMAH GEMILANG", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(140, 5, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik, Jawa Timur. Telp 031-79973432")
    pdf.ln(5)
    
    # Judul Invoice & Info Customer
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 7, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 7, "INVOICE", 0, 1, 'R')
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 7, "", 0)
    pdf.cell(90, 7, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(5)
    
    # Tabel Header
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(25, 10, "Date of Load", 1, 0, 'C', True)
    pdf.cell(50, 10, "Product Description", 1, 0, 'C', True)
    pdf.cell(20, 10, "Origin", 1, 0, 'C', True)
    pdf.cell(20, 10, "Destination", 1, 0, 'C', True)
    pdf.cell(25, 10, "Harga/Kg", 1, 0, 'C', True)
    pdf.cell(20, 10, "Weight", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    
    # Tabel Isi
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(50, 10, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(25, 10, f"Rp {data['harga']:,.0f}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C')
    
    pdf.ln(5)
    # Total Bayar
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C', True)
    
    # Informasi Pembayaran
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA)", ln=True)
    pdf.cell(190, 5, "6720422334", ln=True)
    pdf.cell(190, 5, "A/N ADITYA GAMA SAPUTRI", ln=True)
    
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

# --- 3. MENU UTAMA ---
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

menu = st.sidebar.radio("Navigasi", ["🏠 Dashboard", "📝 Buat Invoice Baru"])

if menu == "📝 Buat Invoice Baru":
    st.subheader("Form Input Invoice PT. GAMA GEMAH GEMILANG")
    with st.form("invoice_form"):
        penerima = st.text_input("Nama Customer (Penerima)")
        deskripsi = st.text_input("Deskripsi Barang (Contoh: Alat Tambang)")
        
        col1, col2 = st.columns(2)
        with col1:
            asal = st.text_input("Origin (Asal)")
            harga = st.number_input("Harga per Kg", min_value=0, value=8500)
        with col2:
            tujuan = st.text_input("Destination (Tujuan)")
            berat = st.number_input("Weight (Kg)", min_value=0, value=1)
            
        submit = st.form_submit_button("Simpan & Cetak PDF")
        
        if submit:
            total_bayar = harga * berat
            tgl_skrg = datetime.now().strftime("%d-%b-%y")
            
            payload = {
                "waktu_tgl": tgl_skrg,
                "penerima": penerima,
                "deskripsi": deskripsi,
                "asal": asal,
                "tujuan": tujuan,
                "harga": harga,
                "berat": berat,
                "total": total_bayar
            }
            
            # Simpan ke Google Sheets (Opsional)
            requests.post(API_URL, json=payload)
            
            st.success("Invoice Berhasil Dibuat!")
            pdf_out = buat_pdf_custom(payload)
            st.download_button(label="📥 Download Invoice PDF", data=pdf_out, file_name=f"Invoice_{penerima}.pdf", mime="application/pdf")
