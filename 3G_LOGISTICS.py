import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from num2words import num2words
from datetime import datetime
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Logistik App 3G Online", layout="wide")

# Link Google Sheets Anda
URL_SHEET = "https://docs.google.com/spreadsheets/d/1CREhsdJ2VO-X09Wbf1nI2frm-pCkHcdCPAuRNkUNCos/edit?usp=sharing"

# --- KONEKSI DATABASE ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # Refresh data setiap 5 detik
def load_data():
    try:
        return conn.read(spreadsheet=URL_SHEET)
    except Exception:
        # Jika sheet kosong, buat kolom default
        columns = ['No_Resi', 'No_Inv', 'Customer', 'Tanggal', 'Date_Load', 
                   'Description', 'Origin', 'Destination', 'Kolli', 'Harga', 'Weight', 'Total']
        return pd.DataFrame(columns=columns)

def generate_auto_no(prefix, df):
    """Menghasilkan nomor otomatis berbasis jumlah baris"""
    date_str = datetime.now().strftime("%d%m%y")
    count = len(df) + 1
    return f"3G/{prefix}/{date_str}/{count:03d}"

# --- FUNGSI GENERATE PDF ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) # Border luar

    # Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 10, w=150)
    pdf.ln(15)

    # Header Invoice
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
    
    # Isi Data Tabel
    pdf.cell(20, 10, str(data['Date_Load']), 1, 0, 'C')
    pdf.cell(50, 10, str(data['Description']), 1, 0, 'L')
    pdf.cell(20, 10, str(data['Origin']), 1, 0, 'C')
    pdf.cell(25, 10, str(data['Destination']), 1, 0, 'C')
    pdf.cell(15, 10, str(data['Kolli']), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['Harga']:,.0f}".replace(",", "."), 1, 0, 'R')
    pdf.cell(20, 10, str(data['Weight']), 1, 0, 'C')
    pdf.cell(20, 10, f"{data['Total']:,.0f}".replace(",", "."), 1, 1, 'R')

    # Total & Terbilang
    pdf.set_fill_color(160, 160, 160); pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(170, 7, "YANG HARUS DI BAYAR", 1, 0, 'C', True)
    pdf.cell(20, 7, f"Rp {data['Total']:,.0f}".replace(",", "."), 1, 1, 'R', True)

    terbilang = num2words(data['Total'], lang='id').title() + " Rupiah"
    pdf.set_fill_color(220, 220, 220); pdf.set_font("Helvetica", 'BI', 9)
    pdf.cell(190, 8, f"Terbilang: {terbilang}", 1, 1, 'C', True)

    # Footer Bank & TTD
    pdf.ln(5); curr_y = pdf.get_y()
    pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(100, 5, "TRANSFER TO : BCA / 6720422334 / ADITYA GAMA SAPUTRI", 0, 1)
    
    pdf.set_y(curr_y)
    pdf.cell(130, 5, "", 0); pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    
    if os.path.exists("ttd.png"):
        pdf.image("ttd.png", 145, pdf.get_y(), w=35)
    
    pdf.ln(15)
    pdf.cell(130, 5, "", 0); pdf.set_font("Helvetica", 'BU', 9); pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    pdf.cell(130, 5, "", 0); pdf.set_font("Helvetica", 'B', 8); pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- MAIN UI ---
st.title("🚚 Logistik App - PT. Gama Gemah Gemilang")
df = load_data()

tab1, tab2 = st.tabs(["🔍 Cek & Cetak Invoice", "➕ Input Data Baru"])

with tab1:
    st.subheader("Cari Data di Database")
    if not df.empty:
        df_clean = df.dropna(subset=['No_Resi'])
        list_resi = df_clean['No_Resi'].astype(str).unique().tolist()[::-1]
        
        selected = st.selectbox("Pilih Nomor Resi:", options=list_resi, index=None)
        
        if selected:
            row = df[df['No_Resi'].astype(str) == selected].iloc[0]
            st.info(f"**Customer:** {row['Customer']} | **Total Tagihan:** Rp {row['Total']:,.0f}".replace(",", "."))
            
            pdf_bytes = generate_pdf(row)
            st.download_button(
                label="📥 Download PDF Invoice",
                data=pdf_bytes,
                file_name=f"Invoice_{selected}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("Database Google Sheets masih kosong.")

with tab2:
    st.subheader("Form Input Database")
    inv_auto = generate_auto_no("INV", df)
    resi_auto = generate_auto_no("RES", df)

    with st.form("input_form", clear_on_submit=True):
        st.write(f"**Draft Nomor:** {inv_auto} / {resi_auto}")
        col1, col2 = st.columns(2)
        
        with col1:
            customer = st.text_input("Nama Customer")
            tgl = st.date_input("Tanggal Invoice", datetime.now())
            date_load = st.text_input("Date of Load (Contoh: 24-Jan-26)")
            desc = st.text_input("Product Description")
        
        with col2:
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
            kolli = st.number_input("Jumlah KOLLI", min_value=1)
            harga = st.number_input("Harga Satuan", min_value=0)
            weight = st.number_input("Weight (Kg)", min_value=0)

        submitted = st.form_submit_button("Simpan Permanen ke Google Sheets")

        if submitted:
            new_data = pd.DataFrame([{
                'No_Resi': resi_auto, 'No_Inv': inv_auto, 'Customer': customer,
                'Tanggal': tgl.strftime("%d/%m/%Y"), 'Date_Load': date_load,
                'Description': desc, 'Origin': origin, 'Destination': dest,
                'Kolli': kolli, 'Harga': harga, 'Weight': weight, 'Total': harga * weight
            }])
            
            # Gabungkan data lama dan baru
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # Tulis balik ke Google Sheets
            conn.update(spreadsheet=URL_SHEET, data=updated_df)
            
            st.success(f"✅ Data {resi_auto} Berhasil Disimpan!")
            st.cache_data.clear()
            st.balloons()
            st.rerun()

