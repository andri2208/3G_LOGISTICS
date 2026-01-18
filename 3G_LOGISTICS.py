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

# FUNGSI GENERATE PDF
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # --- 1. HEADER IMAGE (POSISI PALING ATAS) ---
    try:
        header = ImageReader("HEADER INVOICE.png")
        # Menempatkan logo di koordinat atas dengan lebar penuh yang aman
        c.drawImage(header, 50, height - 90, width=500, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")
        c.setFont("Helvetica", 8)
        c.drawString(50, height - 62, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik")

    # --- 2. JUDUL INVOICE & INFO DASAR ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 120, "INVOICE")
    
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 145, f"CUSTOMER: {d['cust']}")
    c.drawString(440, height - 145, f"DATE: {d['date']}")
    c.drawString(50, height - 158, f"NO. INVOICE: {d['inv']}")

    # --- 3. TABEL BERGARIS (PADAT & RAPI) ---
    t_top = height - 175
    c.setLineWidth(0.5)
    
    # Garis Header Tabel
    c.line(50, t_top, 550, t_top)
    c.setFont("Helvetica-Bold", 8)
    headers = ["Date of Load", "Description", "Origin", "Dest", "Kolli", "Harga/Kg", "Weight", "Total"]
    x_pos = [52, 115, 245, 295, 340, 390, 455, 505]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], t_top - 14, h)
    c.line(50, t_top - 20, 550, t_top - 20)

    # Isi Tabel
    c.setFont("Helvetica", 8)
    row_y = t_top - 34
    c.drawString(52, row_y, d['load'])
    c.drawString(115, row_y, d['prod'][:35]) # Limit teks agar tidak tabrakan
    c.drawString(245, row_y, d['ori'])
    c.drawString(295, row_y, d['dest'])
    c.drawString(340, row_y, d['kolli'])
    c.drawString(390, row_y, f"Rp {d['price']:,.0f}")
    c.drawString(455, row_y, f"{d['weight']} Kg")
    c.drawRightString(545, row_y, f"Rp {d['total']:,.0f}")
    
    # Garis Bawah Isi
    c.line(50, row_y - 10, 550, row_y - 10)

    # --- 4. TOTAL & TERBILANG ---
    c.setFont("Helvetica-Bold", 9)
    c.drawString(340, row_y - 25, "YANG HARUS DI BAYAR")
    c.drawRightString(545, row_y - 25, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, row_y - 45, f"Terbilang: {d['said']}")

    # --- 5. FOOTER (BANK & TANDA TANGAN) ---
    f_y = row_y - 90
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, f_y, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, f_y - 15, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, f_y - 28, "A/N ADITYA GAMA SAPUTRI")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, f_y - 45, f"NB: Jika sudah transfer mohon konfirmasi ke Finance {d['fin_no']}")

    # Area Tanda Tangan
    c.setFont("Helvetica", 9)
    c.drawString(400, f_y, f"Surabaya, {d['date']}")
    c.drawString(400, f_y - 15, "Sincerely,")
    c.drawString(400, f_y - 28, "PT. GAMA GEMAH GEMILANG")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(400, f_y - 85, "KELVINITO JAYADI")
    c.drawString(400, f_y - 97, "DIREKTUR")
    
    c.save()
    buf.seek(0)
    return buf

# LOGIKA NOMOR INVOICE
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# TAB SISTEM
tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_in:
    with st.form("form_3g_v3"):
        col1, col2 = st.columns(2)
        c_name = col1.text_input("Customer", placeholder="Nama Customer")
        i_date = col1.date_input("Tanggal Invoice", datetime.now())
        i_no = col2.text_input("Nomor Invoice", value=auto_no)
        l_date = col2.date_input("Date of Load", datetime.now())

        col3, col4 = st.columns(2)
        p_desc = col3.text_area("Product Description")
        origin = col3.text_input("Origin", value="SBY")
        dest = col3.text_input("Destination", value="MEDAN")
        
        fin_option = col3.selectbox("Kontak Finance", ["081217833322", "082179799200"])
        
        kolli = col4.text_input("KOLLI", value="")
        weight = col4.number_input("Weight (Kg)", min_value=0.0, step=0.1)
        price = col4.number_input("Harga Satuan (Rp)", min_value=0)
        
        total_calc = int(weight * price)
        said_calc = format_terbilang(total_calc)
        
        st.markdown(f"### Total: **Rp {total_calc:,.0f}**")
        
        if st.form_submit_button("Simpan & Kunci Data"):
            st.session_state.data = {
                "cust": c_name, "inv": i_no, "date": i_date.strftime("%d/%m/%Y"),
                "load": l_date.strftime("%d-%b-%y"), "prod": p_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                "total": total_calc, "said": said_calc, "fin_no": fin_option
            }
            st.success("Data Tersimpan! Silakan ke Tab Preview.")

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.write(f"Draf Invoice: **{d['inv']}** untuk **{d['cust']}**")
        
        pdf = generate_pdf(d)
        st.download_button(
            label="📥 Download PDF Invoice (Dengan Header)",
            data=pdf,
            file_name=f"Invoice_{d['cust']}_{d['inv'].replace('/','-')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Silakan isi data terlebih dahulu di tab Input.")
