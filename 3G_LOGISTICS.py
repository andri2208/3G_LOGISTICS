import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- KONFIGURASI ---
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec" 

# Fungsi bantu untuk angka menjadi teks (Terbilang)
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

def buat_pdf_custom(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Perusahaan [cite: 1, 2]
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 7, "PT. GAMA GEMAH GEMILANG", ln=True)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(130, 4, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik, Jawa Timur. Telp 031-79973432")
    pdf.ln(5)
    
    # Info Customer [cite: 3, 4, 5]
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
    pdf.cell(20, 10, f"{data['harga']:,.0f}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C')
    
    # Total & Terbilang [cite: 9, 10, 11]
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,.0f}", 1, 1, 'C', True)
    
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(190, 10, f"Terbilang: {terbilang(data['total'])} Rupiah", ln=True)

    # Info Bank [cite: 12, 13, 14, 15]
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA)", ln=True)
    pdf.cell(190, 5, "6720422334", ln=True)
    pdf.cell(190, 5, "A/N ADITYA GAMA SAPUTRI", ln=True)
    
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

# --- ANTARMUKA STREAMLIT ---
st.title("Sistem Invoice PT. GAMA GEMAH GEMILANG")

if 'inv_data' not in st.session_state: st.session_state.inv_data = None

with st.form("form_inv"):
    cust = st.text_input("Customer Name")
    desc = st.text_input("Product Description")
    c1, c2, c3, c4 = st.columns(4)
    with c1: ori = st.text_input("Origin")
    with c2: dest = st.text_input("Destination")
    with c3: hrg = st.number_input("Harga", value=8500)
    with c4: wgt = st.number_input("Weight (Kg)", value=1)
    
    if st.form_submit_button("Proses Invoice"):
        st.session_state.inv_data = {
            "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
            "penerima": cust,
            "deskripsi": desc,
            "asal": ori,
            "tujuan": dest,
            "harga": hrg,
            "berat": wgt,
            "total": hrg * wgt
        }
        requests.post(API_URL, json=st.session_state.inv_data)

if st.session_state.inv_data:
    pdf = buat_pdf_custom(st.session_state.inv_data)
    st.download_button("📥 Download Invoice PDF", pdf, f"Invoice_{st.session_state.inv_data['penerima']}.pdf", "application/pdf")
