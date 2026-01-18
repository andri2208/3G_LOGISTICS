import streamlit as st
from PIL import Image
import pandas as pd

# 1. KONFIGURASI HALAMAN (Harus di baris pertama)
st.set_page_config(page_title="3G Logistics - Generator Invoice", page_icon="FAVICON.png", layout="wide")

# CSS untuk Anti-Download & Tampilan Cetak
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    header { visibility: hidden; }
    @media print {
        .no-print, .stButton, [data-testid="stSidebar"] { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INISIALISASI STATE (Mencegah NameError)
if 'preview' not in st.session_state:
    st.session_state.preview = False

# 3. SIDEBAR INPUT
with st.sidebar:
    st.header("Input Data Invoice")
    
    # [cite_start]Input Manual [cite: 3, 5, 13]
    [cite_start]cust_name = st.text_input("Customer", value="PT HARVI") [cite: 3]
    [cite_start]inv_date = st.text_input("Tanggal Invoice", value="8/12/2024") [cite: 13]
    
    st.subheader("Detail Barang")
    [cite_start]load_date = st.text_input("Date of Load", value="8-Dec-24") [cite: 5]
    [cite_start]prod_desc = st.text_area("Product Description", value="3 UNIT CDD") [cite: 5]
    [cite_start]origin = st.text_input("Origin", value="TUAL") [cite: 5]
    [cite_start]dest = st.text_input("Destination", value="LARAT") [cite: 5]
    [cite_start]price = st.number_input("Harga (Rp)", min_value=0, value=27000000) [cite: 5]
    [cite_start]terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah") [cite: 6]
    
    st.markdown("---")
    if st.button("Preview Invoice", use_container_width=True):
        st.session_state.preview = True
    
    if st.button("Reset Form", use_container_width=True):
        st.session_state.preview = False
        st.rerun()

# 4. TAMPILAN UTAMA (PREVIEW)
if st.session_state.preview:
    # [cite_start]Header [cite: 1, 2]
    try:
        st.image("HEADER INVOICE.png", use_container_width=True)
    except:
        st.error("File HEADER INVOICE.png tidak ditemukan.")

    # [cite_start]Judul & Info [cite: 3, 4, 13]
    [cite_start]st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True) [cite: 4]
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        [cite_start]st.write(f"**CUSTOMER:** {cust_name}") [cite: 3]
    with col_info2:
        [cite_start]st.write(f"**DATE:** {inv_date}") [cite: 13]

    # [cite_start]Tabel [cite: 5]
    df_data = {
        "Date of Load": [load_date],
        "Product Description": [prod_desc],
        "Origin": [origin],
        "Destination": [dest],
        "Harga": [f"Rp {price:,.0f}"]
    }
    [cite_start]st.table(pd.DataFrame(df_data)) [cite: 5]

    # [cite_start]Total & Terbilang [cite: 5, 6]
    [cite_start]st.write(f"**YANG HARUS DIBAYAR: Rp {price:,.0f}**") [cite: 5]
    [cite_start]st.write(f"*Terbilang: {terbilang}*") [cite: 6]

    # [cite_start]Footer & Bank [cite: 7, 8, 9, 10, 11, 12, 14, 15, 16, 17]
    st.markdown("---")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        [cite_start]st.write("**TRANSFER TO :**") [cite: 7]
        [cite_start]st.write("Bank Central Asia (BCA)") [cite: 8]
        [cite_start]st.write("6720422334") [cite: 9]
        [cite_start]st.write("A/N ADITYA GAMA SAPUTRI") [cite: 10]
        [cite_start]st.write("Finance: 081217833322") [cite: 12]
    
    with col_f2:
        [cite_start]st.write("Sincerely,") [cite: 14]
        [cite_start]st.write("PT. GAMA GEMAH GEMILANG") [cite: 15]
        st.write("##")
        st.write("##") # Ruang tanda tangan manual tanpa gambar stempel
        [cite_start]st.write(f"**KELVINITO JAYADI**") [cite: 16]
        [cite_start]st.write("DIREKTUR") [cite: 17]

    st.button("Cetak (Ctrl+P)", on_click=None, help="Tekan Ctrl+P untuk simpan PDF")
else:
    st.info("Gunakan panel di sebelah kiri untuk mengisi data, lalu klik 'Preview Invoice'.")
