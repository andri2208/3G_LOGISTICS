import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
from num2words import num2words

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Auto Generator", page_icon="FAVICON.png", layout="wide")

# CSS ANTI-DOWNLOAD & TAMPILAN CETAK
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    header { visibility: hidden; }
    @media print {
        .no-print, .stButton, [data-testid="stForm"], [data-testid="stHeader"] { display: none !important; }
        .main { background-color: white !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# FUNGSI TERBILANG (RUPIAH)
def format_terbilang(angka):
    try:
        hasil = num2words(angka, lang='id')
        return hasil.title() + " Rupiah"
    except:
        return "-"

# 2. INISIALISASI STATE
if 'preview' not in st.session_state:
    st.session_state.preview = False

# 3. HALAMAN INPUT
if not st.session_state.preview:
    try:
        st.image("HEADER INVOICE.png", use_container_width=True)
    except:
        pass
        
    st.title("Input Data Invoice")
    
    # OTOMATISASI DATA AWAL
    tgl_sekarang = datetime.now().strftime("%d/%m/%Y")
    # Contoh format No Invoice otomatis: INV/20260119/001 (Bisa diubah manual jika perlu)
    no_inv_auto = f"INV/{datetime.now().strftime('%Y%m%d')}/001"

    with st.form("invoice_form"):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input("Customer", value="PT HARVI")
            no_inv = st.text_input("Nomor Invoice", value=no_inv_auto)
        with c2:
            inv_date = st.text_input("Tanggal Invoice", value=tgl_sekarang)
            load_date = st.text_input("Date of Load", value=datetime.now().strftime("%d-%b-%y"))

        st.subheader("Rincian Barang & Perhitungan Harga")
        c3, c4 = st.columns(2)
        with c3:
            origin = st.text_input("Origin", value="TUAL")
            dest = st.text_input("Destination", value="LARAT")
            prod_desc = st.text_area("Product Description", value="3 UNIT CDD")
        with c4:
            # INPUT UNTUK PERHITUNGAN OTOMATIS
            berat = st.number_input("Weight / Unit / Kolli", min_value=1, value=1)
            harga_satuan = st.number_input("Harga Satuan (Rp)", min_value=0, value=27000000)
            
            # TOTAL OTOMATIS
            total_harga = berat * harga_satuan
            st.write(f"**Total Harga Otomatis:** Rp {total_harga:,.0f}")
            
            # TERBILANG OTOMATIS
            terbilang_auto = format_terbilang(total_harga)
            st.info(f"**Terbilang:** {terbilang_auto}")

        st.markdown("---")
        if st.form_submit_button("Preview Invoice", use_container_width=True):
            st.session_state.data = {
                "cust": cust_name, "inv": no_inv, "date": inv_date,
                "load": load_date, "prod": prod_desc, "ori": origin,
                "dest": dest, "total": total_harga, "said": terbilang_auto,
                "weight": berat, "price": harga_satuan
            }
            st.session_state.preview = True
            st.rerun()

# 4. HALAMAN PREVIEW (SIAP CETAK)
else:
    col_nav = st.columns(2)
    if col_nav[0].button("⬅️ Edit Data"):
        st.session_state.preview = False
        st.rerun()
    if col_nav[1].button("🔄 Reset / Baru"):
        st.session_state.preview = False
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.image("HEADER INVOICE.png", use_container_width=True)
    
    col_pr1, col_pr2 = st.columns(2)
    col_pr1.write(f"**CUSTOMER:** {st.session_state.data['cust']}")
    col_pr2.write(f"**DATE:** {st.session_state.data['date']}")

    st.markdown("<h2 style='text-align: center;'>INVOICE</h2>", unsafe_allow_html=True)
    st.write(f"**No. Invoice:** {st.session_state.data['inv']}")

    # Tabel Rincian
    df = pd.DataFrame({
        "Date of Load": [st.session_state.data['load']],
        "Product Description": [st.session_state.data['prod']],
        "Origin": [st.session_state.data['ori']],
        "Destination": [st.session_state.data['dest']],
        "Weight/Qty": [st.session_state.data['weight']],
        "Total Harga": [f"Rp {st.session_state.data['total']:,.0f}"]
    })
    st.table(df)

    st.write(f"### YANG HARUS DIBAYAR: Rp {st.session_state.data['total']:,.0f}")
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
