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

# CSS PROTEKSI
st.markdown("<style>img { pointer-events: none; } #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# 2. FUNGSI GENERATE PDF
def generate_pdf(d):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # --- POSISI HEADER (PALING ATAS) ---
    try:
        header_img = ImageReader("HEADER INVOICE.png")
        # Menempatkan Header di koordinat Y tertinggi
        c.drawImage(header_img, 40, height - 95, width=520, preserveAspectRatio=True, mask='auto')
    except:
        # Teks Backup jika Gambar Tidak Ditemukan
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 50, "PT. GAMA GEMAH GEMILANG")
        c.setFont("Helvetica", 8)
        c.drawString(50, height - 62, "Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik")

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
    headers = ["Date of Load", "Description", "Origin", "Dest", "Kolli", "Harga/Kg", "Weight", "Total"]
    x_pos = [52, 115, 245, 295, 340, 390, 455, 505]
    for i, h in enumerate(headers):
        c.drawString(x_pos[i], t_top - 14, h)
    
    c.line(50, t_top - 20, 550, t_top - 20)

    # Isi Tabel
    c.setFont("Helvetica", 8)
    row_y = t_top - 34
    c.drawString(52, row_y, d['load'])
    c.drawString(115, row_y, d['prod'][:35])
    c.drawString(245, row_y, d['ori'])
    c.drawString(295, row_y, d['dest'])
    c.drawString(340, row_y, d['kolli'])
    c.drawString(390, row_y, f"Rp {d['price']:,.0f}")
    c.drawString(455, row_y, f"{d['weight']} Kg")
    c.drawRightString(545, row_y, f"Rp {d['total']:,.0f}")
    
    c.line(50, row_y - 10, 550, row_y - 10)

    # --- SUMMARY & FOOTER ---
    c.setFont("Helvetica-Bold", 9)
    c.drawString(340, row_y - 25, "YANG HARUS DI BAYAR")
    c.drawRightString(545, row_y - 25, f"Rp {d['total']:,.0f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, row_y - 45, f"Terbilang: {d['said']}")

    # Info Bank & Finance
    f_y = row_y - 95
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, f_y, "TRANSFER TO :")
    c.setFont("Helvetica", 9)
    c.drawString(50, f_y - 15, "Bank Central Asia (BCA) - 6720422334")
    c.drawString(50, f_y - 28, "A/N ADITYA GAMA SAPUTRI")
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, f_y - 45, f"NB: Jika sudah transfer mohon konfirmasi ke Finance {d['fin_no']}")

    # Tanda Tangan
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

# 3. LOGIKA APLIKASI
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

tab_in, tab_prev = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_in:
    with st.form("form_final_clean"):
        c1, c2 = st.columns(2)
        cust = c1.text_input("Customer")
        tgl_inv = c1.date_input("Tanggal Invoice", datetime.now())
        no_inv = c2.text_input("Nomor Invoice", value=auto_no)
        tgl_load = c2.date_input("Date of Load", datetime.now())

        c3, c4 = st.columns(2)
        p_desc = c3.text_area("Product Description")
        origin = c3.text_input("Origin", value="SBY")
        dest = c3.text_input("Destination", value="MEDAN")
        fin_no = c3.selectbox("Nomor Finance", ["082179799200", "081217833322"])
        
        kolli = c4.text_input("KOLLI")
        weight = c4.number_input("Weight (Kg)", min_value=0.0)
        price = c4.number_input("Harga Satuan (Rp)", min_value=0)
        
        total = int(weight * price)
        
        if st.form_submit_button("Simpan Data & Siapkan PDF"):
            if not cust:
                st.error("Nama Customer harus diisi!")
            else:
                st.session_state.data = {
                    "cust": cust, "inv": no_inv, "date": tgl_inv.strftime("%d/%m/%Y"),
                    "load": tgl_load.strftime("%d-%b-%y"), "prod": p_desc, "ori": origin,
                    "dest": dest, "kolli": kolli, "weight": weight, "price": price,
                    "total": total, "said": format_terbilang(total), "fin_no": fin_no
                }
                st.success("Data Tersimpan! Silakan ke Tab Preview.")

with tab_prev:
    if 'data' in st.session_state:
        d = st.session_state.data
        st.write(f"Draf untuk: **{d['cust']}**")
        st.download_button(
            label="📥 Download PDF Invoice",
            data=generate_pdf(d),
            file_name=f"Invoice_{d['cust']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Isi data terlebih dahulu di tab 'Input Data'.")
