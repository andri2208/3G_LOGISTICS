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
    
    # --- POSISI HEADER DIATAS TULISAN INVOICE ---
    try:
        header = ImageReader("HEADER INVOICE.png")
        # Menempatkan gambar di bagian paling atas
        c.drawImage(header, 50, height - 100, width=500, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")

    # Tulisan INVOICE tepat di bawah Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 130, "INVOICE")
    
    # Detail Info Customer & Tanggal
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"CUSTOMER: {d['cust']}")
    c.drawString(430, height - 160, f"DATE: {d['date']}")
    c.drawString(50, height - 175, f"NO. INVOICE: {d['inv']}")

    # Struktur Tabel (Sesuai Contoh PT HARVI & BAPAK ANDI)
    c.line(50, height - 190, 550, height - 190)
    c.setFont("Helvetica-Bold", 8)
    headers = ["Date of Load", "Description", "Origin", "Dest", "Kolli", "Harga/Kg", "Weight", "Total"]
    x_pos = [55, 130, 260, 310, 360, 410, 475, 515]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], height - 205, h)
    c.line(50, height - 210, 550, height - 210)

    # Isi Tabel
    c.setFont("Helvetica", 8)
    c.drawString(55, height - 225, d['load'])
    c.drawString(130, height - 225, d['prod'][:30])
    c.drawString(260, height - 225, d['ori'])
    c.drawString(310, height - 225, d['dest'])
    c.drawString(360, height - 225, d['kolli'])
    c.drawString(410, height - 225, f"Rp {d['price']:,.0f}")
    c.drawString(475, height - 225, f"{d['weight']} Kg")
    c.drawString(515, height - 225, f"Rp {d['total']:,.0f}")

    # Garis Bawah Tabel & Total
    c.line(50, height - 240, 550, height - 240)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(330, height - 255, "YANG HARUS DI BAYAR")
    c.drawString(480, height - 255, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, height - 275, f"Terbilang: {d['said']}")

    # Footer Bank & Tanda Tangan
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

# LOGIKA NOMOR INVOICE
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# TAB SISTEM
tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_in:
    with st.form("form_3g"):
        col1, col2 = st.columns(2)
        c_name = col1.text_input("Customer", placeholder="Nama Customer")
        i_date = col1.date_input("Tanggal Invoice", datetime.now())
        i_no = col2.text_input("Nomor Invoice", value=auto_no_inv)
        l_date = col2.date_input("Date of Load", datetime.now())

        col3, col4 = st.columns(2)
        p_desc = col3.text_area("Product Description")
        origin = col3.text_input("Origin", value="SBY")
        dest = col3.text_input("Destination", value="MEDAN")
        
        kolli = col4.text_input("KOLLI", value="")
        weight = col4.number_input("Weight (Kg)", min_value=0.0)
        price = col4.number_input("Harga Satuan (Rp)", min_value=0)
        
        total = int(weight * price)
        said = format_terbilang(total)
        
        if st.form_submit_button("Simpan & Siapkan PDF"):
            st.session_state.data = {
                "cust": c_name, "inv": i_no, "date": i_date.strftime("%d/%m/%Y"),
                "load": l_date.strftime("%d-%b-%y"), "prod": p_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                "total": total, "said": said
            }
            st.success("Berhasil! Silakan klik Tab Preview.")

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.subheader("Siap Download")
        st.write(f"Invoice untuk: **{d['cust']}**")
        
        pdf = generate_pdf(d)
        st.download_button(
            label="📥 Download PDF Sekarang",
            data=pdf,
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Isi data terlebih dahulu di tab Input.")
