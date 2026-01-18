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
    
    /* Agar saat dicetak, tombol dan input tidak ikut muncul */
    @media print {
        .no-print, .stButton, [data-testid="stForm"] { display: none !important; }
        .main { background-color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INISIALISASI STATE
if 'preview' not in st.session_state:
    st.session_state.preview = False

# 3. AREA INPUT UTAMA (DI HALAMAN TENGAH)
if not st.session_state.preview:
    st.image("HEADER INVOICE.png", use_container_width=True)
    st.title("Buat Invoice Baru")
    
    with st.form("invoice_form"):
        col1, col2 = st.columns(2)
        with col1:
            [cite_start]cust_name = st.text_input("Customer", value="PT HARVI") [cite: 3]
            no_inv = st.text_input("Nomor Invoice", placeholder="Contoh: 001/INV/3G/2024")
        with col2:
            [cite_start]inv_date = st.text_input("Tanggal Invoice", value="8/12/2024") [cite: 13]
            [cite_start]load_date = st.text_input("Date of Load", value="8-Dec-24") [cite: 5]

        st.subheader("Detail Pengiriman")
        col3, col4 = st.columns(2)
        with col3:
            [cite_start]origin = st.text_input("Origin", value="TUAL") [cite: 5]
            [cite_start]dest = st.text_input("Destination", value="LARAT") [cite: 5]
        with col4:
            [cite_start]price = st.number_input("Harga (Rp)", min_value=0, value=27000000) [cite: 5]
            [cite_start]terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah") [cite: 6]
        
        [cite_start]prod_desc = st.text_area("Product Description", value="3 UNIT CDD") [cite: 5]

        st.markdown("---")
        submit_btn = st.form_submit_button("Preview Invoice", use_container_width=True)
        
        if submit_btn:
            st.session_state.cust_name = cust_name
            st.session_state.inv_date = inv_date
            st.session_state.load_date = load_date
            st.session_state.prod_desc = prod_desc
            st.session_state.origin = origin
            st.session_state.dest = dest
            st.session_state.price = price
            st.session_state.terbilang = terbilang
            st.session_state.preview = True
            st.rerun()

# 4. TAMPILAN PREVIEW (SIAP CETAK)
else:
    # Tombol Kembali & Reset (Hanya muncul di layar, tidak saat di-print)
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⬅️ Kembali Edit Data", use_container_width=True):
            st.session_state.preview = False
            st.rerun()
    with col_nav2:
        if st.button("🔄 Buat Invoice Baru (Reset)", use_container_width=True):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    st.markdown("---")

    # Konten Invoice
    [cite_start]st.image("HEADER INVOICE.png", use_container_width=True) [cite: 4]
    
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        [cite_start]st.write(f"**CUSTOMER:** {st.session_state.cust_name}") [cite: 3]
    with col_prev2:
        [cite_start]st.write(f"**DATE:** {st.session_state.inv_date}") [cite: 13]

    [cite_start]st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True) [cite: 4]

    # Tabel Data
    df_data = {
        "Date of Load": [st.session_state.load_date],
        "Product Description": [st.session_state.prod_desc],
        "Origin": [st.session_state.origin],
        "Destination": [st.session_state.dest],
        "Harga": [f"Rp {st.session_state.price:,.0f}"]
    }
    [cite_start]st.table(pd.DataFrame(df_data)) [cite: 5]

    [cite_start]st.write(f"**YANG HARUS DIBAYAR: Rp {st.session_state.price:,.0f}**") [cite: 5]
    [cite_start]st.write(f"*Terbilang: {st.session_state.terbilang}*") [cite: 6]

    # Info Bank & Tanda Tangan
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
        st.write("##") 
        [cite_start]st.write(f"**KELVINITO JAYADI**") [cite: 16]
        [cite_start]st.write("DIREKTUR") [cite: 17]

    st.info("💡 Tekan **Ctrl + P** untuk simpan sebagai PDF.")
