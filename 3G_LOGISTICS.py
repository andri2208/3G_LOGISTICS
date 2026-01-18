import streamlit as st
import pandas as pd
from datetime import datetime
from num2words import num2words
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Invoice System", layout="wide")

# CSS ANTI-DOWNLOAD POLICY
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# 2. FUNGSI GENERATE PDF
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # HEADER IMAGE [cite: 31, 35]
    try:
        header_img = ImageReader("HEADER INVOICE.png")
        c.drawImage(header_img, 40, height - 90, width=520, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG [cite: 30]")

    # JUDUL [cite: 33]
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 120, "INVOICE")
    
    # INFO CUSTOMER & DATE [cite: 32, 34]
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 145, f"CUSTOMER: {d['cust']}")
    c.drawString(440, height - 145, f"DATE: {d['date']}")
    c.drawString(50, height - 158, f"NO. INVOICE: {d['inv']}")

    # TABEL [cite: 35]
    t_top = height - 175
    c.setLineWidth(0.5)
    c.line(50, t_top, 550, t_top)
    c.setFont("Helvetica-Bold", 8)
    headers = ["Date of Load", "Product Description", "Origin", "Dest", "Kolli", "Harga", "Weight", "Total"]
    x_pos = [52, 115, 245, 295, 340, 390, 455, 505]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], t_top - 14, h)
    c.line(50, t_top - 20, 550, t_top - 20)

    # ISI TABEL [cite: 35]
    c.setFont("Helvetica", 8)
    row_y = t_top - 34
    c.drawString(52, row_y, d['load'])
    c.drawString(115, row_y, d['prod'][:35])
    c.drawString(245, row_y, d['ori'])
    c.drawString(295, row_y, d['dest'])
    c.drawString(340, row_y, d['kolli'])
    c.drawString(390, row_y, f"Rp {d['price']:,.0f}")
    c.drawString(455, row_y, f"{d['weight']}")
    c.drawRightString(545, row_y, f"Rp {d['total']:,.0f}")
    c.line(50, row_y - 10, 550, row_y - 10)

    # TOTAL & TERBILANG [cite: 38, 40]
    c.setFont("Helvetica-Bold", 9)
    c.drawString(340, row_y - 25, "YANG HARUS DI BAYAR")
    c.drawRightString(545, row_y - 25, f"Rp {d['total']:,.0f}")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, row_y - 45, f"Terbilang: {d['said']}")

    # FOOTER [cite: 41, 44, 45, 48]
    f_y = row_y - 95
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, f_y, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, f_y - 15, "Bank Central Asia (BCA) - 6720422334 [cite: 42, 43]")
    c.drawString(50, f_y - 28, "A/N ADITYA GAMA SAPUTRI [cite: 44]")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, f_y - 45, f"NB: Jika sudah transfer mohon konfirmasi ke Finance {d['fin_no']} [cite: 45]")

    c.setFont("Helvetica", 9)
    c.drawString(400, f_y, f"Surabaya, {d['date']}")
    c.drawString(400, f_y - 15, "Sincerely,")
    c.drawString(400, f_y - 28, "PT. GAMA GEMAH GEMILANG [cite: 47]")
    
    # STEMPEL [cite: 48]
    try:
        stempel = ImageReader("STEMPEL TANDA TANGAN.png")
        c.drawImage(stempel, 380, f_y - 90, width=150, preserveAspectRatio=True, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 9)
    c.drawString(400, f_y - 85, "KELVINITO JAYADI [cite: 48]")
    c.drawString(400, f_y - 97, "DIREKTUR [cite: 49]")
    
    c.save()
    buf.seek(0)
    return buf

# 3. INTERFACE
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Live Preview & Download"])

with tab_in:
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        cust = c1.text_input("Customer", placeholder="Nama Bapak Andi [cite: 32]")
        tgl_inv = c1.date_input("Invoice Date", datetime.now())
        no_inv = c2.text_input("Invoice Number", value=auto_no)
        tgl_load = c2.date_input("Date of Load", datetime.now())

        c3, c4 = st.columns(2)
        p_desc = c3.text_area("Description")
        ori = c3.text_input("Origin", value="SBY")
        dest = c3.text_input("Destination")
        fin = c3.selectbox("Finance", ["082179799200", "081217833322"]) [cite: 45]
        
        kolli = c4.text_input("KOLLI")
        weight = c4.text_input("WEIGHT (Contoh: 290 Kg)") [cite: 35]
        price = c4.number_input("Harga/Total (Rp)", min_value=0)
        
        if st.form_submit_button("Preview Invoice Sekarang"):
            st.session_state.data = {
                "cust": cust, "inv": no_inv, "date": tgl_inv.strftime("%d/%m/%Y"),
                "load": tgl_load.strftime("%d-%b-%y"), "prod": p_desc, "ori": ori,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                "total": price, "said": format_terbilang(price), "fin_no": fin
            }

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        
        # TAMPILKAN HEADER & STEMPEL UNTUK CEK FILE
        st.subheader("Pengecekan File Gambar:")
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            try:
                st.image("HEADER INVOICE.png", caption="Header Terdeteksi", width=300)
            except:
                st.error("File HEADER INVOICE.png tidak ditemukan di server!")
        with col_img2:
            try:
                st.image("STEMPEL TANDA TANGAN.png", caption="Stempel Terdeteksi", width=150)
            except:
                st.error("File STEMPEL TANDA TANGAN.png tidak ditemukan di server!")
        
        st.divider()
        
        # GENERATE PDF
        final_pdf = generate_pdf(d)
        
        # PRATINJAU DATA
        st.write("### Draft Preview")
        st.write(f"**Invoice:** {d['inv']} | **Customer:** {d['cust']}")
        
        st.download_button(
            label="📥 DOWNLOAD PDF SEKARANG",
            data=final_pdf,
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Isi data terlebih dahulu di Tab Input.")
