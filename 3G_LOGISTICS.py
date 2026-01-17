import streamlit as st
import pandas as pd
import base64
import os

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# 2. FUNGSI UNTUK GAMBAR & TERBILANG
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

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

# 3. DATABASE SESSION (Agar data tidak hilang saat pindah tab)
if 'db_3g' not in st.session_state:
    st.session_state.db_3g = pd.DataFrame(columns=['Resi','Tgl','Customer','Barang','Asal','Tujuan','Harga','Berat'])

# 4. TAMPILAN TAB
tab1, tab2 = st.tabs(["📝 INPUT DATA", "🖨️ CETAK INVOICE"])

# --- TAB INPUT ---
with tab1:
    st.subheader("Form Input Invoice")
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No Resi", value="INV/2025/001")
            tgl = st.text_input("Tanggal", value="29-Des-25")
            cust = st.text_input("Nama Customer", value="BAPAK ANDI")
            item = st.text_area("Deskripsi Barang", value="SATU SET ALAT TAMBANG")
        with c2:
            asal = st.text_input("Origin", value="SBY")
            tuju = st.text_input("Destination", value="MEDAN")
            hrg = st.number_input("Harga Satuan", value=8500)
            brt = st.number_input("Berat (Kg)", value=290.0)
        
        if st.form_submit_button("Simpan Data"):
            new_row = pd.DataFrame([{'Resi':resi,'Tgl':tgl,'Customer':cust,'Barang':item,'Asal':asal,'Tujuan':tuju,'Harga':hrg,'Berat':brt}])
            st.session_state.db_3g = pd.concat([st.session_state.db_3g, new_row], ignore_index=True)
            st.success("Data Tersimpan!")

# --- TAB CETAK ---
with tab2:
    if st.session_state.db_3g.empty:
        st.warning("Belum ada data.")
    else:
        pilih = st.selectbox("Pilih Resi", st.session_state.db_3g['Resi'].unique())
        d = st.session_state.db_3g[st.session_state.db_3g['Resi'] == pilih].iloc[0]
        total = d['Harga'] * d['Berat']
        
        # Load Gambar (Logo, TTD, Stempel)
        logo = get_image_base64("3G.png")
        ttd = get_image_base64("TANDA TANGAN.png")
        stempel = get_image_base64("STEMPEL DAN NAMA.png")

        # HTML INVOICE (Sesuai PDF)
        invoice_html = f"""
        <div style="background: white; color: black; padding: 40px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 140px;"><img src="data:image/png;base64,{logo}" width="130"></td>
                    <td style="vertical-align: middle;">
                        <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432</p>
                    </td>
                    <td style="text-align:right; vertical-align:top;">
                        <h1 style="margin:0; color:red;">INVOICE</h1>
                        <p><b>DATE: {d['Tgl']}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size:16px;"><b>CUSTOMER: {str(d['Customer']).upper()}</b></p>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <tr style="background: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">HARGA</th>
                    <th style="border: 1px solid black;">WEIGHT</th>
                    <th style="border: 1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 15px;">{d['Tgl']}</td>
                    <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{d['Barang']}</td>
                    <td style="border: 1px solid black;">{d['Asal']}</td>
                    <td style="border: 1px solid black;">{d['Tujuan']}</td>
                    <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                    <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total:,.0f}</td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:red;">Rp {total:,.0f}</span></h3>
                <p><i>Terbilang: {terbilang(total)} Rupiah</i></p>
            </div>
            <table style="width: 100%; margin-top: 40px;">
                <tr>
                    <td style="width: 60%; vertical-align: top; font-size: 12px;">
                        <b>TRANSFER TO :</b><br>Bank BCA | No Rek: 6720422334 [cite: 14]<br>A/N ADITYA GAMA SAPUTRI [cite: 15]<br>
                        <small>NB: Konfirmasi ke Finance 082179799200 [cite: 16]</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b> [cite: 18]<br>
                        <div style="position: relative; height: 100px; width: 180px; margin: auto;">
                            <img src="data:image/png;base64,{ttd}" style="position: absolute; width: 90px; left: 45px; top: 15px; z-index: 1;">
                            <img src="data:image/png;base64,{stempel}" style="position: absolute; width: 150px; left: 15px; top: -5px; z-index: 2; opacity: 0.8;">
                        </div>
                        <br><b>KELVINITO JAYADI</b> [cite: 19]<br>DIREKTUR [cite: 20]
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(invoice_html, unsafe_allow_html=True)
