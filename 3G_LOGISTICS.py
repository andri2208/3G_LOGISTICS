import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from num2words import num2words
from datetime import datetime

# --- KONFIGURASI GOOGLE SHEETS ---
# Mengubah link edit menjadi link export CSV agar bisa dibaca Pandas secara langsung
SHEET_ID = "1CREhsdJ2VO-X09Wbf1nI2frm-pCkHcdCPAuRNkUNCos"
URL_GSHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10) # Data refresh setiap 10 detik
def load_data():
    try:
        # Membaca data langsung dari Google Sheets
        return pd.read_csv(URL_GSHEET)
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")
        columns = ['No_Resi', 'No_Inv', 'Customer', 'Tanggal', 'Date_Load', 
                   'Description', 'Origin', 'Destination', 'Kolli', 'Harga', 'Weight', 'Total']
        return pd.DataFrame(columns=columns)

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287)

    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 10, w=150)
    pdf.ln(35)

    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(190, 6, "INVOICE", 1, 1, 'C', True)

    pdf.set_font("Helvetica", size=8)
    pdf.cell(25, 6, "CUSTOMER  :", 0); pdf.cell(100, 6, str(data['Customer']), 0)
    pdf.cell(25, 6, "NO.INV     :", 0); pdf.cell(40, 6, str(data['No_Inv']), 0, ln=True)
    pdf.cell(25, 6, "TANGGAL    :", 0); pdf.cell(100, 6, str(data['Tanggal']), 0)
    pdf.cell(25, 6, "NO.RESI    :", 0); pdf.cell(40, 6, str(data['No_Resi']), 0, ln=True)
    
    pdf.ln(2)
    # Tabel Utama
    pdf.set_font("Helvetica", 'B', 7)
    pdf.set_fill_color(52, 119, 181); pdf.set_text_color(255, 255, 255)
    headers = [("Date of Load", 20), ("Product Description", 50), ("Origin", 20), 
               ("Destination", 25), ("KOLLI", 15), ("HARGA", 20), ("WEIGHT", 20), ("TOTAL", 20)]
    for h_name, h_width in headers:
        pdf.cell(h_width, 7, h_name, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", size=8)
    pdf.cell(20, 10, str(data['Date_Load']), 1, 0, 'C')
    pdf.cell(50, 10, str(data['Description']), 1, 0, 'L')
    pdf.cell(20, 10, str(data['Origin']), 1, 0, 'C')
    pdf.cell(25, 10, str(data['Destination']), 1, 0, 'C')
    pdf.cell(15, 10, str(data['Kolli']), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['Harga']:,}".replace(",", "."), 1, 0, 'R')
    pdf.cell(20, 10, str(data['Weight']), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['Total']:,}".replace(",", "."), 1, 1, 'R')

    # Total & Terbilang
    pdf.set_fill_color(160, 160, 160); pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(170, 7, "YANG HARUS DI BAYAR", 1, 0, 'C', True)
    pdf.cell(20, 7, f"Rp {data['Total']:,}".replace(",", "."), 1, 1, 'R', True)

    terbilang = num2words(data['Total'], lang='id').title() + " Rupiah"
    pdf.set_fill_color(220, 220, 220); pdf.set_font("Helvetica", 'BI', 9)
    pdf.cell(190, 8, f"Terbilang: {terbilang}", 1, 1, 'C', True)

    # Tanda Tangan & Bank
    pdf.ln(5); curr_y = pdf.get_y()
    pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(100, 5, "TRANSFER TO : BCA / 6720422334 / ADITYA GAMA SAPUTRI", 0, 1)
    
    pdf.set_y(curr_y)
    pdf.cell(130, 5, "", 0); pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    if os.path.exists("ttd.png"):
        pdf.image("ttd.png", 145, pdf.get_y(), w=35)
    pdf.ln(15)
    pdf.cell(130, 5, "", 0); pdf.set_font("Helvetica", 'BU', 9); pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
st.set_page_config(page_title="Logistik App Online", layout="wide")
df = load_data()

st.title("🚚 Sistem Logistik Online - PT. 3G")

tab1, tab2 = st.tabs(["🔍 Cek & Cetak Invoice", "➕ Input Data (via Google Sheets)"])

with tab1:
    st.subheader("Cetak dari Database Cloud")
    if not df.empty:
        # Membersihkan data dari baris kosong (jika ada di Google Sheets)
        df_clean = df.dropna(subset=['No_Resi'])
        list_resi = df_clean['No_Resi'].astype(str).unique().tolist()[::-1]
        
        selected = st.selectbox("Cari Nomor Resi:", options=list_resi, index=None)
        
        if selected:
            row = df[df['No_Resi'].astype(str) == selected].iloc[0]
            st.info(f"Customer: {row['Customer']} | Total: Rp {row['Total']:,}".replace(",", "."))
            
            pdf_bytes = generate_pdf(row)
            st.download_button(
                label="📥 Download Invoice PDF",
                data=pdf_bytes,
                file_name=f"Invoice_{selected}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("Data tidak ditemukan di Google Sheets.")

with tab2:
    st.info("💡 **Tips Online:** Untuk menjaga keamanan dan kecepatan di HP, silakan input data baru langsung melalui aplikasi Google Sheets Anda.")
    st.link_button("🚀 Buka Google Sheets untuk Input Data", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    st.write("Setelah mengisi data di Google Sheets, kembali ke sini dan refresh halaman untuk cetak PDF.")
