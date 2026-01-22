import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G Logistics System", layout="centered")

def terbilang(n):
    bil = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " belas"
    elif n < 100: return terbilang(n // 10) + " puluh " + terbilang(n % 10)
    elif n < 200: return "seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " ratus " + terbilang(n % 100)
    elif n < 2000: return "seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    return ""

class LogisticsPDF(FPDF):
    def safe_header(self, logo_path):
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 190)
        self.ln(25)

    def invoice_body(self, data):
        # Header Utama
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(190, 7, 'INVOICE TAGIHAN', border=1, ln=1, align='C', fill=True)
        
        # Area Info Nomor (PENTING: Di sini Nomor Resi & Inv Muncul)
        self.set_font('Arial', 'B', 9)
        self.cell(25, 7, " CUSTOMER :", border='L', ln=0)
        self.set_font('Arial', '', 9)
        self.cell(85, 7, f" {data['customer']}", border=0, ln=0)
        self.set_font('Arial', 'B', 9)
        self.cell(80, 7, f"NO. INV : {data['no_inv']} ", border='R', ln=1, align='R')
        
        self.cell(25, 7, " TANGGAL :", border='L', ln=0)
        self.set_font('Arial', '', 9)
        self.cell(85, 7, f" {data['date_now']}", border=0, ln=0)
        self.set_font('Arial', 'B', 9)
        self.cell(80, 7, f"NO. RESI : {data['no_resi']} ", border='R', ln=1, align='R')
        
        # Header Tabel
        self.ln(2)
        self.set_fill_color(26, 99, 175); self.set_text_color(255, 255, 255)
        w = [22, 50, 23, 23, 10, 22, 13, 27] 
        cols = ["Date Load", "Description", "Origin", "Dest", "KOL", "HARGA", "WGT", "TOTAL"]
        for i, col in enumerate(cols):
            self.cell(w[i], 7, col, border=1, align='C', fill=True)
        self.ln()

        # Isi Tabel
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 8)
        y_s = self.get_y()
        self.cell(w[0], 12, data['date_load'], border=1, align='C')
        c_x = self.get_x()
        self.multi_cell(w[1], 6, data['desc'], border=1, align='C')
        y_e = self.get_y()
        h = max(12, y_e - y_s)
        
        self.set_xy(c_x + w[1], y_s)
        self.cell(w[2], h, data['origin'], border=1, align='C')
        self.cell(w[3], h, data['dest'], border=1, align='C')
        self.cell(w[4], h, str(data['kolli']), border=1, align='C')
        self.cell(w[5], h, f"{data['harga']:,}", border=1, align='C')
        self.cell(w[6], h, str(data['weight']), border=1, align='C')
        self.cell(w[7], h, f"{data['total_val']:,}", border=1, align='C')
        
        self.set_y(y_s + h)
        self.set_fill_color(200, 200, 200); self.set_font('Arial', 'B', 8)
        self.cell(sum(w[:-1]), 7, "TOTAL YANG HARUS DIBAYAR", border=1, align='C', fill=True)
        self.cell(w[-1], 7, f"Rp {data['total_val']:,}", border=1, align='C', fill=True)
        self.ln()
        self.set_font('Arial', 'BI', 8)
        self.cell(190, 8, f" Terbilang: # {data['terbilang']} RUPIAH #", border=1, ln=1, align='C')

    def receipt_page(self, data):
        self.add_page()
        self.safe_header("HEADER.png")
        self.set_fill_color(50, 50, 50); self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(190, 8, f"RESI PENGIRIMAN BARANG - {data['no_resi']}", border=1, ln=1, align='C', fill=True)
        
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 10)
        self.ln(5)
        self.cell(95, 6, f"Penerima: {data['customer']}", ln=0)
        self.cell(95, 6, f"No. Invoice: {data['no_inv']}", ln=1, align='R')
        self.ln(5)
        
        # Tabel Resi Singkat
        self.set_font('Arial', 'B', 9)
        w = [30, 80, 40, 20, 20]
        cols = ["Tgl Muat", "Nama Barang", "Rute", "KOL", "Berat"]
        for i, col in enumerate(cols):
            self.cell(w[i], 8, col, border=1, align='C')
        self.ln()
        self.set_font('Arial', '', 9)
        self.cell(w[0], 12, data['date_load'], border=1, align='C')
        self.cell(w[1], 12, data['desc'][:40], border=1, align='C')
        self.cell(w[2], 12, f"{data['origin']} - {data['dest']}", border=1, align='C')
        self.cell(w[3], 12, str(data['kolli']), border=1, align='C')
        self.cell(w[4], 12, str(data['weight']), border=1, align='C')
        self.ln(20)
        
        # Tanda Tangan
        self.cell(63, 5, "Penerima,", ln=0, align='C')
        self.cell(63, 5, "Sopir/Kurir,", ln=0, align='C')
        self.cell(64, 5, "Admin 3G,", ln=1, align='C')
        self.ln(15)
        self.cell(63, 5, "(....................)", ln=0, align='C')
        self.cell(63, 5, "(....................)", ln=0, align='C')
        self.cell(64, 5, "( KELVINITO J. )", ln=1, align='C')

