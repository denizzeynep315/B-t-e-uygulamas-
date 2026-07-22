import streamlit as st
import pandas as pd
import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="Aile Bütçe Asistanı", page_icon="💸", layout="wide")

# Hafıza İlkleme
if 'harcamalar' not in st.session_state:
    st.session_state.harcamalar = pd.DataFrame(columns=["Tarih", "Kişi", "Kategori", "Miktar", "Açıklama"])

if 'butce' not in st.session_state:
    st.session_state.butce = 30000.0

# ESPRİLİ TELKİN MOTORU
def esprili_mesaj_uret(toplam_harcama, butce):
    kalan = butce - toplam_harcama
    oran = kalan / butce if butce > 0 else 0

    if kalan < 0:
        return f"🚨 **EYVAH EYVAH!** Bütçe {abs(kalan):,.2f} TL aşıldı! Arkadaşlar bu ay sonu çorba içiyoruz, kemerleri bağlayın!"
    elif oran <= 0.10:
        return f"⚠️ **SARI ALARM!** Kalan: **{kalan:,.2f} TL**. Bakiyeniz son nefesini veriyor. Telefonu yavaşça yere bırakın ve alışveriş sitesinden çıkın!"
    elif oran <= 0.25:
        return f"👀 **DİKKAT!** Kalan: **{kalan:,.2f} TL**. Ayın sonuna yaklaştık ve limit alarm veriyor! Kahveyi dışarıdan değil evden içme vakti..."
    elif oran <= 0.50:
        return f"⚖️ **YARI YOL:** Kalan: **{kalan:,.2f} TL**. Bütçenin yarısı gitti bile. Hızınızı biraz azaltın!"
    else:
        return f"🎉 **HARİKA GİDİYORSUNUZ!** Kalan: **{kalan:,.2f} TL**. Finansal gurular sizinle gurur duyuyor!"

# ARAYÜZ
st.title("💸 Aile Bütçe & Disiplin Asistanı")
st.markdown("---")

# Sol Panel
with st.sidebar:
    st.header("⚙️ Bütçe Ayarı")
    yeni_butce = st.number_input("Aylık Harcama Hedefi (TL):", value=float(st.session_state.butce), step=1000.0)
    st.session_state.butce = yeni_butce

    st.markdown("---")
    st.header("➕ Harcama Ekle")
    
    kisi = st.selectbox("Harcayan Kişi:", ["Eşim", "Ben"])
    kategori = st.selectbox("Kategori:", ["Market", "Fatura", "Dışarıda Yemek", "Eğlence/Aktivite", "Giyim", "Diğer"])
    tutar = st.number_input("Harcama Tutarı (TL):", min_value=0.0, step=10.0)
    aciklama = st.text_input("Açıklama (Örn: Kahve, Market vb.):")

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
            st.success("Harcama eklendi!")
            st.rerun()

# Ana Ekran
toplam_harcama = st.session_state.harcamalar["Miktar"].sum() if not st.session_state.harcamalar.empty else 0.0
kalan_butce = st.session_state.butce - toplam_harcama

col1, col2, col3 = st.columns(3)
col1.metric("Aylık Hedef Bütçe", f"{st.session_state.butce:,.2f} TL")
col2.metric("Yapılan Harcama", f"{toplam_harcama:,.2f} TL")
col3.metric("Kalan Bütçe", f"{kalan_butce:,.2f} TL")

st.markdown("### 📣 Asistanınızın Bu Ayki Yorumu")
st.info(esprili_mesaj_uret(toplam_harcama, st.session_state.butce))

st.markdown("---")

if not st.session_state.harcamalar.empty:
    st.subheader("📊 Harcama Dağılımı")
    st.bar_chart(st.session_state.harcamalar, x="Kategori", y="Miktar")

    st.subheader("📋 Harcama Geçmişi")
    st.dataframe(st.session_state.harcamalar, use_container_width=True)
