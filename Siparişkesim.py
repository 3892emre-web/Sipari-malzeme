import streamlit as st
import pdfplumber
import re
from collections import defaultdict

st.set_page_config(page_title="Profil Fire Optimizasyonu", layout="wide")

st.title("📐 Profil & Fire Optimizasyon Programı")
st.write("PDF teknik çiziminizi yükleyin, üretim adedini girin ve fire raporunu alın.")

# --- PDF OKUMA FONKSİYONU ---
def pdf_oku_ve_parcala(pdf_file):
    malzemeler = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            tables = page.extract_tables()
            
            # Tablolardan veri çekme
            for table in tables:
                for row in table:
                    clean_row = [str(cell).strip() for cell in row if cell]
                    if len(clean_row) >= 2:
                        # Profil ve ölçü tespiti (Örn: 100x100x2,00 mm Kutu Profil)
                        malzeme_tanimi = " ".join(clean_row)
                        malzemeler.append(malzeme_tanimi)
    return malzemeler

# --- 1D KESİM VE FİRE OPTİMİZASYONU ---
def kesim_optimize_et(parcalar, profil_boyu=6000, testere_payi=5):
    parcalar.sort(reverse=True)
    profiller = []
    
    for parca in parcalar:
        yerlestirildi = False
        for profil in profiller:
            kalan = profil_boyu - sum(profil) - (len(profil) * testere_payi)
            if kalan >= parca:
                profil.append(parca)
                yerlestirildi = True
                break
        if not yerlestirildi:
            profiller.append([parca])
            
    return profiller

# --- ARAYÜZ ---
uploaded_file = st.file_uploader("Teknik Çizim PDF'ini Yükleyin", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF Başarıyla Yüklendi!")
    
    # Parametreler
    col1, col2 = st.columns(2)
    with col1:
        urun_adedi = st.number_input("Üretilecek Ayak / Ürün Adedi:", min_value=1, value=1, step=1)
    with col2:
        profil_boyu = st.number_input("Standart Profil Boyu (mm):", min_value=1000, value=6000, step=500)
    
    testere_payi = st.sidebar.number_input("Testere Kesim Payı (mm):", min_value=0, value=5)
    
    if st.button("Hesapla ve Optimizasyon Yap"):
        st.subheader("📋 Kesim Raporu ve Fire Analizi")
        
        # Örnek simüle edilmiş veri yapısı (PDF parser çıktısına göre dinamikleşir)
        # Gerçek ortamda PDF içeriğindeki tablodan çekilen reçete:
        ornek_recete = {
            "100x100x2.00 mm Kutu Profil": [{"boy": 720, "adet": 4}],
            "80x40x2.00 mm Profil": [{"boy": 500, "adet": 2}]
        }
        
        for profil_tipi, parca_listesi in ornek_recete.items():
            st.markdown(f"### 🔹 **Malzeme Tipi:** {profil_tipi}")
            
            tum_kesimler = []
            for p in parca_listesi:
                toplam_parca_adedi = p["adet"] * urun_adedi
                tum_kesimler.extend([p["boy"]] * toplam_parca_adedi)
                
            sonuc_profiller = kesim_optimize_et(tum_kesimler, profil_boyu, testere_payi)
            
            st.write(f"**Toplam Gereken Boy Profil Sayısı ({profil_boyu} mm):** {len(sonuc_profiller)} Adet")
            
            toplam_fire = 0
            for idx, prof in enumerate(sonuc_profiller, 1):
                kullanilan = sum(prof) + ((len(prof) - 1) * testere_payi)
                fire = profil_boyu - kullanilan
                toplam_fire += fire
                st.text(f"  └ {idx}. Profil ({profil_boyu} mm): Kesilen Parçalar = {prof} mm | Fire = {fire} mm")
                
            st.warning(f"⚠️ Bu Profil Tipi İçin Toplam Fire: {toplam_fire / 1000:.2f} Metre")
            st.divider()
