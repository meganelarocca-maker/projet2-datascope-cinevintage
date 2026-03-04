import base64
import re
import pandas as pd
import streamlit as st
from sklearn.neighbors import NearestNeighbors

# ==============================
# GUARD AUTH (à remettre quand inscription OK)
# ==============================
# if not st.session_state.get("authenticated", False):
#     st.switch_page("pages/connexion.py")

st.set_page_config(page_title="Ciné Vintage", layout="wide")

# =========================
# BACKGROUND
# =========================
def set_page_background(image_path: str):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        .block-container {{
            background: transparent !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 1200px !important;
        }}

        section[data-testid="stSidebar"],
        div[data-testid="stSidebarContent"] {{
            background: rgba(255, 140, 40, 0.08) !important;
            backdrop-filter: blur(14px) saturate(120%) !important;
            -webkit-backdrop-filter: blur(14px) saturate(120%) !important;
            border-right: 1px solid rgba(255, 190, 120, 0.25) !important;
            box-shadow: 4px 0px 18px rgba(0,0,0,0.25) !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: #FFE8C2 !important;
        }}

        .glass {{
            background: rgba(10, 8, 6, 0.55);
            border: 1px solid rgba(255, 210, 140, 0.20);
            border-radius: 14px;
            padding: 14px;
            box-shadow: 0 12px 28px rgba(0,0,0,0.35);
            backdrop-filter: blur(8px);
        }}

        .section-title {{
            color: #F8E7C2;
            font-weight: 800;
            text-shadow: 1px 1px 10px rgba(0,0,0,0.6);
            margin-top: 8px;
        }}

        .muted {{
            color: rgba(255,232,194,0.85);
        }}

        .poster-wrap {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 210, 140, 0.18);
            box-shadow: 0 10px 22px rgba(0,0,0,0.35);
        }}
        .poster-wrap img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .poster-caption {{
            margin-top: 6px;
            color: #F8E7C2;
            font-weight: 700;
            font-size: 0.95rem;
            line-height: 1.15rem;
        }}
        .poster-sub {{
            color: rgba(255,232,194,0.85);
            font-size: 0.85rem;
        }}

        .search-box {{
            background: rgba(10, 8, 6, 0.40);
            border: 1px solid rgba(255, 210, 140, 0.18);
            border-radius: 14px;
            padding: 12px 14px;
            box-shadow: 0 10px 22px rgba(0,0,0,0.25);
            backdrop-filter: blur(8px);
            margin: 10px 0 14px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_page_background("assets/main_background.png")

# =========================
# BANNIÈRE
# =========================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600&display=swap');

    .cinv-banner {
        width: 100%;
        border-radius: 14px;
        background-image: url("assets/banner.png");
        background-size: cover;
        background-position: center;
        height: 170px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: inset 0 0 0 1000px rgba(0,0,0,0.35);
        margin-bottom: 12px;
    }

    .cinv-banner h1 {
        font-family: 'Cinzel', serif;
        font-size: 50px;
        color: #F8E7C2;
        letter-spacing: 1px;
        text-shadow: 2px 2px 14px rgba(0,0,0,0.9);
        margin: 0 20px;
    }
    </style>

    <div class="cinv-banner">
        <h1>LAISSEZ-VOUS GUIDER<br/>VERS VOTRE PROCHAIN CHEF-D’ŒUVRE</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
def pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def split_list_cell(x):
    if not isinstance(x, str):
        return []
    return [t.strip().lower() for t in x.split(",") if t.strip()]

def poster_to_url(*candidates, size: str = "w342") -> str | None:
    """
    Priorité:
    - OMDb URL (http...)
    - TMDb path '/xxx.jpg'
    On ignore les cellules "dump pandas" multi-lignes (sinon même poster partout).
    """
    base = f"https://image.tmdb.org/t/p/{size}"

    for p in candidates:
        if not isinstance(p, str):
            continue
        p = p.strip()
        if not p:
            continue

        # ignore dump multi-lignes
        if "\n" in p and ("dtype" in p or "Name:" in p):
            continue

        if p.startswith("http"):
            return p

        if p.startswith("/"):
            return base + p

        # cas "cassé" contenant un path
        m = re.search(r"(/[^ \t\r\n]+?\.(?:jpg|jpeg|png|webp))", p, flags=re.IGNORECASE)
        if m:
            return base + m.group(1)

    return None

def build_label(row: pd.Series) -> str:
    t = (row.get("title") or "").strip()
    o = (row.get("originalTitle") or "").strip()
    if t and o and t.lower() != o.lower():
        return f"{t} ({o})"
    return t or o or "Sans titre"

def get_query_movie() -> str | None:
    qp = st.query_params
    movie = qp.get("movie")
    if isinstance(movie, list):
        return movie[0] if movie else None
    return movie

def set_query_movie(tconst: str | None):
    if tconst:
        st.query_params["movie"] = tconst
    else:
        st.query_params.clear()

def poster_tile(row: pd.Series):
    tconst = str(row.get("tconst"))
    title = row.get("title", "")
    year = row.get("startYear", "")
    genres = row.get("genres", "")

    poster_url = poster_to_url(
        row.get("omdb_poster"),
        row.get("poster_final"),
        row.get("poster_path"),
        size="w342",
    )

    if poster_url:
        st.markdown(
            f"""
            <a href="?movie={tconst}" style="text-decoration:none;">
              <div class="poster-wrap">
                <img src="{poster_url}" />
              </div>
            </a>
            <div class="poster-caption">{title} ({year})</div>
            <div class="poster-sub">{genres}</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <a href="?movie={tconst}" style="text-decoration:none;">
              <div class="glass" style="padding:12px;">
                <div class="poster-caption">{title} ({year})</div>
                <div class="poster-sub">{genres}</div>
                <div class="muted" style="margin-top:8px;">Poster indisponible</div>
              </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

def detail_panel(df: pd.DataFrame, tconst: str):
    row = df[df["tconst"].astype(str) == str(tconst)]
    if row.empty:
        st.warning("Film introuvable.")
        return
    r = row.iloc[0]

    title = build_label(r)
    year = r.get("startYear", "")
    genres = r.get("genres", "")
    directors = r.get("directors", "")
    actors = r.get("actors", "")
    lang = r.get("original_language", r.get("origine", ""))
    runtime = r.get("runtimeMinutes", r.get("runtime", r.get("duration", "")))
    overview = r.get("overview_final") or r.get("overview") or ""

    poster_url = poster_to_url(
        r.get("omdb_poster"),
        r.get("poster_final"),
        r.get("poster_path"),
        size="w500",
    )

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    top = st.columns([1, 2])
    with top[0]:
        if poster_url:
            #st.image(poster_url, use_container_width=True)
            st.image(poster_url, width=True)
    with top[1]:
        st.markdown(f"## {title}")
        st.caption(f"{year} • {genres}")
        if directors:
            st.markdown(f"**Réalisateur(s)** : {directors}")
        if actors:
            st.markdown(f"**Acteurs** : {actors}")
        if runtime:
            st.markdown(f"**Durée** : {runtime} min")
        if lang:
            st.markdown(f"**Langue / Origine** : {lang}")

    if isinstance(overview, str) and overview.strip():
        st.markdown("---")
        st.markdown("### Synopsis")
        st.write(overview)

    st.markdown('</div>', unsafe_allow_html=True)

    #if st.button("Fermer", use_container_width=True):
    if st.button("Fermer", width=True):
        set_query_movie(None)
        st.rerun()

# =========================
# LOAD DATAS
# =========================
@st.cache_data
def load_csvs():
    df_display = pd.read_csv("data_raw/df_display_enriched.csv")
    df_features = pd.read_csv("data_raw/df_features_encoded.csv")
    df_display["tconst"] = df_display["tconst"].astype(str)
    df_features["tconst"] = df_features["tconst"].astype(str)
    return df_display, df_features

df_display, df_ml = load_csvs()  # df_ml = ton DF ML (avec tconst + features)

# colonnes variables
year_col = pick_col(df_display, ["startYear", "year"])
dur_col = pick_col(df_display, ["runtimeMinutes", "runtime", "duration"])
lang_col = pick_col(df_display, ["original_language", "origine", "language", "lang"])

if year_col:
    df_display[year_col] = pd.to_numeric(df_display[year_col], errors="coerce")
if dur_col:
    df_display[dur_col] = pd.to_numeric(df_display[dur_col], errors="coerce")

# =========================
# KNN (COSINE) + X_df
# =========================
@st.cache_resource
def build_knn_model(df_ml: pd.DataFrame):
    # IMPORTANT : X_df = toutes les colonnes features (donc tout sauf tconst)
    X_df = df_ml.drop(columns=["tconst"])
    knn = NearestNeighbors(metric="cosine")
    knn.fit(X_df.values)
    # mapping tconst -> idx
    id_to_idx = pd.Series(df_ml.index, index=df_ml["tconst"]).to_dict()
    return knn, X_df, id_to_idx

knn, X_df, id_to_idx = build_knn_model(df_ml)

# =========================
# TA FONCTION RECO (ADAPTÉE)
# =========================
def recommend_by_tconst(tconst: str, n_reco: int = 5):
    if tconst not in id_to_idx:
        raise ValueError(f"tconst introuvable: {tconst}")

    idx = id_to_idx[tconst]

    distances, indices = knn.kneighbors([X_df.iloc[idx].values], n_neighbors=n_reco + 1)

    reco_idx = [i for i in indices[0] if i != idx][:n_reco]
    reco_dist = [d for i, d in zip(indices[0], distances[0]) if i != idx][:n_reco]

    result = df_ml.iloc[reco_idx][["tconst"]].copy()
    result["distance_cosine"] = reco_dist
    return result

# =========================
# SIDEBAR FILTERS
# =========================
with st.sidebar:
    deconnexion = st.button("Déconnexion")
    if deconnexion:
        st.write("A bientôt sur notre site")
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.success("A bientôt sur notre site 🙏")
        st.switch_page("pages/connexion.py")
    
    st.markdown("## Filtres")

    genre_selected = None
    if "genres" in df_display.columns:
        all_genres = sorted({g for cell in df_display["genres"].dropna().tolist() for g in split_list_cell(cell)})
        genre_selected = st.selectbox("Genre", ["—"] + all_genres)
        if genre_selected == "—":
            genre_selected = None

    director_selected = None
    if "directors" in df_display.columns:
        all_directors = sorted({d for cell in df_display["directors"].dropna().tolist() for d in split_list_cell(cell)})
        director_selected = st.selectbox("Réalisateur", ["—"] + all_directors)
        if director_selected == "—":
            director_selected = None

    origin_selected = None
    if lang_col:
        vals = sorted(df_display[lang_col].dropna().unique())
        origin_selected = st.selectbox("Origine / Langue", ["—"] + vals)
        if origin_selected == "—":
            origin_selected = None

    actor_selected = None
    if "actors" in df_display.columns:
        all_actors = sorted({a for cell in df_display["actors"].dropna().tolist() for a in split_list_cell(cell)})
        actor_selected = st.selectbox("Acteur", ["—"] + all_actors)
        if actor_selected == "—":
            actor_selected = None

    year_range = None
    if year_col and df_display[year_col].notna().any():
        y_min = int(df_display[year_col].min())
        y_max = int(df_display[year_col].max())
        year_range = st.slider("Année", min_value=y_min, max_value=y_max, value=(y_min, y_max))

    dur_range = None
    if dur_col and df_display[dur_col].notna().any():
        d_min = int(df_display[dur_col].min())
        d_max = int(df_display[dur_col].max())
        dur_range = st.slider("Durée (minutes)", min_value=d_min, max_value=d_max, value=(d_min, d_max))

# =========================
# APPLY FILTERS
# =========================
filtered_df = df_display.copy()

if genre_selected:
    filtered_df = filtered_df[filtered_df["genres"].fillna("").apply(lambda x: genre_selected.lower() in split_list_cell(x))]

if director_selected and "directors" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["directors"].fillna("").apply(lambda x: director_selected.lower() in split_list_cell(x))]

if actor_selected and "actors" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["actors"].fillna("").apply(lambda x: actor_selected.lower() in split_list_cell(x))]

if origin_selected and lang_col:
    filtered_df = filtered_df[filtered_df[lang_col] == origin_selected]

if year_col and year_range:
    filtered_df = filtered_df[(filtered_df[year_col] >= year_range[0]) & (filtered_df[year_col] <= year_range[1])]

if dur_col and dur_range:
    filtered_df = filtered_df[(filtered_df[dur_col] >= dur_range[0]) & (filtered_df[dur_col] <= dur_range[1])]

# =========================
# SEARCH / SELECT FILM (hors sidebar)
# =========================
st.markdown('<div class="search-box">', unsafe_allow_html=True)

df_display["label"] = df_display.apply(build_label, axis=1)
selected_label = st.selectbox(
    "Rechercher un film…",
    df_display["label"].sort_values().unique(),
    label_visibility="collapsed"
)

st.markdown("</div>", unsafe_allow_html=True)

tconst_selected = df_display.loc[df_display["label"] == selected_label, "tconst"].iloc[0]

# =========================
# DETAIL ON CLICK
# =========================
movie_clicked = get_query_movie()
if movie_clicked:
    detail_panel(df_display, movie_clicked)
    st.markdown("<br/>", unsafe_allow_html=True)

# =========================
# RECO (5 films)
# =========================
reco_df = recommend_by_tconst(str(tconst_selected), n_reco=5)
reco_tconst = reco_df["tconst"].astype(str).tolist()

df_reco = df_display[df_display["tconst"].astype(str).isin(reco_tconst)].copy()
df_reco["order"] = df_reco["tconst"].astype(str).apply(lambda x: reco_tconst.index(x))
df_reco = df_reco.sort_values("order")

# =========================
# DISPLAY GRID
# =========================
st.markdown('<h2 class="section-title">Films correspondants :</h2>', unsafe_allow_html=True)
st.markdown(f'<div class="muted">{len(filtered_df)} films trouvés</div>', unsafe_allow_html=True)

to_show = filtered_df.head(10)
cols = st.columns(5)
for i, (_, r) in enumerate(to_show.iterrows()):
    with cols[i % 5]:
        poster_tile(r)

st.markdown('<h2 class="section-title" style="margin-top:18px;">Vous pourriez aussi aimer :</h2>', unsafe_allow_html=True)

cols2 = st.columns(5)
for i, (_, r) in enumerate(df_reco.iterrows()):
    with cols2[i % 5]:
        poster_tile(r)