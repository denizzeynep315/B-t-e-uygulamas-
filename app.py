import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from PIL import Image
import pytesseract
import re

# Sayfa Yapılandırması
st.set_page_config(page_title="Aile Bütçe & Esprili Takip", page_icon="💸", layout="wide")

# Session State (Veri Depolama) İlkleme
if 'harcamalar' not in st.session_state:
    st.session_state.harcamalar = pd.DataFrame(columns=["Tarih", "Kişi", "Kategori", "Miktar", "Açıklama"])

if 'butce' not in st.session_state:
    st.session_state.butce = 30000.0

# --- FİŞ OKUMA FONKSİYONU ---
def fis_oku(image):
    try:
        text = pytesseract.image_to_string(image, lang='tur')
        # Fiş üzerindeki en büyük veya "TOPLAM" kelimesinden sonra gelen tutarı bulma (Regex)
        tutarlar = re.findall(r'\d+[.,]\d{2}', text)
        if tutarlar:
            # En son veya en yüksek tutarı alalım (Genelde TOPLAM tutardır)
            tutar = float(tutarlar[-1].replace(',', '.'))
            return tutar, text
    except Exception as e:
        return None, str(e)
    return None, ""

# --- ESPRİLİ TELKİN MOTORU ---
def esprili_mesaj_uret(toplam_harcama, butce):
    kalan = butce - toplam_harcama
    oran = kalan / butce if butce > 0 else 0

    if kalan < 0:
        return f"🚨 **EYVAH EYVAH!** Bütçe {abs(kalan):,.2f} TL aşıldı! Arkadaşlar bu ay sonu çorba içiyoruz, kemerleri sıkın değil direkt bağlayın!"
    elif oran <= 0.10:
        return f"⚠️ **SARI ALARM!** Kalan: **{kalan:,.2f} TL**. Bakiyeniz son nefesini veriyor. Sakın o alışveriş sitesini kapatın ve telefonunuzu yavaşça yere bırakın!"
    elif oran <= 0.25:
        return f"👀 **DİKKAT!** Kalan: **{kalan:,.2f} TL**. Ayın sonuna yaklaştık ve limit alarm veriyor! Kahveyi dışarıdan değil evden içme vakti geldi..."
    elif oran <= 0.50:
        return f"⚖️ **YARI YOL:** Kalan: **{kalan:,.2f} TL**. Bütçenin yarısı gitti bile. Hızınızı biraz azaltın, virajı alamayabilirsiniz!"
    else:
        return f"🎉 **HARİKA GİDİYORSUNUZ!** Kalan: **{kalan:,.2f} TL**. Finansal gurular sizinle gurur duyuyor. Böyle devam!"

# --- ARAYÜZ (UI) ---
st.title("💸 Aile Bütçe & Disiplin Asistanı")
st.markdown("---")

# Sol Panel: Bütçe Ayarı ve Yeni Harcama Girişi
with st.sidebar:
    st.header("⚙️ Bütçe Ayarı")
    yeni_butce = st.number_input("Aylık Harcama Hedefi (TL):", value=float(st.session_state.butce), step=1000.0)
    st.session_state.butce = yeni_butce

    st.markdown("---")
    st.header("➕ Harcama Ekle")
    
    ekleme_yontemi = st.radio("Ekleme Yöntemi:", ["Manuel Giriş", "Fiş Fotoğrafı Yükle"])
    
    kisi = st.selectbox("Harcayan Kişi:", ["Eşim", "Ben"])
    kategori = st.selectbox("Kategori:", ["Market", "Fatura", "Dışarıda Yemek", "Eğlence/Aktivite", "Giyim", "Diğer"])
    
    tutar = 0.0
    aciklama = ""

    if ekleme_yontemi == "Manuel Giriş":
        tutar = st.number_input("Harcama Tutarı (TL):", min_value=0.0, step=10.0)
        aciklama = st.text_input("Açıklama (Örn: Kahve, Market vb.):")
    
    else:  # Fiş Yükleme
        uploaded_file = st.file_uploader("Fiş Görseli Seçin", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Yüklenen Fiş', use_container_width=True)
            
            okunan_tutar, raw_text = fis_oku(image)
            if okunan_tutar:
                st.success(f"Fişten algılanan tutar: {okunan_tutar} TL")
                tutar = st.number_input("Onaylanan Tutar (TL):", value=okunan_tutar)
            else:
                st.warning("Tutar otomatik okunamadı, lütfen elle girin.")
                tutar = st.number_input("Harcama Tutarı (TL):", min_value=0.0)
            
            aciklama = st.text_input("Açıklama:", value="Fiş ile eklendi")

    if st.button("Harcamayı Kaydet", use_container_width=True):
        if tutar > 0:
            yeni_veri = pd.DataFrame([{
                "Tarih": datetime.date.today().strftime("%Y-%m-%d"),
                "Kişi": kisi,
                "Kategori": kategori,
                "Miktar": tutar,
                "Açıklama": aciklama
            }])
            st.session_state.harcamalar = pd.concat([st.session_state.harcamalar, yeni_veri], ignore_index=True)
            st.success("Harcama başarıyla eklendi!")
            st.rerun()
        else:
            st.error("Lütfen geçerli bir tutar girin.")

# Ana Ekran: Özet ve Esprili Uyarılar
toplam_harcama = st.session_state.harcamalar["Miktar"].sum() if not st.session_state.harcamalar.empty else 0.0
kalan_butce = st.session_state.butce - toplam_harcama

# Üst Bilgi Kartları
col1, col2, col3 = st.columns(3)
col1.metric("Aylık Hedef Bütçe", f"{st.session_state.butce:,.2f} TL")
col2.metric("Yapılan Harcama", f"{toplam_harcama:,.2f} TL")
col3.metric("Kalan Bütçe", f"{kalan_butce:,.2f} TL", delta=f"{kalan_butce:,.2f} TL", delta_color="normal")

# 🤖 ESPRİLİ TELKİN KUTUSU
st.markdown("### 📣 Asistanınızın Bu Ayki Yorumu")
mesaj = esprili_mesaj_uret(toplam_harcama, st.session_state.butce)
st.info(mesaj)

st.markdown("---")

# Grafikler ve Detay Tablosu
if not st.session_state.harcamalar.empty:
    col_grafik1, col_grafik2 = st.columns(2)

    with col_grafik1:
        st.subheader("📊 Nereye Ne Harcadık? (Kategoriler)")
        fig_kat = px.pie(st.session_state.harcamalar, values='Miktar', names='Kategori', hole=0.4)
        st.plotly_chart(fig_kat, use_container_width=True)

    with col_grafik2:
        st.subheader("👥 Kim Ne Kadar Harcadı?")
        fig_kisi = px.bar(st.session_state.harcamalar, x='Kişi', y='Miktar', color='Kişi', barmode='group')
        st.plotly_chart(fig_kisi, use_container_width=True)

    st.subheader("📋 Harcama Geçmişi")
    st.dataframe(st.session_state.harcamalar, use_container_width=True)
else:
    st.write("Henüz bir harcama girilmedi. Sol taraftaki panelden ilk harcamanızı ekleyebilirsiniz!")
