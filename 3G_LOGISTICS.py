import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G Logistics Billing", layout="centered")

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

class InvoicePDF(FPDF):
    def safe_header(self, logo_path):
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 190)
        self.ln(25)

    def invoice_body(self, data):
        # Lebar kolom yang sudah dihitung agar pas 190mm dan tidak bertumpuk
        # [Date, Desc, Ori, Dest, Kol, Harga, Wgt, Total]
        w = [22, 50, 23, 23, 10, 22, 13, 27] 
        
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 10)
        self.cell(190, 6, 'INVOICE', border=1, ln=1, align='C', fill=True)
        
        self.set_font('Arial', 'B', 9)
        self.cell(25, 7, " CUSTOMER :", border='L', ln=0)
        self.set_font('Arial', '', 9)
        self.cell(95, 7, f" {data['customer']}", border=0, ln=0)
        self.cell(70, 7, f"DATE : {data['date_now']} ", border='R', ln=1, align='R')
        
        # Header Tabel
        self.set_fill_color(26, 99, 175); self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        cols = ["Date Load", "Description", "Origin", "Dest", "KOL", "HARGA", "WGT", "TOTAL"]
        for i, col in enumerate(cols):
            self.cell(w[i], 7, col, border=1, align='C', fill=True)
        self.ln()

        # Isi Tabel
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 8)
        y_start = self.get_y()
        
        # Baris pertama (kiri)
        self.cell(w[0], 12, data['date_load'], border=1, align='C')
        
        # Description (MultiCell agar rapi)
        curr_x = self.get_x()
        self.multi_cell(w[1], 6, data['desc'], border=1, align='C')
        y_end = self.get_y()
        h_cell = max(12, y_end - y_start)
        
        # Kolom sisa mengikuti tinggi h_cell
        self.set_xy(curr_x + w[1], y_start)
        self.cell(w[2], h_cell, data['origin'], border=1, align='C')
        self.cell(w[3], h_cell, data['dest'], border=1, align='C')
        self.cell(w[4], h_cell, str(data['kolli']), border=1, align='C')
        self.cell(w[5], h_cell, f"{data['harga']:,}", border=1, align='C')
        self.cell(w[6], h_cell, str(data['weight']), border=1, align='C')
        self.cell(w[7], h_cell, f"{data['total_val']:,}", border=1, align='C')
        
        # Footer Tabel
        self.set_y(y_start + h_cell)
        self.set_fill_color(200, 200, 200); self.set_font('Arial', 'B', 8)
        self.cell(sum(w[:-1]), 7, "YANG HARUS DI BAYAR", border=1, align='C', fill=True)
        self.cell(w[-1], 7, f"Rp {data['total_val']:,}", border=1, align='C', fill=True)
        self.ln()
        
        self.set_fill_color(230, 230, 230)
        self.cell(20, 8, " Terbilang :", border='LB', fill=True)
        self.set_font('Arial', 'BI', 8)
        self.cell(170, 8, f" # {data['terbilang']} RUPIAH #", border='RB', ln=1, fill=True, align='C')

    def safe_footer(self, stempel_path):
        self.ln(5)
        y_f = self.get_y()
        self.set_font('Arial', 'B', 8)
        self.cell(0, 5, "TRANSFER TO : BCA / 6720422334 / A/N ADITYA GAMA SAPUTRI", ln=1)
        self.set_font('Arial', 'BI', 8)
        self.cell(0, 4, "NB : Mohon konfirmasi ke Finance 082179799200 setelah transfer", ln=1)
        
        self.set_xy(145, y_f)
        self.set_font('Arial', '', 9)
        self.cell(45, 5, "Sincerely,", ln=1, align='C')
        if os.path.exists(stempel_path):
            self.image(stempel_path, 148, self.get_y() - 2, 35)
        self.ln(15)
        self.set_x(145)
        self.set_font('Arial', 'BU', 9)
        self.cell(45, 5, "KELVINITO JAYADI", ln=1, align='C')

# --- FRONTEND STREAMLIT ---
st.title("🚚 PT. GAMA GEMAH GEMILANG")

if 'inv_no' not in st.session_state:
    st.session_state.inv_no = f"INV/{datetime.now().strftime('%Y%m%d')}/{random.randint(100,999)}"

with st.form("inv_form"):
    col1, col2 = st.columns(2)
    with col1:
        cust = st.text_input("Customer", value="BAPAK ANDI").upper()
        ori = st.text_input("Origin", value="SBY").upper()
        kol = st.text_input("KOLLI")
    with col2:
        d_load = st.date_input("Date Load")
        dest = st.text_input("Destination", value="MEDAN").upper()
        wgt = st.number_input("Weight", value=290.0)
    
    hrg = st.number_input("Harga", value=8500)
    desc = st.text_area("Description", value="SATU SET ALAT TAMBANG").upper()
    total = int(hrg * wgt)
    
    st.write(f"### Total: Rp {total:,}")
    generate = st.form_submit_button("SIAPKAN DOWNLOAD")

if generate:
    payload = {
        "customer": cust, "date_now": datetime.now().strftime("%d/%m/%Y"),
        "date_load": d_load.strftime("%d-%m-%y"), "desc": desc,
        "origin": ori, "dest": dest, "kolli": kol, "harga": hrg,
        "weight": wgt, "total_val": total, "terbilang": terbilang(total).upper()
    }

    pdf = InvoicePDF()
    pdf.add_page()
    pdf.safe_header("HEADER.png")
    pdf.invoice_body(payload)
    pdf.safe_footer("STEMPEL.png")
    
    # KONVERSI AMAN KE BYTES
    pdf_output = pdf.output()
    pdf_bytes = bytes(pdf_output) if isinstance(pdf_output, bytearray) else pdf_output

    st.success("✅ File PDF Berhasil Dibuat!")
    st.download_button(
    label="📥 DOWNLOAD PDF",
    data=pdf_bytes,
    file_name=f"Invoice_{cust}.pdf",
    mime="application/pdf"
)
