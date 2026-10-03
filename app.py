import streamlit as st
from datetime import date, datetime
from supabase import create_client, Client
from pathlib import Path
import uuid
import html as html_lib

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
        .order("data", desc=False)  # od najstarszego
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

def format_date_pl(data_str):
    try:
        d = datetime.strptime(data_str, "%Y-%m-%d")
        date_display = d.strftime("%d.%m.%Y")
        weekday = ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"][d.weekday()]
        return f"{date_display} · {weekday}"
    except Exception:
        return data_str

# ============================================
# Przełącznik motywu
# ============================================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ============================================
# Style + animacja przekładania kartki
# ============================================
def get_css(theme):
    flip_anim = """
    @keyframes pageFlipIn {
        0% {
            opacity: 0;
            transform: perspective(900px) rotateY(-18deg) scale(0.97);
        }
        60% {
            opacity: 1;
            transform: perspective(900px) rotateY(4deg) scale(1.01);
        }
        100% {
            opacity: 1;
            transform: perspective(900px) rotateY(0deg) scale(1);
        }
    }
    .diary-page {
        animation: pageFlipIn 0.55s ease-out;
        transform-origin: left center;
        transform-style: preserve-3d;
    }
    """
    if theme == "dark":
        return f"""
        <style>
            .stApp {{ background-color: #0f0f0f; color: #e0e0e0; }}
            h1, h2, h3 {{ color: #f5f5f5 !important; font-family: 'Segoe UI', system-ui, sans-serif; font-weight: 600; }}
            .diary-page {{
                background: linear-gradient(145deg, #1c1c1c 0%, #161616 100%);
                border-radius: 14px;
                padding: 1.8rem 2rem;
                margin: 0.8rem 0 1.2rem 0;
                border: 1px solid #2e2e2e;
                box-shadow: 0 6px 18px rgba(0,0,0,0.35);
                position: relative;
            }}
            .diary-page::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 12px;
                bottom: 12px;
                width: 4px;
                background: #5a5a5a;
                border-radius: 0 3px 3px 0;
            }}
            .diary-date {{
                font-size: 1.3rem;
                font-weight: 600;
                color: #f0f0f0;
                margin-bottom: 0.9rem;
                letter-spacing: 0.02em;
            }}
            .diary-content {{
                color: #c8c8c8;
                line-height: 1.7;
                font-size: 1.05rem;
                white-space: pre-wrap;
            }}
            .page-nav {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin: 0.5rem 0 0.2rem 0;
            }}
            .page-counter {{
                color: #888;
                font-size: 0.95rem;
                min-width: 140px;
                text-align: center;
            }}
            p, .stMarkdown, .stCaption {{ color: #d0d0d0 !important; }}
            .stButton > button {{
                border-radius: 8px !important;
                border: 1px solid #333 !important;
                background: #1f1f1f !important;
                color: #e0e0e0 !important;
                font-weight: 500 !important;
            }}
            .stButton > button:hover {{
                background: #2a2a2a !important;
                border-color: #444 !important;
                color: #fff !important;
            }}
            .stTextArea textarea, .stDateInput input, .stTextInput input {{
                background-color: #1a1a1a !important;
                color: #e0e0e0 !important;
                border: 1px solid #333 !important;
                border-radius: 6px !important;
            }}
            .stTabs [data-baseweb="tab"] {{
                background: #1a1a1a !important;
                color: #aaa !important;
                border-radius: 6px 6px 0 0 !important;
                border: 1px solid #2a2a2a !important;
            }}
            .stTabs [aria-selected="true"] {{
                background: #252525 !important;
                color: #fff !important;
                border-bottom: 2px solid #666 !important;
            }}
            hr {{ border-color: #2a2a2a !important; }}
            .stAlert {{
                background: #1a1a1a !important;
                color: #ccc !important;
                border: 1px solid #333 !important;
            }}
            {flip_anim}
        </style>
        """
    else:
        return f"""
        <style>
            .stApp {{ background-color: #f7f7f7; color: #1a1a1a; }}
            h1, h2, h3 {{ color: #111 !important; font-family: 'Segoe UI', system-ui, sans-serif; font-weight: 600; }}
            .diary-page {{
                background: linear-gradient(145deg, #ffffff 0%, #fafafa 100%);
                border-radius: 14px;
                padding: 1.8rem 2rem;
                margin: 0.8rem 0 1.2rem 0;
                border: 1px solid #e5e5e5;
                box-shadow: 0 4px 14px rgba(0,0,0,0.06);
                position: relative;
            }}
            .diary-page::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 12px;
                bottom: 12px;
                width: 4px;
                background: #c0c0c0;
                border-radius: 0 3px 3px 0;
            }}
            .diary-date {{
                font-size: 1.3rem;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 0.9rem;
                letter-spacing: 0.02em;
            }}
            .diary-content {{
                color: #333;
                line-height: 1.7;
                font-size: 1.05rem;
                white-space: pre-wrap;
            }}
            .page-nav {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin: 0.5rem 0 0.2rem 0;
            }}
            .page-counter {{
                color: #666;
                font-size: 0.95rem;
                min-width: 140px;
                text-align: center;
            }}
            p, .stMarkdown, .stCaption {{ color: #333 !important; }}
            .stButton > button {{
                border-radius: 8px !important;
                border: 1px solid #ccc !important;
                background: #ffffff !important;
                color: #222 !important;
                font-weight: 500 !important;
            }}
            .stButton > button:hover {{
                background: #f0f0f0 !important;
                border-color: #999 !important;
            }}
            .stTextArea textarea, .stDateInput input, .stTextInput input {{
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                border: 1px solid #ccc !important;
                border-radius: 6px !important;
            }}
            .stTabs [data-baseweb="tab"] {{
                background: #eee !important;
                color: #555 !important;
                border-radius: 6px 6px 0 0 !important;
                border: 1px solid #ddd !important;
            }}
            .stTabs [aria-selected="true"] {{
                background: #fff !important;
                color: #111 !important;
                border-bottom: 2px solid #666 !important;
            }}
            hr {{ border-color: #ddd !important; }}
            .stAlert {{
                background: #fff !important;
                color: #333 !important;
                border: 1px solid #ddd !important;
            }}
            {flip_anim}
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
    st.write("")
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
    st.subheader("Kartki z pamiętnika")

    if not entries:
        st.info("Brak wpisów. Dodaj pierwszy wpis powyżej.")
    else:
        # --- Wyszukiwarka dni ---
        search_col, clear_col = st.columns([5, 1])
        with search_col:
            search_query = st.text_input(
                "🔍 Szukaj dnia (np. 2025, 2025-03, 2025-03-15)",
                placeholder="Wpisz rok, miesiąc lub pełną datę...",
                key="search_days"
            )
        with clear_col:
            st.write("")
            if st.button("Wyczyść", key="clear_search"):
                st.session_state.search_days = ""
                st.session_state.page_idx = 0
                st.rerun()

        # Filtrowanie
        filtered = entries
        if search_query and search_query.strip():
            q = search_query.strip()
            filtered = [e for e in entries if q in e.get("data", "")]

        # Reset indeksu gdy zmienia się filtr
        filter_key = search_query.strip() if search_query else ""
        if "last_filter" not in st.session_state or st.session_state.last_filter != filter_key:
            st.session_state.last_filter = filter_key
            st.session_state.page_idx = 0

        if "page_idx" not in st.session_state:
            st.session_state.page_idx = 0

        if not filtered:
            st.warning(f"Brak wpisów pasujących do „{search_query}”.")
        else:
            total = len(filtered)
            # zabezpieczenie zakresu
            if st.session_state.page_idx >= total:
                st.session_state.page_idx = total - 1
            if st.session_state.page_idx < 0:
                st.session_state.page_idx = 0

            idx = st.session_state.page_idx
            wpis = filtered[idx]

            # --- Nawigacja strzałkami ---
            nav_left, nav_center, nav_right = st.columns([1, 3, 1])

            with nav_left:
                disabled_prev = idx <= 0
                if st.button("◀  Poprzedni", key="btn_prev", disabled=disabled_prev, use_container_width=True):
                    st.session_state.page_idx = max(0, idx - 1)
                    st.rerun()

            with nav_center:
                date_full = format_date_pl(wpis["data"])
                st.markdown(
                    f"<div style='text-align:center; padding-top:0.35rem;'>"
                    f"<strong style='font-size:1.05rem;'>{date_full}</strong><br>"
                    f"<span class='page-counter'>kartka {idx + 1} z {total}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with nav_right:
                disabled_next = idx >= total - 1
                if st.button("Następny  ▶", key="btn_next", disabled=disabled_next, use_container_width=True):
                    st.session_state.page_idx = min(total - 1, idx + 1)
                    st.rerun()

            # --- Edycja ---
            edit_key = f"edit_{wpis['id']}"

            if st.session_state.get(edit_key, False):
                with st.form(f"edit_form_{wpis['id']}"):
                    st.markdown(f"**Edycja wpisu z {date_full}**")
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
                # --- Kartka z animacją ---
                # escapujemy treść, żeby HTML nie psuł layoutu
                content_raw = wpis.get("opis") or ""
                if content_raw.strip():
                    content_html = html_lib.escape(content_raw).replace("\n", "<br>")
                else:
                    content_html = "<i style='opacity:0.5'>Brak treści</i>"

                st.markdown(f"""
                <div class="diary-page">
                    <div class="diary-date">{date_full}</div>
                    <div class="diary-content">{content_html}</div>
                </div>
                """, unsafe_allow_html=True)

                if wpis.get("zdjecia"):
                    n = len(wpis["zdjecia"])
                    cols = st.columns(min(3, n))
                    for i, url in enumerate(wpis["zdjecia"]):
                        with cols[i % 3]:
                            st.image(url, use_container_width=True)

                col_a, col_b, _ = st.columns([1, 1, 6])
                with col_a:
                    if st.button("Edytuj", key=f"btn_edit_{wpis['id']}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                with col_b:
                    if st.button("Usuń", key=f"btn_del_{wpis['id']}"):
                        delete_entry(wpis["id"])
                        # po usunięciu cofnij indeks jeśli trzeba
                        if st.session_state.page_idx >= total - 1 and st.session_state.page_idx > 0:
                            st.session_state.page_idx -= 1
                        st.success("Usunięto.")
                        st.rerun()

            # mała podpowiedź na dole
            st.caption("Użyj strzałek lub klawiszy, żeby przekładać kartki · od najstarszego do najnowszego")

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
