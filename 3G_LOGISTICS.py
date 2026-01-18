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

# FUNGSI GENERATE PDF
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    try:
        header = ImageReader("HEADER INVOICE.png")
        c.drawImage(header, 50, height - 100, width=500, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG") [cite: 1, 18]

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 130, "INVOICE") [cite: 4, 21]
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"CUSTOMER: {d['cust']}") [cite: 3, 20]
    c.drawString(430, height - 160, f"DATE: {d['date']}") [cite: 13, 22]
    c.drawString(50, height - 175, f"NO. INVOICE: {d['inv']}")

    # Tabel
    c.line(50, height - 190, 550, height - 190)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(55, height - 205, "Date of Load") [cite: 5, 23]
    c.drawString(130, height - 205, "Description") [cite: 5, 23]
    c.drawString(260, height - 205, "Origin") [cite: 5, 23]
    c.drawString(320, height - 205, "Dest") [cite: 5, 23]
    c.drawString(380, height - 205, "Qty") [cite: 5, 23]
    c.drawString(430, height - 205, "Harga/Kg") [cite: 23]
    c.drawString(500, height - 205, "Total")
    c.line(50, height - 210, 550, height - 210)

    # Isi Tabel
    c.setFont("Helvetica", 8)
    c.drawString(55, height - 225, d['load']) [cite: 5, 23]
    c.drawString(130, height - 225, d['prod'][:30]) [cite: 5, 23]
    c.drawString(260, height - 225, d['ori']) [cite: 5, 23]
    c.drawString(320, height - 225, d['dest']) [cite: 5, 23]
    c.drawString(380, height - 225, f"{d['weight']} {d['kolli']}") [cite: 23]
    c.drawString(430, height - 225, f"Rp {d['price']:,.0f}") [cite: 23]
    c.drawString(500, height - 225, f"Rp {d['total']:,.0f}") [cite: 5, 23]

    # Footer
    c.line(50, height - 240, 550, height - 240)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, height - 255, "YANG HARUS DI BAYAR") [cite: 5, 26]
    c.drawString(480, height - 255, f"Rp {d['total']:,.0f}") [cite: 5, 24, 25]
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, height - 275, f"Terbilang: {d['said']}") [cite: 5, 27, 28]

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 150, "TRANSFER TO :") [cite: 7, 29]
    c.setFont("Helvetica", 9)
    c.drawString(50, 135, "Bank Central Asia (BCA) - 6720422334") [cite: 8, 9, 30, 31]
    c.drawString(50, 120, "A/N ADITYA GAMA SAPUTRI") [cite: 10, 32]
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 105, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200") [cite: 33]

    c.setFont("Helvetica", 10)
    c.drawString(400, 150, f"Surabaya, {d['date']}") [cite: 13, 22]
    c.drawString(400, 135, "Sincerely,") [cite: 14, 34]
    c.drawString(400, 120, "PT. GAMA GEMAH GEMILANG") [cite: 1, 15, 18, 35]
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
    with st.form("invoice_form"):
        col_a, col_b = st.columns(2)
        cust_input = col_a.text_input("Customer", placeholder="Contoh: BAPAK ANDI") [cite: 20]
        date_input = col_a.date_input("Tanggal Invoice", datetime.now()) [cite: 22]
        inv_no_input = col_b.text_input("Nomor Invoice", value=auto_no_inv)
        load_date_input = col_b.date_input("Date of Load", datetime.now()) [cite: 5, 23]

        col_c, col_d = st.columns(2)
        prod_input = col_c.text_area("Product Description") [cite: 5, 23]
        ori_input = col_c.text_input("Origin", value="SBY") [cite: 23]
        dest_input = col_c.text_input("Destination", value="MEDAN") [cite: 23]
        
        unit_input = col_d.text_input("Satuan (Kolli/Unit)", value="Kg") [cite: 23]
        weight_input = col_d.number_input("Berat/Jumlah", min_value=0.0) [cite: 23]
        price_input = col_d.number_input("Harga Satuan (Rp)", min_value=0) [cite: 23]
        
        total_val = int(weight_input * price_input)
        terbilang_val = format_terbilang(total_val)
        
        if st.form_submit_button("Simpan & Siapkan PDF"):
            st.session_state.data = {
                "cust": cust_input, "inv": inv_no_input, "date": date_input.strftime("%d/%m/%Y"),
                "load": load_date_input.strftime("%d-%b-%y"), "prod": prod_input, "ori": ori_input,
                "dest": dest_input, "kolli": unit_input, "weight": weight_input, "price": price_input,
                "total": total_val, "said": terbilang_val
            }
            st.success("Data berhasil disimpan! Klik Tab 'Preview & Download'.")

with tab_preview:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.subheader("Konfirmasi Invoice")
        st.write(f"**Customer:** {d['cust']} | **Total:** Rp {d['total']:,.0f}") [cite: 20, 24, 25]
        
        final_pdf = generate_pdf(d)
        
        st.download_button(
            label="📥 Download PDF Sekarang",
            data=final_pdf,
            file_name=f"Invoice_{d['cust']}_{d['inv'].replace('/','-')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Silakan isi data di tab 'Input Data' terlebih dahulu.")
