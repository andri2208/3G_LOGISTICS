import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
from num2words import num2words
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics - Invoice System", page_icon="FAVICON.png", layout="wide")

# CSS ANTI-DOWNLOAD & STYLE
st.markdown("""
    <style>
    img { pointer-events: none; } 
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }
    .invoice-container { border: 1px solid #ccc; padding: 40px; background-color: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

def format_terbilang(angka):
    if angka == 0: return "-"
    return num2words(int(angka), lang='id').title() + " Rupiah"

# 2. NOMOR INVOICE OTOMATIS
if 'inv_count' not in st.session_state:
    st.session_state.inv_count = 1
auto_no_inv = f"INV/{datetime.now().strftime('%Y%m%d')}/{str(st.session_state.inv_count).zfill(3)}"

# 3. SISTEM TAB
tab_input, tab_preview = st.tabs(["📝 Input Data", "👁️ Preview & Download"])

with tab_input:
    st.header("Formulir Invoice")
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input("Customer", value="", placeholder="Contoh: BAPAK ANDI")
            inv_date = st.date_input("Tanggal Invoice", datetime.now())
        with c2:
            no_inv = st.text_input("Nomor Invoice", value=auto_no_inv)
            load_date = st.date_input("Date of Load", datetime.now())

        st.subheader("Rincian Pengiriman")
        c3, c4 = st.columns(2)
        with c3:
            prod_desc = st.text_area("Product Description", placeholder="Contoh: SATU SET ALAT TAMBANG")
            origin = st.text_input("Origin (Asal)", value="SBY")
            dest = st.text_input("Destination (Tujuan)", value="MEDAN")
        with c4:
            kolli = st.text_input("Kolli", value="")
            weight = st.number_input("Weight (Kg)", min_value=0.0, step=0.1)
            price_kg = st.number_input("Harga per Kg (Rp)", min_value=0, step=500)
            
            # Hitung Total Otomatis
            total_calc = int(weight * price_kg)
            st.metric("Total Bayar", f"Rp {total_calc:,.0f}")
            terbilang_calc = format_terbilang(total_calc)
            st.caption(f"Terbilang: {terbilang_calc}")

        if st.form_submit_button("Simpan & Lihat Preview"):
            st.session_state.data = {
                "cust": cust_name, "inv": no_inv, "date": inv_date.strftime("%d/%m/%Y"),
                "load": load_date.strftime("%d-%b-%y"), "prod": prod_desc, "ori": origin,
                "dest": dest, "kolli": kolli, "weight": weight, "price": price_kg,
                "total": total_calc, "said": terbilang_calc
            }
            st.success("Data disimpan! Silakan buka Tab Preview.")

with tab_preview:
    if 'data' in st.session_state:
        d = st.session_state.data
        
        # Tampilan Invoice Visual (Seperti Hasil Cetak)
        st.markdown('<div class="invoice-container">', unsafe_allow_html=True)
        try:
            st.image("HEADER INVOICE.png", use_container_width=True)
        except: pass
        
        st.markdown(f"**CUSTOMER:** {d['cust']}")
        st.markdown(f"**DATE:** {d['date']}")
        st.markdown("<h3 style='text-align: center;'>INVOICE</h3>", unsafe_allow_html=True)
        
        # Tabel sesuai contoh Bapak Andi
        df_display = pd.DataFrame({
            "Date of Load": [d['load']],
            "Product Description": [d['prod']],
            "Origin": [d['ori']],
            "Destination": [d['dest']],
            "Kolli": [d['kolli']],
            "Harga/Kg": [f"Rp {d['price']:,.0f}"],
            "Weight": [f"{d['weight']} Kg"],
            "Total": [f"Rp {d['total']:,.0f}"]
        })
        st.table(df_display)
        
        st.markdown(f"**YANG HARUS DI BAYAR: Rp {d['total']:,.0f}**")
        st.markdown(f"*Terbilang: {d['said']}*")
        
        st.write("---")
        f1, f2 = st.columns(2)
        with f1:
            st.write("**TRANSFER TO :**")
            st.write("Bank Central Asia (BCA) - 6720422334")
            st.write("A/N ADITYA GAMA SAPUTRI")
            st.write("Finance: 082179799200")
        with f2:
            st.write(f"Surabaya, {d['date']}")
            st.write("Sincerely, PT. GAMA GEMAH GEMILANG")
            st.write("##")
            st.write(f"**KELVINITO JAYADI**")
            st.write("DIREKTUR")
        st.markdown('</div>', unsafe_allow_html=True)

        # Tombol Download PDF (Sederhana)
        if st.button("Download PDF"):
            st.info("Fitur cetak PDF sedang menyiapkan file...")
            # (Fungsi generate_pdf bisa Anda tambahkan seperti di pesan sebelumnya)
    else:
        st.warning("Silakan isi data di Tab Input terlebih dahulu.")
