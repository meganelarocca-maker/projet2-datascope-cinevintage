import sqlite3
import streamlit as st
import hashlib

def show():
    st.title("Inscription")

    # Création table si besoin
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

    with st.form("register_form"):
        username = st.text_input("Nom d'utilisateur", key="reg_username")
        password = st.text_input("Mot de passe", type="password", key="reg_password")
        submit = st.form_submit_button("S'inscrire")

    if submit:
        if username.strip() and password.strip():
            password_hash = hashlib.sha256(password.strip().encode()).hexdigest()
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username.strip(), password_hash)
                )
                conn.commit()
                st.success("Inscription réussie ✅")
            except sqlite3.IntegrityError:
                st.error("Nom d'utilisateur déjà existant ❌")
            conn.close()
        else:
            st.error("Veuillez remplir tous les champs")