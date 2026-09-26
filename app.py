import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client
from pathlib import Path
import uuid

# ============================================
# Klucze
# ============================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# Funkcje
# ============================================
def upload_image(uploaded_file):
    if uploaded_file is None:
        return None
    file_ext = Path(uploaded_file.name).suffix.lower()
    file_name = f"{uuid.uuid4()}{file_ext}"
    supabase.storage.from_("zdjecia").upload(
        file_name,
        uploaded_file.getvalue(),
        file_options={"content-type": uploaded_file.type}
    )
    return supabase.storage.from_("zdjecia").get_public_url(file_name)

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

def update_entry(entry_id, data_wpisu, opis):
    supabase.table("wpisy").update({
        "data": str(data_wpisu),
        "opis": opis
    }).eq("id", entry_id).execute()

def delete_entry(entry_id):
    supabase.table("wpisy").delete().eq("id", entry_id).execute()

def get_all_photos(entries):
    photos = []
    for e in entries:
        if e.get("zdjecia"):
            for url in e["zdjecia"]:
                photos.append({
                    "url": url,
                    "data": e["data"],
                    "opis": e.get("opis", "")[:80]
                })
    return photos

# ============================================
# Cukierkowy styl
# ============================================
st.set_page_config(
    page_title="Mój Słodki Dziennik",
    page_icon="🍬",
    layout="wide"
)

st.markdown("""
<style>
    /* Tło i ogólny klimat */
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #f0e6ff 50%, #e0f7fa 100%);
    }
    
    /* Nagłówki */
    h1, h2, h3 {
        color: #d46b9b !important;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Karty wpisów */
    .entry-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(212, 107, 155, 0.15);
        border: 2px solid #ffe4f0;
    }
    
    /* Przyciski */
    .stButton > button {
        border-radius: 12px !important;
        border: none !important;
        background: linear-gradient(90deg, #ff9ec4, #d4a5ff) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #ff7eb3, #c084fc) !important;
        transform: translateY(-1px);
    }
    
    /* Formularze */
    .stTextArea textarea, .stDateInput input {
        border-radius: 12px !important;
        border: 2px solid #ffd6e7 !important;
    }
    
    /* Tabulator */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0 !important;
        background: #ffe4f0 !important;
        color: #d46b9b !important;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        border-bottom: 3px solid #d46b9b !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍬 Mój Słodki Dziennik")

# ============================================
# Zakładki
# ============================================
tab1, tab2 = st.tabs(["📔 Wpisy", "🖼️ Galeria zdjęć"])

entries = load_entries()

# ----------------------------------------
# ZAKŁADKA 1: WPISY
# ----------------------------------------
with tab1:
    st.header("Dodaj nowy wpis")

    with st.form("nowy_wpis", clear_on_submit=True):
        data_wpisu = st.date_input("Data", value=date.today())
        opis = st.text_area("Co się wydarzyło?", height=140, placeholder="Napisz tutaj swoje myśli...")
        zdjecia = st.file_uploader(
            "Dodaj słodkie zdjęcia 📸",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True
        )
        
        if st.form_submit_button("Zapisz wpis ☁️"):
            if not opis.strip() and not zdjecia:
                st.warning("Dodaj chociaż opis albo zdjęcie 💕")
            else:
                with st.spinner("Zapisuję w chmurze..."):
                    lista_url = []
                    if zdjecia:
                        for zdj in zdjecia:
                            url = upload_image(zdj)
                            if url:
                                lista_url.append(url)
                    save_entry(data_wpisu, opis.strip(), lista_url)
                    st.success("Zapisano! ✨")
                    st.rerun()

    st.markdown("---")
    st.header("Twoje wpisy")

    if not entries:
        st.info("Jeszcze pusto... Dodaj pierwszy wpis powyżej! 🌸")
    else:
        for wpis in entries:
            with st.container():
                st.markdown(f"""
                <div class="entry-card">
                    <h3>📅 {wpis['data']}</h3>
                </div>
                """, unsafe_allow_html=True)

                # Tryb edycji
                edit_key = f"edit_{wpis['id']}"
                if st.session_state.get(edit_key, False):
                    with st.form(f"edit_form_{wpis['id']}"):
                        new_date = st.date_input(
                            "Data",
                            value=datetime.strptime(wpis["data"], "%Y-%m-%d").date(),
                            key=f"date_{wpis['id']}"
                        )
                        new_opis = st.text_area(
                            "Opis",
                            value=wpis.get("opis", ""),
                            height=140,
                            key=f"opis_{wpis['id']}"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Zapisz zmiany 💾"):
                                update_entry(wpis["id"], new_date, new_opis.strip())
                                st.session_state[edit_key] = False
                                st.success("Zaktualizowano!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Anuluj"):
                                st.session_state[edit_key] = False
                                st.rerun()
                else:
                    if wpis.get("opis"):
                        st.write(wpis["opis"])

                    if wpis.get("zdjecia"):
                        cols = st.columns(min(3, len(wpis["zdjecia"])))
                        for idx, url in enumerate(wpis["zdjecia"]):
                            with cols[idx % 3]:
                                st.image(url, use_container_width=True)

                    col_a, col_b, col_c = st.columns([1, 1, 4])
                    with col_a:
                        if st.button("✏️ Edytuj", key=f"btn_edit_{wpis['id']}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with col_b:
                        if st.button("🗑️ Usuń", key=f"btn_del_{wpis['id']}"):
                            delete_entry(wpis["id"])
                            st.success("Usunięto")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------
# ZAKŁADKA 2: GALERIA
# ----------------------------------------
with tab2:
    st.header("🖼️ Galeria wszystkich zdjęć")
    
    all_photos = get_all_photos(entries)
    
    if not all_photos:
        st.info("Brak zdjęć do wyświetlenia. Dodaj jakieś we wpisach! 🌈")
    else:
        st.caption(f"Znaleziono {len(all_photos)} zdjęć")
        
        # Siatka 4 kolumny
        cols = st.columns(4)
        for idx, photo in enumerate(all_photos):
            with cols[idx % 4]:
                st.image(photo["url"], use_container_width=True)
                st.caption(f"{photo['data']}")
                if photo["opis"]:
                    st.caption(photo["opis"] + "...")
