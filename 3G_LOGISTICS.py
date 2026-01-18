import streamlit as st
from PIL import Image
import pandas as pd

# 1. KONFIGURASI HALAMAN & PROTEKSI
st.set_page_config(page_title="3G Logistics - Generator Invoice", page_icon="FAVICON.png", layout="wide")

# CSS untuk Anti-Download & Tampilan Cetak
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    @media print {
        .no-print { display: none !important; }
        .stButton { display: none !important; }
    }
    .invoice-box {
        padding: 20px;
        border: 1px solid #eee;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNGSI RESET
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

def reset_form():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# 3. SIDEBAR INPUT (INPUT MANUAL)
with st.sidebar:
    st.header("Input Data Invoice")
    cust_name = st.text_input("Customer", placeholder="Contoh: PT HARVI") [cite: 3]
    inv_date = st.text_input("Tanggal Invoice", value="8/12/2024") [cite: 13]
    
    st.subheader("Detail Barang")
    load_date = st.text_input("Date of Load", value="8-Dec-24") [cite: 5]
    prod_desc = st.text_area("Product Description", value="3 UNIT CDD") [cite: 5]
    origin = st.text_input("Origin", value="TUAL") [cite: 5]
    dest = st.text_input("Destination", value="LARAT") [cite: 5]
    price = st.number_input("Harga (Rp)", min_value=0, value=27000000, step=1000) [cite: 5]
    terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah") [cite: 6]
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button("Reset Form", on_click=reset_form, use_container_width=True)
    with col_btn2:
        preview_mode = st.checkbox("Preview Invoice")

# 4. TAMPILAN UTAMA (PREVIEW INVOICE)
if preview_mode:
    # Header dari File Anda
    st.image("HEADER INVOICE.png", use_container_width=True)
    
    # Informasi Perusahaan (Opsional jika sudah ada di Header Gambar)
    st.write(f"**CUSTOMER:** {cust_name}") [cite: 3]
    st.write(f"**DATE:** {inv_date}") [cite: 13]
    st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True) [cite: 4]

    # Tabel Data
    data = {
        "Date of Load": [load_date],
        "Product Description": [prod_desc],
        "Origin": [origin],
        "Destination": [dest],
        "Harga": [f"Rp {price:,.0f}"]
    }
    df = pd.DataFrame(data)
    st.table(df) [cite: 5]

    # Total & Terbilang
    col_t1, col_t2 = st.columns([2, 1])
    with col_t2:
        st.write(f"**TOTAL BAYAR: Rp {price:,.0f}**") [cite: 5]
    st.write(f"*Terbilang: {terbilang}*") [cite: 6]

    # Informasi Bank & Tanda Tangan
    st.markdown("---")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.write("**TRANSFER TO :**") [cite: 7]
        st.write("Bank Central Asia (BCA)") [cite: 8]
        st.write("Acc No: 6720422334") [cite: 9]
        st.write("A/N: ADITYA GAMA SAPUTRI") [cite: 10]
        st.write("Konfirmasi Finance: 081217833322") [cite: 12]
    
    with col_f2:
        st.write(f"Surabaya, {inv_date}")
        st.write("Sincerely,") [cite: 14]
        st.write("PT. GAMA GEMAH GEMILANG") [cite: 15]
        st.write("##")
        st.write("##") # Ruang tanda tangan manual
        st.write(f"**KELVINITO JAYADI**") [cite: 16]
        st.write("DIREKTUR") [cite: 17]

    # Tombol Cetak
    st.markdown("---")
    if st.button("Cetak / Simpan PDF", use_container_width=True):
        st.info("Gunakan Ctrl+P (Windows) atau Cmd+P (Mac) untuk menyimpan sebagai PDF.")
else:
    st.info("Silakan isi data di sidebar kiri dan centang 'Preview Invoice' untuk melihat hasil.")