# --- UI STREAMLIT ---
st.title("🚚 3G LOGISTICS - Sistem Otomatis")

if 'inv_3g' not in st.session_state:
    st.session_state.inv_3g = f"3G-INV-{datetime.now().strftime('%y%m%d')}-{random.randint(100,999)}"
    st.session_state.resi_3g = f"3G-RS-{datetime.now().strftime('%y%m%d')}-{random.randint(100,999)}"

with st.form("form_3g"):
    st.subheader(f"No. Invoice: {st.session_state.inv_3g}")
    st.subheader(f"No. Resi: {st.session_state.resi_3g}")
    
    c1, c2 = st.columns(2)
    with c1:
        customer = st.text_input("Nama Customer").upper()
        asal = st.text_input("Kota Asal (Origin)").upper()
        jumlah = st.text_input("Jumlah Kolli", value="1")
    with c2:
        tgl_muat = st.date_input("Tanggal Muat")
        tujuan = st.text_input("Kota Tujuan (Destination)").upper()
        berat = st.number_input("Berat Barang (WGT)", value=1.0)
    
    harga_satuan = st.number_input("Harga per WGT", value=5000)
    deskripsi = st.text_area("Deskripsi Barang").upper()
    total_bayar = int(harga_satuan * berat)
    
    generate_btn = st.form_submit_button("GENERATE PDF (INV + RESI)")

if generate_btn:
    if not customer:
        st.error("Silakan isi nama customer!")
    else:
        final_data = {
            "no_inv": st.session_state.inv_3g,
            "no_resi": st.session_state.resi_3g,
            "customer": customer, "date_now": datetime.now().strftime("%d/%m/%Y"),
            "date_load": tgl_muat.strftime("%d/%m/%y"), "desc": deskripsi,
            "origin": asal, "dest": tujuan, "kolli": jumlah, 
            "harga": harga_satuan, "weight": berat, "total_val": total_bayar,
            "terbilang": terbilang(total_bayar).upper()
        }

        pdf = LogisticsPDF()
        # Halaman 1
        pdf.add_page()
        pdf.safe_header("HEADER.png")
        pdf.invoice_body(final_data)
        # Halaman 2 (RESI)
        pdf.receipt_page(final_data)

        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, bytearray): pdf_bytes = bytes(pdf_bytes)

        st.success("Berhasil! Nomor Resi telah digabungkan ke dalam PDF.")
        st.download_button(
            label="📥 DOWNLOAD PDF LENGKAP",
            data=pdf_bytes,
            file_name=f"3G_{st.session_state.inv_3g}.pdf",
            mime="application/pdf"
        )
