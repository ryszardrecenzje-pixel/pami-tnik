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
# Przełącznik motywu
# ============================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ============================================
# Style
# ============================================
def get_css(theme):
    if theme == "dark":
        return """
        <style>
            .stApp { background-color: #0f0f0f; color: #e0e0e0; }
            h1, h2, h3 { color: #f5f5f5 !important; font-family: 'Segoe UI', system-ui, sans-serif; font-weight: 600; }
            .entry-card {
                background: #1a1a1a;
                border-radius: 8px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1.2rem;
                border: 1px solid #2a2a2a;
            }
            p, .stMarkdown, .stCaption { color: #d0d0d0 !important; }
            .stButton > button {
                border-radius: 6px !important;
                border: 1px solid #333 !important;
                background: #1f1f1f !important;
                color: #e0e0e0 !important;
                font-weight: 500 !important;
            }
            .stButton > button:hover {
                background: #2a2a2a !important;
                border-color: #444 !important;
                color: #fff !important;
            }
            .stTextArea textarea, .stDateInput input, .stTextInput input {
                background-color: #1a1a1a !important;
                color: #e0e0e0 !important;
                border: 1px solid #333 !important;
                border-radius: 6px !important;
            }
            .stTabs [data-baseweb="tab"] {
                background: #1a1a1a !important;
                color: #aaa !important;
                border-radius: 6px 6px 0 0 !important;
                border: 1px solid #2a2a2a !important;
            }
            .stTabs [aria-selected="true"] {
                background: #252525 !important;
                color: #fff !important;
                border-bottom: 2px solid #666 !important;
            }
            hr { border-color: #2a2a2a !important; }
            .stAlert {
                background: #1a1a1a !important;
                color: #ccc !important;
                border: 1px solid #333 !important;
            }
        </style>
        """
    else:
        return """
        <style>
            .stApp { background-color: #f7f7f7; color: #1a1a1a; }
            h1, h2, h3 { color: #111 !important; font-family: 'Segoe UI', system-ui, sans-serif; font-weight: 600; }
            .entry-card {
                background: #ffffff;
                border-radius: 8px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1.2rem;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            }
            p, .stMarkdown, .stCaption { color: #333 !important; }
            .stButton > button {
                border-radius: 6px !important;
                border: 1px solid #ccc !important;
                background: #ffffff !important;
                color: #222 !important;
                font-weight: 500 !important;
            }
            .stButton > button:hover {
                background: #f0f0f0 !important;
                border-color: #999 !important;
            }
            .stTextArea textarea, .stDateInput input, .stTextInput input {
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                border: 1px solid #ccc !important;
                border-radius: 6px !important;
            }
            .stTabs [data-baseweb="tab"] {
                background: #eee !important;
                color: #555 !important;
                border-radius: 6px 6px 0 0 !important;
                border: 1px solid #ddd !important;
            }
            .stTabs [aria-selected="true"] {
                background: #fff !important;
                color: #111 !important;
                border-bottom: 2px solid #666 !important;
            }
            hr { border-color: #ddd !important; }
            .stAlert {
                background: #fff !important;
                color: #333 !important;
                border: 1px solid #ddd !important;
            }
        </style>
        """

st.set_page_config(page_title="Dziennik", page_icon="📓", layout="wide")
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ============================================
# Nagłówek + przełącznik
# ============================================
col_title, col_theme = st.columns([6, 1])
with col_title:
    st.title("📓 Dziennik")
with col_theme:
    st.write("")  # odstęp
    if st.button("🌙" if st.session_state.theme == "light" else "☀️", help="Przełącz motyw"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# ============================================
# Zakładki
# ============================================
tab1, tab2 = st.tabs(["Wpisy", "Galeria"])

entries = load_entries()

# ----------------------------------------
# ZAKŁADKA 1: WPISY
# ----------------------------------------
with tab1:
    st.subheader("Nowy wpis")

    with st.form("nowy_wpis", clear_on_submit=True):
        data_wpisu = st.date_input("Data", value=date.today())
        opis = st.text_area("Treść", height=150, placeholder="Co się wydarzyło...")
        zdjecia = st.file_uploader(
            "Zdjęcia",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True
        )
        
        if st.form_submit_button("Zapisz"):
            if not opis.strip() and not zdjecia:
                st.warning("Dodaj treść albo zdjęcie.")
            else:
                with st.spinner("Zapisuję..."):
                    lista_url = []
                    if zdjecia:
                        for zdj in zdjecia:
                            url = upload_image(zdj)
                            if url:
                                lista_url.append(url)
                    save_entry(data_wpisu, opis.strip(), lista_url)
                    st.success("Zapisano.")
                    st.rerun()

    st.markdown("---")
    st.subheader("Wpisy")

    if not entries:
        st.info("Brak wpisów.")
    else:
        for wpis in entries:
            with st.container():
                st.markdown(f"""
                <div class="entry-card">
                    <h3 style="margin:0 0 0.6rem 0; font-size:1.15rem;">{wpis['data']}</h3>
                </div>
                """, unsafe_allow_html=True)

                edit_key = f"edit_{wpis['id']}"
                
                if st.session_state.get(edit_key, False):
                    with st.form(f"edit_form_{wpis['id']}"):
                        new_date = st.date_input(
                            "Data",
                            value=datetime.strptime(wpis["data"], "%Y-%m-%d").date(),
                            key=f"date_{wpis['id']}"
                        )
                        new_opis = st.text_area(
                            "Treść",
                            value=wpis.get("opis", ""),
                            height=150,
                            key=f"opis_{wpis['id']}"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Zapisz zmiany"):
                                update_entry(wpis["id"], new_date, new_opis.strip())
                                st.session_state[edit_key] = False
                                st.success("Zaktualizowano.")
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

                    col_a, col_b, _ = st.columns([1, 1, 6])
                    with col_a:
                        if st.button("Edytuj", key=f"btn_edit_{wpis['id']}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with col_b:
                        if st.button("Usuń", key=f"btn_del_{wpis['id']}"):
                            delete_entry(wpis["id"])
                            st.success("Usunięto.")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------
# ZAKŁADKA 2: GALERIA
# ----------------------------------------
with tab2:
    st.subheader("Galeria")
    
    all_photos = get_all_photos(entries)
    
    if not all_photos:
        st.info("Brak zdjęć.")
    else:
        st.caption(f"{len(all_photos)} zdjęć")
        
        cols = st.columns(4)
        for idx, photo in enumerate(all_photos):
            with cols[idx % 4]:
                st.image(photo["url"], use_container_width=True)
                st.caption(photo["data"])
