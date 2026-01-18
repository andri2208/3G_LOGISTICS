import streamlit as st
import pandas as pd
from datetime import datetime
from num2words import num2words
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Invoice System", page_icon="FAVICON.png", layout="wide")

# CSS PROTEKSI ANTI-DOWNLOAD
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# 2. FUNGSI GENERATE PDF DENGAN HEADER & STEMPEL
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # --- POSISI HEADER (PALING ATAS) ---
    try:
        header_img = ImageReader("HEADER INVOICE.png")
        # Menempatkan Header di koordinat Y tertinggi (height - 90)
        c.drawImage(header_img, 40, height - 90, width=520, preserveAspectRatio=True, mask='auto')
    except:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")

    # --- JUDUL & INFO ---
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 120, "INVOICE")
    
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 145, f"CUSTOMER: {d['cust']}")
    c.drawString(440, height - 145, f"DATE: {d['date']}")
    c.drawString(50, height - 158, f"NO. INVOICE: {d['inv']}")

    # --- TABEL DATA ---
    t_top = height - 175
    c.setLineWidth(0.5)
    c.line(50, t_top, 550, t_top)
    
    c.setFont("Helvetica-Bold", 8)
    headers = ["Date of Load", "Description", "Origin", "Dest", "Kolli", "Harga", "Weight", "Total"]
    x_pos = [52, 115, 245, 295, 340, 390, 455, 505]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], t_top - 14, h)
    c.line(50, t_top - 20, 550, t_top - 20)

    # Isi Baris
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

    # --- SUMMARY ---
    c.setFont("Helvetica-Bold", 9)
    c.drawString(340, row_y - 25, "YANG HARUS DI BAYAR")
    c.drawRightString(545, row_y - 25, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, row_y - 45, f"Terbilang: {d['said']}")

    # --- FOOTER & TANDA TANGAN ---
    f_y = row_y - 95
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, f_y, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, f_y - 15, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, f_y - 28, "A/N ADITYA GAMA SAPUTRI")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, f_y - 45, f"NB: Jika sudah transfer mohon konfirmasi ke Finance {d['fin_no']}")

    # Info Tanda Tangan
    c.setFont("Helvetica", 9)
    c.drawString(400, f_y, f"Surabaya, {d['date']}")
    c.drawString(400, f_y - 15, "Sincerely,")
    c.drawString(400, f_y - 28, "PT. GAMA GEMAH GEMILANG")
    
    # --- STEMPEL & TANDA TANGAN (POSISI DI ATAS NAMA DIREKTUR) ---
    try:
        stempel_img = ImageReader("STEMPEL TANDA TANGAN.png")
        # Posisi stempel menimpa sedikit area nama direktur agar terlihat asli
        c.drawImage(stempel_img, 380, f_y - 100, width=150, preserveAspectRatio=True, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 9)
    c.drawString(400, f_y - 85, "KELVINITO JAYADI")
    c.drawString(400, f_y - 97, "DIREKTUR")
    
    c.save()
    buf.seek(0)
    return buf

# 3. LOGIKA APLIKASI
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_in:
    with st.form("form_final_v3"):
        col1, col2 = st.columns(2)
        cust = col1.text_input("Customer Name", placeholder="Contoh: BAPAK ANDI")
        tgl_inv = col1.date_input("Invoice Date", datetime.now())
        no_inv = col2.text_input("Invoice Number", value=auto_no)
        tgl_load = col2.date_input("Date of Load", datetime.now())

        col3, col4 = st.columns(2)
        p_desc = col3.text_area("Product Description")
        origin = col3.text_input("Origin", value="SBY")
        dest = col3.text_input("Destination")
        fin_no = col3.selectbox("Finance Contact", ["082179799200", "081217833322"])
        
        kolli = col4.text_input("KOLLI (e.g., 45)")
        weight = col4.text_input("WEIGHT (e.g., 487 Kg)")
        price = col4.number_input("Harga Satuan (Rp)", min_value=0)
        
        # Perhitungan total: Jika Weight ada angkanya, kalikan. Jika tidak, ambil Harga langsung.
        try:
            w_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', weight)))
            total_val = int(w_val * price)
        except:
            total_val = int(price)
            
        if st.form_submit_button("Simpan & Siapkan PDF"):
            st.session_state.data = {
                "cust": cust, "inv": no_inv, "date": tgl_inv.strftime("%d/%m/%Y"),
                "load": tgl_load.strftime("%d-%b-%y"), "prod": p_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                "total": total_val, "said": format_terbilang(total_val), "fin_no": fin_no
            }
            st.success("Berhasil! Silakan klik Tab Preview.")

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.download_button(
            label="📥 Download Invoice (Header & Stempel Aktif)",
            data=generate_pdf(d),
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Isi data di tab Input Data terlebih dahulu.")
