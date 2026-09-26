import streamlit as st
from datetime import date
import json
import os
from pathlib import Path
from PIL import Image

# === KONFIGURACJA ===
DATA_FILE = "dziennik.json"
IMAGES_DIR = Path("zdjecia")
IMAGES_DIR.mkdir(exist_ok=True)

# === FUNKCJE POMOCNICZE ===
def load_entries():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def save_image(uploaded_file):
    """Zapisuje zdjęcie i zwraca ścieżkę"""
    if uploaded_file is None:
        return None
    file_path = IMAGES_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)

# === INTERFEJS ===
st.set_page_config(page_title="Mój Dziennik", page_icon="📔")
st.title("📔 Mój Dziennik")

# --- Formularz dodawania wpisu ---
st.header("Dodaj nowy wpis")

with st.form("nowy_wpis", clear_on_submit=True):
    data_wpisu = st.date_input("Data", value=date.today())
    opis = st.text_area("Opis / co się wydarzyło", height=150)
    zdjecia = st.file_uploader(
        "Dodaj zdjęcia (możesz wybrać kilka)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )
    
    submitted = st.form_submit_button("Zapisz wpis")

    if submitted:
        if not opis.strip() and not zdjecia:
            st.warning("Dodaj przynajmniej opis albo zdjęcie.")
        else:
            entries = load_entries()
            
            # zapisujemy zdjęcia
            sciezki_zdjec = []
            if zdjecia:
                for zdjecie in zdjecia:
                    sciezka = save_image(zdjecie)
                    if sciezka:
                        sciezki_zdjec.append(sciezka)
            
            nowy_wpis = {
                "data": str(data_wpisu),
                "opis": opis.strip(),
                "zdjecia": sciezki_zdjec
            }
            
            entries.append(nowy_wpis)
            # sortujemy od najnowszych
            entries.sort(key=lambda x: x["data"], reverse=True)
            save_entries(entries)
            
            st.success("Wpis zapisany!")
            st.rerun()

# --- Wyświetlanie wpisów ---
st.header("Twoje wpisy")

entries = load_entries()

if not entries:
    st.info("Jeszcze nie ma żadnych wpisów. Dodaj pierwszy powyżej!")
else:
    for i, wpis in enumerate(entries):
        with st.container():
            st.subheader(f"📅 {wpis['data']}")
            
            if wpis["opis"]:
                st.write(wpis["opis"])
            
            # wyświetlanie zdjęć
            if wpis["zdjecia"]:
                cols = st.columns(min(3, len(wpis["zdjecia"])))
                for idx, sciezka in enumerate(wpis["zdjecia"]):
                    if os.path.exists(sciezka):
                        with cols[idx % 3]:
                            st.image(sciezka, use_container_width=True)
            
            st.divider()
