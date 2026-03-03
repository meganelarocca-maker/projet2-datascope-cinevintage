# CineVintage DataScope

Ce projet est une application Streamlit pour la recommandation de films et l'exploration de données. Suivez les étapes ci-dessous pour démarrer.

## Configuration

1. **Créer un environnement virtuel** (recommandé) :

   ```powershell
   cd "C:\Users\VIDA\Desktop\WCS\Projet 2\projet2-datascope-cinevintage"
   python -m venv .venv
   ```

2. **Activer l'environnement virtuel** :

   - Sous Windows (PowerShell) :
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Sous Windows (Invite de commandes) :
     ```cmd
     .\.venv\Scripts\activate.bat
     ```

3. **Installer les dépendances** :

   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Lancer l'application

Une fois les dépendances installées et l'environnement virtuel activé :

```powershell
streamlit run app.py
```

Cela démarrera le serveur Streamlit et ouvrira l'application dans votre navigateur (généralement à `http://localhost:8501`).

---

N'hésitez pas à explorer les répertoires `pages` et `utils` pour comprendre la structure du projet.

Bon développement ! 🚀