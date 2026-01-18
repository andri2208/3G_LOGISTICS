import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
from num2words import num2words
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Invoice System", page_icon="FAVICON.png", layout="wide")

# CSS ANTI-DOWNLOAD
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# FUNGSI GENERATE PDF (Instan)
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # Header Image
    try:
        header = ImageReader("HEADER INVOICE.png")
        c.drawImage(header, 50, height - 100, width=500, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG") [cite: 1, 18]

    # Info Invoice
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 130, "INVOICE") [cite: 4, 21]
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"CUSTOMER: {d['cust']}") [cite: 3, 20]
    c.drawString(450, height - 160, f"DATE: {d['date']}") [cite: 13, 22]
    c.drawString(50, height - 175, f"NO. INVOICE: {d['inv']}")

    # Garis Tabel
    c.line(50, height - 190, 550, height - 190)
    c.setFont("Helvetica-Bold", 9)
    headers = ["Date of Load", "Description", "Origin", "Dest", "Qty", "Total"]
    x_pos = [55, 130, 250, 320, 390, 470]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], height - 205, h)
    c.line(50, height - 210, 550, height - 210)

    # Isi Tabel
    c.setFont("Helvetica", 9)
    c.drawString(55, height - 225, d['load']) [cite: 5, 23]
    c.drawString(130, height - 225, d['prod'][:25]) [cite: 5, 23]
    c.drawString(250, height - 225, d['ori']) [cite: 5, 23]
    c.drawString(320, height - 225, d['dest']) [cite: 5, 23]
    c.drawString(390, height - 225, f"{d['weight']} {d['kolli']}") [cite: 23]
    c.drawString(470, height - 225, f"Rp {d['total']:,.0f}") [cite: 5, 23]

    # Total & Terbilang
    c.line(50, height - 240, 550, height - 240)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(300, height - 255, "YANG HARUS DI BAYAR") [cite: 5, 26]
    c.drawString(470, height - 255, f"Rp {d['total']:,.0f}") [cite: 5, 25]
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, height - 275, f"Terbilang: {d['said']}") [cite: 5, 27]

    # Footer Bank
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 150, "TRANSFER TO :") [cite: 7, 29]
    c.setFont("Helvetica", 10)
    c.drawString(50, 135, "Bank Central Asia (BCA) - 6720422334") [cite: 8, 9, 30, 31]
    c.drawString(50, 120, "A/N ADITYA GAMA SAPUTRI") [cite: 10, 32]
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 105, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200") [cite: 12, 33]

    # Tanda Tangan
    c.setFont("Helvetica", 10)
    c.drawString(400, 150, f"Surabaya, {d['date']}") [cite: 13, 22]
    c.drawString(400, 135, "Sincerely,") [cite: 14, 34]
    c.drawString(400, 120, "PT. GAMA GEMAH GEMILANG") [cite: 15, 35]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, 60, "KELVINITO JAYADI") [cite: 16, 36]
    c.drawString(400, 48, "DIREKTUR") [cite: 17, 37]
    
    c.save()
    buf.seek(0)
    return buf

# LOGIKA NOMOR INVOICE
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# SISTEM TAB
tab_input, tab_preview = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_input:
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        cust_name = c1.text_input("Customer", placeholder="Contoh: BAPAK ANDI") [cite: 20]
        inv_date = c1.date_input("Tanggal Invoice", datetime.now())
        no_inv = c2.text_input("Nomor Invoice", value=auto_no_inv)
        load_date = c2.date_input("Date of Load", datetime.now())

        c3, c4 = st.columns(2)
        prod_desc = c3.text_area("Product Description") [cite: 23]
        origin = c3.text_input("Origin", value="SBY") [cite: 23]
        dest = c3.text_input("Destination", value="MEDAN") [cite: 23]
        kolli = c4.text_input("Satuan (Kolli/Unit/Kg)", value="Kg") [cite: 23]
        weight = c4.number_input("Berat/Jumlah", min_value=0.0) [cite: 23]
        price_kg = c4.number_input("Harga Satuan (Rp)", min_value=0) [cite: 23]
        
        total_calc = int(weight * price_kg)
        terbilang_calc = format_terbilang(total_calc)
        
        if st.form_submit_button("Simpan Data"):
            st.session_state.data = {
                "cust": cust_name, "inv": no_inv, "date": inv_date.strftime("%d/%m/%Y"),
                "load": load_date.strftime("%d-%b-%y"), "prod": prod_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price_kg,
                "total": total_calc, "said": terbilang_calc
            }
            st.success("Data Siap! Silakan pindah ke Tab Preview.")

with tab_preview:
    if 'data' in st.session_state:
        d = st.session_state.data
        
        # Tampilan layar
        st.subheader("Preview Invoice")
        st.write(f"**Customer:** {d['cust']} | **Total:** Rp {d['total']:,.0f}") [cite: 20, 25]
        
        # Proses PDF Instan
        pdf_file = generate_pdf(d)
        
        st.download_button(
            label="📥 Download PDF Sekarang",
            data=pdf_file,
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Isi data di tab Input terlebih dahulu.")
