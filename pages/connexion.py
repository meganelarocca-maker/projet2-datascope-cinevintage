import os
import sqlite3
import hashlib
import streamlit as st

st.set_page_config(page_title="Connexion - Ciné Vintage", layout="wide")

DB_PATH = os.path.join("data_raw", "users.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def hash_password(password: str, salt_hex: str) -> str:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        200_000
    )
    return dk.hex()

init_db()

# Si déjà connecté → go principale
if st.session_state.get("authenticated", False):
    st.switch_page("pages/page_principale.py")

st.title("Connexion")

with st.form("login_form", clear_on_submit=False):
    login = st.text_input("Nom d'utilisateur ou email")
    password = st.text_input("Mot de passe", type="password")
    submitted = st.form_submit_button("Se connecter")

if submitted:
    login = (login or "").strip().lower()

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT username, email, password_hash, salt FROM users WHERE lower(username)=? OR lower(email)=?",
            (login, login)
        )
        row = cur.fetchone()

    if not row:
        st.error("Identifiants incorrects.")
        st.stop()

    username, email, password_hash, salt = row
    computed = hash_password(password, salt)

    if computed != password_hash:
        st.error("Identifiants incorrects.")
        st.stop()

    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.success(f"Bienvenue {username} ✅")
    st.switch_page("pages/page_principale.py")

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Créer un compte"):
        st.switch_page("pages/inscription.py")
with col2:
    if st.button("Retour landing"):
        st.switch_page("app.py")