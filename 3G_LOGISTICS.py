import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# --- 2. FUNGSI LOAD GAMBAR (PENTING) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. FUNGSI TERBILANG ---
def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return str(n)

# --- 4. DATABASE SESSION ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Resi','Tgl','Cust','Item','Asal','Tuju','Koli','Hrg','Brt'])

# --- 5. NAVIGASI ---
st.title("3G LOGISTICS SYSTEM")
t1, t2 = st.tabs(["INPUT DATA", "CETAK INVOICE"])

with t1:
    with st.form("f1", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No Resi")
            tgl = st.date_input("Tanggal", value=datetime.now())
            cust = st.text_input("Customer")
            item = st.text_area("Deskripsi Barang")
        with c2:
            asal = st.text_input("Origin", value="SBY")
            tuju = st.text_input("Destination", value="MEDAN")
            koli = st.number_input("Kolli", min_value=1)
            hrg = st.number_input("Harga", min_value=0)
            brt = st.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN"):
            if resi and cust:
                row = pd.DataFrame([{'Resi':resi,'Tgl':tgl.strftime('%d-%b-%y'),'Cust':cust,'Item':item,'Asal':asal,'Tuju':tuju,'Koli':koli,'Hrg':hrg,'Brt':brt}])
                st.session_state.db = pd.concat([st.session_state.db, row], ignore_index=True)
                st.success("Tersimpan!")
            else:
                st.error("No Resi dan Customer tidak boleh kosong!")

with t2:
    if not st.session_state.db.empty:
        pilih = st.selectbox("Pilih Resi", st.session_state.db['Resi'].unique())
        d = st.session_state.db[st.session_state.db['Resi'] == pilih].iloc[0]
        
        # Perhitungan & Pencegahan Error
        total = float(d['Hrg']) * float(d['Brt'])
        cust_name = str(d['Cust']).upper() if d['Cust'] else ""
        
        # Load Gambar
        h_img = get_image_base64("HEADER-INVOCE.PNG")
        f_img = get_image_base64("STEMPEL-TANDA-TANGAN.PNG")

        invoice_html = f"""
        <div style="background:white; color:black; padding:20px; font-family:Arial; width:800px; margin:auto; border:1px solid #eee;">
            <img src="data:image/png;base64,{h_img}" style="width:100%;">
            <div style="text-align:right; margin-top:10px;">
                <h1 style="color:red; margin:0; font-size:30px;">INVOICE</h1>
                <p>DATE: {d['Tgl']}</p>
            </div>
            <p><b>CUSTOMER: {cust_name}</b></p>
            <table style="width:100%; border-collapse:collapse; border:1px solid black; text-align:center; font-size:12px;">
                <tr style="background:#f2f2f2;">
                    <th style="border:1px solid black; padding:8px;">Product Description</th>
                    <th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Dest</th>
                    <th style="border:1px solid black;">Harga</th>
                    <th style="border:1px solid black;">Weight</th>
                    <th style="border:1px solid black;">Total</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:15px; text-align:left;">{d['Item']}</td>
                    <td style="border:1px solid black;">{d['Asal']}</td>
                    <td style="border:1px solid black;">{d['Tuju']}</td>
                    <td style="border:1px solid black;">Rp {d['Hrg']:,}</td>
                    <td style="border:1px solid black;">{d['Brt']} Kg</td>
                    <td style="border:1px solid black;"><b>Rp {total:,.0f}</b></td>
                </tr>
            </table>
            <div style="text-align:right; margin-top:20px;">
                <h3 style="margin:0;">YANG HARUS DIBAYAR: <span style="color:red; font-size:22px;">Rp {total:,.0f}</span></h3>
                <p style="font-size:12px;"><i>Terbilang: {terbilang(total)} Rupiah</i></p>
            </div>
            <table style="width:100%; margin-top:30px; font-size:13px;">
                <tr>
                    <td style="width:60%;"><b>TRANSFER TO :</b><br>Bank BCA | 6720422334 | A/N ADITYA GAMA SAPUTRI</td>
                    <td style="text-align:center;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        <img src="data:image/png;base64,{f_img}" width="180"><br>
                        <b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        # Render desain
        st.markdown(invoice_html, unsafe_allow_html=True)
