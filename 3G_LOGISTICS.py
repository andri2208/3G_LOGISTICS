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

# CSS ANTI-DOWNLOAD & PROTEKSI
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

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
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 130, "INVOICE")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"CUSTOMER: {d['cust']}")
    c.drawString(430, height - 160, f"DATE: {d['date']}")
    c.drawString(50, height - 175, f"NO. INVOICE: {d['inv']}")

    # Tabel
    c.line(50, height - 190, 550, height - 190)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(55, height - 205, "Date of Load")
    c.drawString(130, height - 205, "Product Description")
    c.drawString(260, height - 205, "Origin")
    c.drawString(310, height - 205, "Dest")
    c.drawString(360, height - 205, "Kolli")
    c.drawString(410, height - 205, "Harga/Kg")
    c.drawString(470, height - 205, "Weight")
    c.drawString(515, height - 205, "Total")
    c.line(50, height - 210, 550, height - 210)

    # Isi Tabel
    c.setFont("Helvetica", 8)
    c.drawString(55, height - 225, d['load'])
    c.drawString(130, height - 225, d['prod'][:30])
    c.drawString(260, height - 225, d['ori'])
    c.drawString(310, height - 225, d['dest'])
    c.drawString(360, height - 225, d['kolli'])
    c.drawString(410, height - 225, f"Rp {d['price']:,.0f}")
    c.drawString(470, height - 225, f"{d['weight']} Kg")
    c.drawString(515, height - 225, f"Rp {d['total']:,.0f}")

    # Footer
    c.line(50, height - 240, 550, height - 240)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(330, height - 255, "YANG HARUS DI BAYAR")
    c.drawString(480, height - 255, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, height - 275, f"Terbilang: {d['said']}")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 150, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, 135, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, 120, "A/N ADITYA GAMA SAPUTRI")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 105, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200")

    c.setFont("Helvetica", 10)
    c.drawString(400, 150, f"Surabaya, {d['date']}")
    c.drawString(400, 135, "Sincerely,")
    c.drawString(400, 120, "PT. GAMA GEMAH GEMILANG")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, 60, "KELVINITO JAYADI")
    c.drawString(400, 48, "DIREKTUR")
    
    c.save()
    buf.seek(0)
    return buf

# LOGIKA NOMOR INVOICE OTOMATIS
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# SISTEM TAB
tab_input, tab_preview = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_input:
    # Menggunakan form tunggal dengan tombol submit yang benar
    with st.form(key="form_invoice"):
        col_1, col_2 = st.columns(2)
        cust_in = col_1.text_input("Customer", placeholder="Contoh: BAPAK ANDI")
        date_in = col_1.date_input("Tanggal Invoice", datetime.now())
        inv_no_in = col_2.text_input("Nomor Invoice", value=auto_no_inv)
        load_date_in = col_2.date_input("Date of Load", datetime.now())

        col_3, col_4 = st.columns(2)
        prod_in = col_3.text_area("Product Description")
        ori_in = col_3.text_input("Origin", value="SBY")
        dest_in = col_3.text_input("Destination", value="MEDAN")
        
        kolli_in = col_4.text_input("KOLLI", value="")
        weight_in = col_4.number_input("Weight (Kg)", min_value=0.0)
        price_in = col_4.number_input("Harga per Kg (Rp)", min_value=0)
        
        # Kalkulasi Total
        total_val = int(weight_in * price_in)
        terbilang_val = format_terbilang(total_val)
        
        st.write(f"**Total Otomatis:** Rp {total_val:,.0f}")
        
        # Tombol Submit Form
        btn_submit = st.form_submit_button("Simpan & Siapkan Preview")
        
        if btn_submit:
            st.session_state.data = {
                "cust": cust_in, "inv": inv_no_in, "date": date_in.strftime("%d/%m/%Y"),
                "load": load_date_in.strftime("%d-%b-%y"), "prod": prod_in, "ori": ori_in,
                "dest": dest_in, "kolli": kolli_in, "weight": weight_in, "price": price_in,
                "total": total_val, "said": terbilang_val
            }
            st.success("Data disimpan. Buka Tab 'Preview & Download' untuk mengunduh PDF.")

with tab_preview:
    if 'data' in st.session_state:
        d_final = st.session_state.data
        st.subheader("Konfirmasi Invoice")
        st.write(f"**Customer:** {d_final['cust']} | **Total:** Rp {d_final['total']:,.0f}")
        
        # Proses PDF
        pdf_ready = generate_pdf(d_final)
        
        st.download_button(
            label="📥 Download Invoice PDF",
            data=pdf_ready,
            file_name=f"Invoice_{d_final['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Silakan isi data di tab 'Input Data' dan klik Simpan.")
