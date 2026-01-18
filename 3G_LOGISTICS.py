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
st.set_page_config(page_title="3G Logistics - Generator", page_icon="FAVICON.png", layout="wide")

# CSS ANTI-DOWNLOAD
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# FUNGSI TERBILANG
def format_terbilang(angka):
    if angka == 0: return "-"
    try:
        return num2words(int(angka), lang='id').title() + " Rupiah"
    except: return "-"

# FUNGSI GENERATE PDF
def generate_pdf(data):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # Header Image
    try:
        header = ImageReader("HEADER INVOICE.png")
        c.drawImage(header, 50, height - 120, width=500, preserveAspectRatio=True, mask='auto')
    except: pass

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 150, "INVOICE")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 180, f"CUSTOMER: {data['cust']}")
    c.drawString(50, height - 195, f"NO. INVOICE: {data['inv']}")
    c.drawString(400, height - 180, f"DATE: {data['date']}")

    # Tabel Sederhana
    c.line(50, height - 210, 550, height - 210)
    c.drawString(55, height - 225, f"Description: {data['prod']}")
    c.drawString(55, height - 240, f"Route: {data['ori']} - {data['dest']}")
    c.drawString(55, height - 255, f"Qty/Weight: {data['weight']}")
    c.line(50, height - 265, 550, height - 265)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(400, height - 280, f"TOTAL: Rp {data['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, height - 300, f"Terbilang: {data['said']}")

    # Footer Bank
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 150, "TRANSFER TO :")
    c.setFont("Helvetica", 10)
    c.drawString(50, 135, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, 120, "A/N ADITYA GAMA SAPUTRI")

    c.drawString(400, 150, f"Surabaya, {data['date']}")
    c.drawString(400, 135, "Sincerely,")
    c.drawString(400, 120, "PT. GAMA GEMAH GEMILANG")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, 50, "KELVINITO JAYADI")
    
    c.save()
    buf.seek(0)
    return buf

# 2. LOGIKA NOMOR INVOICE OTOMATIS
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# 3. HALAMAN INPUT
st.title("Sistem Invoice 3G Logistics")

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        cust_name = st.text_input("Customer", value="")
        # Tanggal Pilih Manual (Popup)
        inv_date = st.date_input("Tanggal Invoice", datetime.now())
    with c2:
        no_inv = st.text_input("Nomor Invoice (Otomatis)", value=auto_no_inv)
        load_date = st.date_input("Date of Load", datetime.now())

    st.subheader("Detail Biaya")
    c3, c4 = st.columns(2)
    with c3:
        origin = st.text_input("Origin", "")
        dest = st.text_input("Destination", "")
        prod_desc = st.text_area("Product Description", "")
    with c4:
        weight = st.number_input("Weight / Qty", min_value=0.0, step=0.1)
        price_unit = st.number_input("Harga Satuan (Rp)", min_value=0, step=1000)
        
        # TOTAL OTOMATIS MUNCUL SEBELUM SIMPAN
        total_calc = int(weight * price_unit)
        st.metric("Total Yang Harus Dibayar", f"Rp {total_calc:,.0f}")
        terbilang_calc = format_terbilang(total_calc)
        st.caption(f"Terbilang: {terbilang_calc}")

    submit = st.form_submit_button("Preview & Kunci Data")

# 4. PREVIEW & DOWNLOAD
if submit:
    data_final = {
        "cust": cust_name, "inv": no_inv, "date": inv_date.strftime("%d/%m/%Y"),
        "prod": prod_desc, "ori": origin, "dest": dest,
        "weight": weight, "total": total_calc, "said": terbilang_calc
    }
    
    st.success("Data berhasil dikunci. Silakan download PDF di bawah ini.")
    
    pdf_file = generate_pdf(data_final)
    
    st.download_button(
        label="📥 Download Invoice (PDF)",
        data=pdf_file,
        file_name=f"Invoice_{cust_name}_{no_inv.replace('/','-')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Increment counter untuk nomor berikutnya
    st.session_state.inv_count += 1
