import streamlit as st
from PIL import Image
import pandas as pd

# 1. KONFIGURASI HALAMAN
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

# 2. INISIALISASI STATE
if 'preview' not in st.session_state:
    st.session_state.preview = False

# 3. SIDEBAR INPUT
with st.sidebar:
    st.header("Input Data Invoice")
    
    cust_name = st.text_input("Customer", value="PT HARVI")
    inv_date = st.text_input("Tanggal Invoice", value="8/12/2024")
    
    st.subheader("Detail Barang")
    load_date = st.text_input("Date of Load", value="8-Dec-24")
    prod_desc = st.text_area("Product Description", value="3 UNIT CDD")
    origin = st.text_input("Origin", value="TUAL")
    dest = st.text_input("Destination", value="LARAT")
    price = st.number_input("Harga (Rp)", min_value=0, value=27000000)
    terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah")
    
    st.markdown("---")
    if st.button("Preview Invoice", use_container_width=True):
        st.session_state.preview = True
    
    if st.button("Reset Form", use_container_width=True):
        st.session_state.preview = False
        st.rerun()

# 4. TAMPILAN UTAMA (PREVIEW)
if st.session_state.preview:
    try:
        st.image("HEADER INVOICE.png", use_container_width=True)
    except:
        st.error("File HEADER INVOICE.png tidak ditemukan.")

    st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True)
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write(f"**CUSTOMER:** {cust_name}")
    with col_info2:
        st.write(f"**DATE:** {inv_date}")

    # [cite_start]Tabel Rincian [cite: 5]
    df_data = {
        "Date of Load": [load_date],
        "Product Description": [prod_desc],
        "Origin": [origin],
        "Destination": [dest],
        "Harga": [f"Rp {price:,.0f}"]
    }
    st.table(pd.DataFrame(df_data))

    st.write(f"**YANG HARUS DIBAYAR: Rp {price:,.0f}**")
    st.write(f"*Terbilang: {terbilang}*")

    st.markdown("---")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.write("**TRANSFER TO :**")
        st.write("Bank Central Asia (BCA)")
        st.write("6720422334")
        st.write("A/N ADITYA GAMA SAPUTRI")
        st.write("Finance: 081217833322")
    
    with col_f2:
        st.write("Sincerely,")
        st.write("PT. GAMA GEMAH GEMILANG")
        st.write("##")
        st.write("##") 
        st.write(f"**KELVINITO JAYADI**")
        st.write("DIREKTUR")

    st.info("💡 Tekan **Ctrl + P** untuk simpan sebagai PDF.")
else:
    st.info("Silakan isi data di panel kiri, lalu klik 'Preview Invoice'.")
