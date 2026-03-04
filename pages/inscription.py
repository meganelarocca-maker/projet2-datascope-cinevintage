import os
import sqlite3
import streamlit as st
import hashlib

#def show():
st.set_page_config(page_title="Connexion - Ciné Vintage", page_icon="📽", layout="wide")


#accès à la base
DB_PATH = os.path.join("data_raw", "users.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn =  sqlite3.connect(DB_PATH, check_same_thread=False)
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


st.title("Inscription")


#saisie des informations d'inscription
with st.form("register_form"):
    username = st.text_input("Nom d'utilisateur ou email", key="reg_username")
    password = st.text_input("Mot de passe", type="password", key="reg_password")
    submit = st.form_submit_button("S'inscrire")

if submit:
    #on tente la création de la base
    init_db()
    if username.strip() and password.strip():
        password_hash = hashlib.sha256(password.strip().encode()).hexdigest()
        #accès base
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username.strip(), password_hash)
                        )       
            conn.commit()
            st.success("Inscription réussie ✅.")
            st.success(f"Compte créé pour {username}! Veuillez vous connecter.")  
        except sqlite3.IntegrityError:
        #except sqlite3.Error as e:
        #    st.error(e.sqlite_errorname)   
            st.error("Nom d'utilisateur déjà existant ❌.")
        conn.close()
    else:
            st.error("Veuillez saisir tous les champs.")