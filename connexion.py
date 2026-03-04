import sqlite3
import hashlib
import streamlit as st

st.set_page_config(page_title="Connexion - Ciné Vintage", layout="wide")

DB_PATH = "users.db"  # même chemin que ton inscription

st.title("Connexion")

with st.form("login_form", clear_on_submit=False):
    login = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    submitted = st.form_submit_button("Se connecter")

if submitted:
    login = (login or "").strip()
    password = (password or "").strip()

    # Connexion à la base
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password FROM users WHERE username=?",
        (login,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        st.error("Identifiants incorrects ❌")
        st.stop()

    username_db, password_hash_db = row

    # Hash du mot de passe saisi avec SHA256
    computed_hash = hashlib.sha256(password.encode()).hexdigest()

    if computed_hash != password_hash_db:
        st.error("Identifiants incorrects ❌")
        st.stop()

    # ✅ Connexion réussie
    st.session_state["authenticated"] = True
    st.session_state["username"] = username_db
    st.success(f"Bienvenue {username_db} ✅")
    st.switch_page("pages/page_principale.py")  # ou redirige vers ta page principale