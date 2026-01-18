import streamlit as st
import pandas as pd
from datetime import datetime
from num2words import num2words
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Invoice System", page_icon="FAVICON.png", layout="wide")

# CSS ANTI-DOWNLOAD
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# FUNGSI GENERATE PDF (DIPERKETAT & DIBERI GARIS)
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # 1. HEADER IMAGE (Paling Atas)
    try:
        header = ImageReader("HEADER INVOICE.png")
        c.drawImage(header, 50, height - 85, width=500, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")

    # 2. JUDUL & INFO UTAMA (Dibuat Lebih Rapat)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 110, "INVOICE")
    
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 135, f"CUSTOMER: {d['cust']}")
    c.drawString(430, height - 135, f"DATE: {d['date']}")
    c.drawString(50, height - 148, f"NO. INVOICE: {d['inv']}")

    # 3. TABEL DENGAN GARIS (GRID)
    top_table = height - 165
    row_height = 20
    
    # Header Tabel
    c.setLineWidth(1)
    c.line(50, top_table, 550, top_table) # Garis atas
    c.setFont("Helvetica-Bold", 8)
    
    headers = ["Date of Load", "Description", "Origin", "Dest", "Kolli", "Harga/Kg", "Weight", "Total"]
    x_pos = [52, 115, 235, 285, 335, 385, 450, 505]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], top_table - 14, h)
    
    c.line(50, top_table - 20, 550, top_table - 20) # Garis bawah header

    # Isi Tabel
    c.setFont("Helvetica", 8)
    curr_y = top_table - 35
    c.drawString(52, curr_y, d['load'])
    c.drawString(115, curr_y, d['prod'][:35])
    c.drawString(235, curr_y, d['ori'])
    c.drawString(285, curr_y, d['dest'])
    c.drawString(335, curr_y, d['kolli'])
    c.drawString(385, curr_y, f"Rp {d['price']:,.0f}")
    c.drawString(450, curr_y, f"{d['weight']} Kg")
    c.drawString(505, curr_y, f"Rp {d['total']:,.0f}")
    
    c.line(50, curr_y - 10, 550, curr_y - 10) # Garis bawah isi

    # 4. TOTAL & TERBILANG (Dibuat Lebih Ringkas)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(335, curr_y - 25, "YANG HARUS DI BAYAR")
    c.drawRightString(545, curr_y - 25, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, curr_y - 40, f"Terbilang: {d['said']}")

    # 5. FOOTER (Posisi Dinaikkan agar Tidak Terlalu Bawah)
    footer_y = curr_y - 80
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, footer_y, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, footer_y - 15, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, footer_y - 28, "A/N ADITYA GAMA SAPUTRI")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, footer_y - 45, "NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200")

    # Tanda Tangan
    c.setFont("Helvetica", 9)
    c.drawString(400, footer_y, f"Surabaya, {d['date']}")
    c.drawString(400, footer_y - 15, "Sincerely,")
    c.drawString(400, footer_y - 28, "PT. GAMA GEMAH GEMILANG")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(400, footer_y - 80, "KELVINITO JAYADI")
    c.drawString(400, footer_y - 92, "DIREKTUR")
    
    c.save()
    buf.seek(0)
    return buf

# LOGIKA NOMOR INVOICE
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# SISTEM TAB
tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_in:
    with st.form("form_3g_v2"):
        c1, c2 = st.columns(2)
        c_name = c1.text_input("Customer", placeholder="Nama PT / Perorangan")
        i_date = c1.date_input("Tanggal Invoice", datetime.now())
        i_no = c2.text_input("Nomor Invoice", value=auto_no_inv)
        l_date = c2.date_input("Date of Load", datetime.now())

        c3, c4 = st.columns(2)
        p_desc = c3.text_area("Product Description")
        origin = c3.text_input("Origin", value="SBY")
        dest = c3.text_input("Destination", value="MEDAN")
        
        kolli = c4.text_input("KOLLI", value="")
        weight = c4.number_input("Weight (Kg)", min_value=0.0)
        price = c4.number_input("Harga Satuan (Rp)", min_value=0)
        
        total = int(weight * price)
        said = format_terbilang(total)
        
        if st.form_submit_button("Simpan & Kunci Data"):
            st.session_state.data = {
                "cust": c_name, "inv": i_no, "date": i_date.strftime("%d/%m/%Y"),
                "load": l_date.strftime("%d-%b-%y"), "prod": p_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                "total": total, "said": said
            }
            st.success("Data disimpan! Silakan klik Tab Preview.")

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.info(f"Invoice untuk {d['cust']} siap diunduh.")
        
        pdf = generate_pdf(d)
        st.download_button(
            label="📥 Download PDF (Tampilan Ringkas)",
            data=pdf,
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Belum ada data. Isi di tab Input Data.")
