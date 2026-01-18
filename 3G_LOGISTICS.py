import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. KONFIGURASI KEAMANAN & API ---
PASSWORD_AKSES = "3G2026" # <--- SILAKAN GANTI PASSWORD ANDA DI SINI
API_URL = "https://script.google.com/macros/s/AKfycbw7baLr4AgAxGyt6uQQk-G5lnVExcbTd-UMZdY9rwkCSbaZlvYPqLCX8-QENVebKa13/exec"

st.set_page_config(
    page_title="3G LOGISTICS - Invoice System",
    page_icon="FAVICON.png", 
    layout="wide"
)

# --- 2. SISTEM LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Akses Terbatas - 3G LOGISTICS")
    pwd_input = st.text_input("Masukkan Password Akses:", type="password")
    if st.button("Login"):
        if pwd_input == PASSWORD_AKSES:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password Salah! Silakan hubungi admin.")
    st.stop() # Menghentikan aplikasi jika belum login

# --- 3. FUNGSI-FUNGSI PENDUKUNG ---

def generate_invoice_number():
    now = datetime.now()
    return f"INV/{now.strftime('%Y%m%d')}/{now.strftime('%H%M%S')}"

def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    hasil = ""
    n = int(n)
    if n == 0: return "Rupiah"
    if n < 12: hasil = bilangan[n]
    elif n < 20: hasil = terbilang(n - 10).replace(" Rupiah", "") + " Belas"
    elif n < 100: hasil = terbilang(n // 10).replace(" Rupiah", "") + " Puluh " + terbilang(n % 10).replace(" Rupiah", "")
    elif n < 200: hasil = "Seratus " + terbilang(n - 100).replace(" Rupiah", "")
    elif n < 1000: hasil = terbilang(n // 100).replace(" Rupiah", "") + " Ratus " + terbilang(n % 100).replace(" Rupiah", "")
    elif n < 2000: hasil = "Seribu " + terbilang(n - 1000).replace(" Rupiah", "")
    elif n < 1000000: hasil = terbilang(n // 1000).replace(" Rupiah", "") + " Ribu " + terbilang(n % 1000).replace(" Rupiah", "")
    elif n < 1000000000: hasil = terbilang(n // 1000000).replace(" Rupiah", "") + " Juta " + terbilang(n % 1000000).replace(" Rupiah", "")
    return hasil.strip() + " Rupiah"

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
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 6, f"CUSTOMER: {data['penerima'].upper()}", 0)
    pdf.cell(90, 6, "INVOICE", 0, 1, 'R')
    pdf.set_font("Arial", size=9)
    pdf.cell(100, 6, f"No: {data['no_inv']}", 0)
    pdf.cell(90, 6, f"DATE: {data['waktu_tgl']}", 0, 1, 'R')
    pdf.ln(5)
    
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
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "YANG HARUS DI BAYAR", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {data['total']:,}", 1, 1, 'C', True)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(190, 8, f"Terbilang: {terbilang(data['total'])}")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 5, "TRANSFER TO :", ln=True)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "Bank Central Asia (BCA) - 6720422334 - A/N ADITYA GAMA SAPUTRI", ln=True)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(190, 5, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200", ln=True)
    
    pdf.ln(10)
    pdf.cell(130, 5, "Sincerely,", 0, 1, 'R')
    y_ttd = pdf.get_y()
    if os.path.exists("STEMPEL TANDA TANGAN.png"):
        pdf.image("STEMPEL TANDA TANGAN.png", x=145, y=y_ttd, w=35)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 5, "KELVINITO JAYADI", 0, 1, 'R')
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, "DIREKTUR", 0, 1, 'R')

    return pdf.output(dest='S').encode('latin-1')

# --- 4. TAMPILAN UTAMA (SETELAH LOGIN) ---
if os.path.exists("HEADER INVOICE.png"):
    st.image("HEADER INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📝 Buat Invoice", "📊 Riwayat Invoice"])

with tab1:
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None

    with st.form("main_form", clear_on_submit=True):
        st.subheader("Data Pengiriman Baru")
        cust = st.text_input("Nama Customer *")
        prod = st.text_input("Deskripsi Barang *")
        c1, c2, c3, c4 = st.columns(4)
        with c1: ori = st.text_input("Origin *")
        with c2: dest = st.text_input("Destination *")
        with c3: hrg = st.number_input("Harga *", min_value=0, value=0)
        with c4: wgt = st.number_input("Berat (Kg) *", min_value=0.0, value=0.0)
        
        btn_proses = st.form_submit_button("Proses & Simpan")

        if btn_proses:
            if not cust.strip() or not prod.strip() or not ori.strip() or not dest.strip() or hrg <= 0 or wgt <= 0:
                st.warning("⚠️ LENGKAPI SEMUA DATA! Kolom bertanda * wajib diisi dengan benar.")
            else:
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
                    st.success(f"✅ Data {inv_no} Berhasil Disimpan!")
                    st.balloons()
                except:
                    st.error("❌ Gagal mengirim ke Google Sheets.")

    if st.session_state.preview_data:
        d = st.session_state.preview_data
        st.divider()
        col1, col2 = st.columns([0.8, 0.2])
        col1.subheader(f"🔍 Preview: {d['no_inv']}")
        if col2.button("🗑️ Tutup Preview"):
            st.session_state.preview_data = None
            st.rerun()
        
        with st.container(border=True):
            st.table(pd.DataFrame([d]))
            st.write(f"**Terbilang:** {terbilang(d['total'])}")

        pdf_bytes = buat_pdf_custom(d)
        st.download_button(label="📥 Download Invoice PDF", data=pdf_bytes, 
                           file_name=f"Invoice_{d['penerima']}_{d['no_inv']}.pdf", mime="application/pdf")

with tab2:
    st.subheader("Database Invoice")
    if st.button("🔄 Refresh Data Database"):
        try:
            res = requests.get(API_URL)
            all_rows = res.json()
            if len(all_rows) > 1:
                df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
                st.dataframe(df.iloc[::-1], use_container_width=True)
            else:
                st.info("Database kosong.")
        except:
            st.error("Gagal memuat data.")

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

