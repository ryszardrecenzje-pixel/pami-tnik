import streamlit as st
from datetime import date
from supabase import create_client, Client
from pathlib import Path
import uuid

# ============================================
# Pobieranie kluczy z sekretów Streamlit
# ============================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# Funkcje
# ============================================
def upload_image(uploaded_file):
    """Wrzuca zdjęcie do Supabase Storage i zwraca publiczny link"""
    if uploaded_file is None:
        return None
    
    file_ext = Path(uploaded_file.name).suffix.lower()
    file_name = f"{uuid.uuid4()}{file_ext}"
    
    supabase.storage.from_("zdjecia").upload(
        file_name,
        uploaded_file.getvalue(),
        file_options={"content-type": uploaded_file.type}
    )
    
    public_url = supabase.storage.from_("zdjecia").get_public_url(file_name)
    return public_url

def load_entries():
    response = (
        supabase.table("wpisy")
        .select("*")
        .order("data", desc=True)
        .execute()
    )
    return response.data

def save_entry(data_wpisu, opis, lista_url_zdjec):
    supabase.table("wpisy").insert({
        "data": str(data_wpisu),
        "opis": opis,
        "zdjecia": lista_url_zdjec
    }).execute()

# ============================================
# Interfejs
# ============================================
st.set_page_config(
    page_title="Mój Dziennik",
    page_icon="📔",
    layout="wide"
)

st.title("📔 Mój Dziennik")

# --- Formularz dodawania wpisu ---
st.header("Dodaj nowy wpis")

with st.form("nowy_wpis", clear_on_submit=True):
    data_wpisu = st.date_input("Data", value=date.today())
    opis = st.text_area("Opis", height=150)
    zdjecia = st.file_uploader(
        "Dodaj zdjęcia",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )
    
    submitted = st.form_submit_button("Zapisz wpis ☁️")

    if submitted:
        if not opis.strip() and not zdjecia:
            st.warning("Dodaj przynajmniej opis albo zdjęcie.")
        else:
            with st.spinner("Zapisuję w chmurze..."):
                lista_url = []
                if zdjecia:
                    for zdj in zdjecia:
                        url = upload_image(zdj)
                        if url:
                            lista_url.append(url)
                
                save_entry(data_wpisu, opis.strip(), lista_url)
                st.success("Wpis zapisany!")
                st.rerun()

# --- Wyświetlanie wpisów ---
st.header("Twoje wpisy")

entries = load_entries()

if not entries:
    st.info("Jeszcze nie ma żadnych wpisów. Dodaj pierwszy powyżej!")
else:
    for wpis in entries:
        with st.container():
            st.subheader(f"📅 {wpis['data']}")
            
            if wpis.get("opis"):
                st.write(wpis["opis"])
            
            if wpis.get("zdjecia"):
                cols = st.columns(min(3, len(wpis["zdjecia"])))
                for idx, url in enumerate(wpis["zdjecia"]):
                    with cols[idx % 3]:
                        st.image(url, use_container_width=True)
            
            st.divider()
