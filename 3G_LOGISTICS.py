import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI API & HALAMAN ---
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS - Invoice System",
    page_icon="FAVICON.png", 
    layout="wide"
)

# --- FUNGSI BARU: GENERATE NOMOR INVOICE ---
def generate_invoice_number():
    # Format: INV/YYYYMMDD/Urutan
    # Untuk sementara kita gunakan timestamp unik agar selalu berbeda setiap kali klik
    # Jika ingin urutan 001, 002, dst, sistem harus membaca database terlebih dahulu
    now = datetime.now()
    return f"INV/{now.strftime('%Y%m%d')}/{now.strftime('%H%M%S')}"

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

# --- 3. FUNGSI PDF (DENGAN NOMOR INVOICE) ---
def buat_pdf_custom(data):
    pdf = FPDF()
    pdf.add_page()
    
    if os.path.exists("HEADER INVOICE.png"):
        pdf.image("HEADER INVOICE.png", x=10, y=8, w=190)
        pdf.ln(35)
    else:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 7, "PT. GAMA GEMAH GEMILANG", ln=True)
        pdf.ln(10)
    
    # Header Info & Nomor Invoice
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 6, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 6, "INVOICE", 0, 1, 'R')
    
    pdf.set_font("Arial", size=9)
    pdf.cell(100, 6, f"No: {data['no_inv']}", 0) # Menampilkan Nomor Invoice
    pdf.cell(90, 6, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(5)
    
    # Tabel
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(25, 10, "Date of Load", 1, 0, 'C', True)
    pdf.cell(50, 10, "Product Description", 1, 0, 'C', True)
    pdf.cell(20, 10, "Origin", 1, 0, 'C', True)
    pdf.cell(25, 10, "Destination", 1, 0, 'C', True)
    pdf.cell(20, 10, "Harga", 1, 0, 'C', True)
    pdf.cell(20, 10, "Weight", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 10, data['waktu_tgl'], 1, 0, 'C')
    pdf.cell(50, 10, data['deskripsi'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, data['asal'].upper(), 1, 0, 'C')
    pdf.cell(25, 10, data['tujuan'].upper(), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['harga']:,}", 1, 0, 'C')
    pdf.cell(20, 10, f"{data['berat']} Kg", 1, 0, 'C')
    pdf.cell(30, 10, f"Rp {data['total']:,}", 1, 1, 'C')
    
    # Total & Footer Rekening
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])} Rupiah")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA) - 6720422334 - A/N ADITYA GAMA SAPUTRI", ln=True)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(190, 5, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200", ln=True)
    
    # Tanda Tangan
    pdf.ln(10)
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    
    y_ttd = pdf.get_y()
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=145, y=y_ttd, w=35)
        pdf.ln(20)
    else:
        pdf.ln(20)
        
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. ANTARMUKA WEB ---
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

st.title("GENERATOR INVOICE 3G")

if 'preview_data' not in st.session_state:
    st.session_state.preview_data = None

def reset_form():
    st.session_state.preview_data = None

with st.form("main_form", clear_on_submit=True):
    cust = st.text_input("Nama Customer")
    prod = st.text_input("Deskripsi Barang")
    c1, c2, c3, c4 = st.columns(4)
    with c1: ori = st.text_input("Origin")
    with c2: dest = st.text_input("Destination")
    with c3: hrg = st.number_input("Harga", value=8500)
    with c4: wgt = st.number_input("Berat (Kg)", value=1)
    
    if st.form_submit_button("Proses & Preview"):
        if not cust:
            st.error("Nama Customer harus diisi!")
        else:
            # Generate Nomor Invoice Baru
            inv_no = generate_invoice_number()
            
            st.session_state.preview_data = {
                "no_inv": inv_no,
                "waktu_tgl": datetime.now().strftime("%d-%b-%y"),
                "penerima": cust,
                "deskripsi": prod,
                "asal": ori,
                "tujuan": dest,
                "harga": hrg,
                "berat": wgt,
                "total": int(hrg * wgt)
            }
            try:
                requests.post(API_URL, json=st.session_state.preview_data)
            except:
                pass

# --- 5. PREVIEW & DOWNLOAD ---
if st.session_state.preview_data:
    d = st.session_state.preview_data
    st.divider()
    
    c_head, c_res = st.columns([0.8, 0.2])
    with c_head:
        st.subheader(f"🔍 Preview Invoice: {d['no_inv']}")
    with c_res:
        st.button("🗑️ Reset", on_click=reset_form)
    
    with st.container(border=True):
        st.write(f"**No Invoice:** {d['no_inv']}")
        st.write(f"**Customer:** {d['penerima']} | **Tanggal:** {d['waktu_tgl']}")
        st.table(pd.DataFrame([d]))
        st.write(f"### Total Bayar: Rp {d['total']:,}")

    pdf_bytes = buat_pdf_custom(d)
    st.download_button(
        label="📥 Download Invoice PDF",
        data=pdf_bytes,
        file_name=f"Invoice_{d['penerima']}_{d['no_inv']}.pdf",
        mime="application/pdf"
    )
