import os
import sqlite3
import hashlib
import streamlit as st
import numpy as np

st.set_page_config(page_title="Connexion - Ciné Vintage", page_icon="📽", layout="wide")

#on s'assure que la table existe et qu'elle est bien créée
DB_PATH = os.path.join("data_raw", "users.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
    conn.commit()
    conn.close()

# Si déjà connecté → go principale
if st.session_state.get("authenticated", True):
    st.switch_page("pages/page_principale.py")

#
#affichage des éléments de connexion
st.title("Connexion")

with st.form("login_form", clear_on_submit=False):
    login = st.text_input("Nom d'utilisateur ou email")
    password = st.text_input("Mot de passe", type="password")
    submitted = st.form_submit_button("Se connecter")

if submitted:
    #on tente la création de la base
    init_db()

    #login = (login or "").strip().lower()
    if login.strip() and password.strip():
        password_hash = hashlib.sha256(password.strip().encode()).hexdigest()
        #on appelle la base
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
                "SELECT * FROM users WHERE username=? AND password_hash=?",
                    (login.strip(), password_hash)
                )
        row = cursor.fetchone()
        conn.close()

        #if not row:
        if row is None:
            st.error("Identifiant ou mot de passe incorrects.")
            st.stop()
        else:

            st.session_state["authenticated"] = True
            st.session_state["username"] = login
            st.success(f"Heureux de vous revoir {login} ✅")
            st.switch_page("pages/page_principale.py")

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("Créer un compte"):
        st.switch_page("pages/inscription.py")
with col2:
    if st.button("Retour landing"):
        st.switch_page("app.py")