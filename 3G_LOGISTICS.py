import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from num2words import num2words
from datetime import datetime

# --- KONFIGURASI GOOGLE SHEETS ---
# Mengambil ID dari link yang Anda berikan
SHEET_ID = "1CREhsdJ2VO-X09Wbf1nI2frm-pCkHcdCPAuRNkUNCos"
URL_GSHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10) # Refresh data setiap 10 detik
def load_data():
    try:
        # Membaca data langsung dari Google Sheets sebagai CSV
        df = pd.read_csv(URL_GSHEET)
        return df
    except Exception as e:
        # Jika gagal/kosong, buat dataframe kosong dengan kolom standar
        columns = ['No_Resi', 'No_Inv', 'Customer', 'Tanggal', 'Date_Load', 
                   'Description', 'Origin', 'Destination', 'Kolli', 'Harga', 'Weight', 'Total']
        return pd.DataFrame(columns=columns)

def generate_pdf(data):
    # Menggunakan Helvetica agar aman di server online (Linux)
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
    pdf.cell(25, 6, "CUSTOMER  :", 0)
    pdf.cell(100, 6, str(data['Customer']), 0)
    pdf.cell(25, 6, "NO.INV     :", 0)
    pdf.cell(40, 6, str(data['No_Inv']), 0, ln=True)
    
    pdf.cell(25, 6, "TANGGAL    :", 0)
    pdf.cell(100, 6, str(data['Tanggal']), 0)
    pdf.cell(25, 6, "NO.RESI    :", 0)
    pdf.cell(40, 6, str(data['No_Resi']), 0, ln=True)
    pdf.ln(2)

    # TABEL UTAMA
    pdf.set_font("Helvetica", 'B', 7)
    pdf.set_fill_color(52, 119, 181)
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(20, 7, "Date of Load", 1, 0, 'C', True)
    pdf.cell(50, 7, "Product Description", 1, 0, 'C', True)
    pdf.cell(20, 7, "Origin", 1, 0, 'C', True)
    pdf.cell(25, 7, "Destination", 1, 0, 'C', True)
    pdf.cell(15, 7, "KOLLI", 1, 0, 'C', True)
    pdf.cell(20, 7, "HARGA", 1, 0, 'C', True)
    pdf.cell(20, 7, "WEIGHT (Kg)", 1, 0, 'C', True)
    pdf.cell(20, 7, "TOTAL", 1, 1, 'C', True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(20, 10, str(data['Date_Load']), 1, 0, 'C')
    pdf.cell(50, 10, str(data['Description']), 1, 0, 'L')
    pdf.cell(20, 10, str(data['Origin']), 1, 0, 'C')
    pdf.cell(25, 10, str(data['Destination']), 1, 0, 'C')
    pdf.cell(15, 10, str(data['Kolli']), 1, 0, 'C')
    
    # Format Rupiah
    harga = float(data['Harga']) if str(data['Harga']).replace('.','').isdigit() else 0
    total = float(data['Total']) if str(data['Total']).replace('.','').isdigit() else 0
    
    pdf.cell(20, 10, f"Rp {harga:,.0f}".replace(",", "."), 1, 0, 'R')
    pdf.cell(20, 10, str(data['Weight']), 1, 0, 'C')
    pdf.cell(20, 10, f"Rp {total:,.0f}".replace(",", "."), 1, 1, 'R')

    # TOTAL & TERBILANG
    pdf.set_fill_color(160, 160, 160)
    pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(170, 7, "YANG HARUS DI BAYAR", 1, 0, 'C', True)
    pdf.cell(20, 7, f"Rp {total:,.0f}".replace(",", "."), 1, 1, 'R', True)

    pdf.set_fill_color(220, 220, 220)
    pdf.cell(190, 5, "Terbilang :", "LR", 1, 'L', True)
    terbilang = num2words(total, lang='id').title() + " Rupiah"
    pdf.set_font("Helvetica", 'BI', 9)
    pdf.cell(190, 8, f"{terbilang}", "LRB", 1, 'C', True)

    # TANDA TANGAN
    pdf.ln(5)
    curr_y = pdf.get_y()
    pdf.set_font("Helvetica", 'B', 8)
    pdf.cell(100, 5, "TRANSFER TO :", 0, 1)
    pdf.set_font("Helvetica", size=8)
    pdf.cell(100, 4, "Bank Central Asia / 6720422334", 0, 1)
    pdf.cell(100, 4, "A/N ADITYA GAMA SAPUTRI", 0, 1)
    
    pdf.set_y(curr_y)
    pdf.cell(130, 5, "", 0); pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    
    if os.path.exists("ttd.png"):
        pdf.image("ttd.png", 145, pdf.get_y(), w=35)
    
    pdf.ln(15)
    pdf.cell(130, 5, "", 0); pdf.set_font("Helvetica", 'BU', 9); pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    pdf.cell(130, 5, "", 0); pdf.set_font("Helvetica", 'B', 8); pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
st.set_page_config(page_title="Logistik App 3G Online", layout="wide")
df = load_data()

st.title("🚚 Sistem Logistik Online - PT. Gama Gemah Gemilang")

tab1, tab2 = st.tabs(["🔍 Cek & Cetak Invoice", "➕ Cara Input Data Baru"])

with tab1:
    st.subheader("Pilih Data dari Google Sheets")
    df = load_data() # Memastikan data terbaru
    
    if not df.empty:
        # Bersihkan data baris kosong
        df_clean = df.dropna(subset=['No_Resi'])
        list_resi = df_clean['No_Resi'].astype(str).unique().tolist()[::-1]
        
        selected_resi = st.selectbox(
            "Cari Nomor Resi:",
            options=list_resi,
            index=None,
            placeholder="Ketik atau pilih nomor resi..."
        )
        
        if selected_resi:
            hasil = df[df['No_Resi'].astype(str) == selected_resi]
            if not hasil.empty:
                row = hasil.iloc[0]
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.info(f"**Customer:** {row['Customer']}")
                with c2: st.info(f"**Tujuan:** {row['Destination']}")
                with c3: 
                    total_val = float(row['Total']) if str(row['Total']).replace('.','').isdigit() else 0
                    st.info(f"**Total:** Rp {total_val:,.0f}".replace(",", "."))
                
                pdf_bytes = generate_pdf(row)
                st.download_button(
                    label="📥 Download Invoice PDF",
                    data=pdf_bytes,
                    file_name=f"Invoice_{selected_resi.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.warning("Data tidak ditemukan di Google Sheets. Pastikan kolom di GSheet sudah benar.")

with tab2:
    st.success("### 📝 Cara Menambah Data Baru secara Online")
    st.write("Karena aplikasi ini berjalan online, Anda bisa menginput data langsung ke Google Sheets agar tersimpan permanen.")
    
    st.link_button("📂 Buka Google Sheets (Database)", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit", use_container_width=True)
    
    st.info("""
    **Langkah-langkah:**
    1. Klik tombol di atas untuk membuka Google Sheets.
    2. Masukkan data pengiriman baru di baris paling bawah.
    3. Kembali ke aplikasi ini dan buka Tab **Cek & Cetak Invoice**.
    4. Nomor resi baru akan otomatis muncul di daftar pilihan.
    """)
