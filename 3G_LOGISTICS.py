import streamlit as st
from PIL import Image
import pandas as pd

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Generator Invoice", page_icon="FAVICON.png", layout="wide")

# CSS UNTUK ANTI-DOWNLOAD & TAMPILAN CETAK
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    @media print {
        .no-print, .stButton, [data-testid="stForm"], [data-testid="stHeader"] { 
            display: none !important; 
        }
        .main { background-color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INISIALISASI STATE
if 'preview' not in st.session_state:
    st.session_state.preview = False

# 3. HALAMAN INPUT (TAMPILAN UTAMA)
if not st.session_state.preview:
    try:
        st.image("HEADER INVOICE.png", use_container_width=True)
    except:
        pass
        
    st.title("Input Data Invoice")
    
    with st.form("invoice_form"):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input("Customer", value="PT HARVI")
            no_inv = st.text_input("Nomor Invoice", value="001/INV/3G/2024")
        with c2:
            inv_date = st.text_input("Tanggal Invoice", value="8/12/2024")
            load_date = st.text_input("Date of Load", value="8-Dec-24")

        st.subheader("Rincian Barang & Harga")
        c3, c4 = st.columns(2)
        with c3:
            origin = st.text_input("Origin", value="TUAL")
            dest = st.text_input("Destination", value="LARAT")
        with c4:
            price = st.number_input("Harga (Rp)", min_value=0, value=27000000)
            terbilang = st.text_input("Terbilang", value="Dua puluh tujuh juta rupiah")
        
        prod_desc = st.text_area("Product Description", value="3 UNIT CDD")

        st.markdown("---")
        if st.form_submit_button("Preview Invoice", use_container_width=True):
            st.session_state.data = {
                "cust": cust_name, "inv": no_inv, "date": inv_date,
                "load": load_date, "prod": prod_desc, "ori": origin,
                "dest": dest, "price": price, "said": terbilang
            }
            st.session_state.preview = True
            st.rerun()

# 4. HALAMAN PREVIEW (TAMPILAN INVOICE)
else:
    # Tombol Navigasi (Hanya muncul di layar)
    col_nav = st.columns(2)
    if col_nav[0].button("⬅️ Edit Data"):
        st.session_state.preview = False
        st.rerun()
    if col_nav[1].button("🔄 Reset / Baru"):
        st.session_state.preview = False
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # Konten Cetak
    st.image("HEADER INVOICE.png", use_container_width=True)
    
    col_pr1, col_pr2 = st.columns(2)
    col_pr1.write(f"**CUSTOMER:** {st.session_state.data['cust']}")
    col_pr2.write(f"**DATE:** {st.session_state.data['date']}")

    st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True)

    # Tabel Berdasarkan Data PDF
    df = pd.DataFrame({
        "Date of Load": [st.session_state.data['load']],
        "Product Description": [st.session_state.data['prod']],
        "Origin": [st.session_state.data['ori']],
        "Destination": [st.session_state.data['dest']],
        "Harga": [f"Rp {st.session_state.data['price']:,.0f}"]
    })
    st.table(df)

    st.write(f"**TOTAL BAYAR: Rp {st.session_state.data['price']:,.0f}**")
    st.write(f"*Terbilang: {st.session_state.data['said']}*")

    st.markdown("---")
    f1, f2 = st.columns(2)
    with f1:
        st.write("**TRANSFER TO :**")
        st.write("Bank Central Asia (BCA) - 6720422334")
        st.write("A/N ADITYA GAMA SAPUTRI")
        st.write("Finance: 081217833322")
    
    with f2:
        st.write(f"Surabaya, {st.session_state.data['date']}")
        st.write("Sincerely, PT. GAMA GEMAH GEMILANG")
        st.write("##")
        st.write("##") 
        st.write(f"**KELVINITO JAYADI**")
        st.write("DIREKTUR")

    st.info("💡 Tekan **Ctrl + P** untuk simpan sebagai PDF.")
