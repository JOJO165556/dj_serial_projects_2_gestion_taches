# TaskFlow — Gestion de projets Kanban

Application full-stack de gestion de projets avec tableau Kanban, invitations par lien, authentification JWT et connexion par magic link.

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Django 6 + Django REST Framework + SimpleJWT |
| Temps réel | Django Channels + WebSockets |
| Frontend | Vue 3 + Vite + TypeScript + Pinia |
| Base de données | PostgreSQL (Render) / SQLite (dev) |
| Email | Gmail SMTP (mot de passe d'application) |
| Déploiement | Render (backend) + Vercel (frontend) |

---

## Structure du projet

```
gestion_taches/
├── backend/
│   ├── apps/
│   │   ├── users/          # Modèle utilisateur personnalisé
│   │   ├── project/        # Projets et invitations
│   │   └── task/           # Tâches et colonnes Kanban
│   ├── api/
│   │   ├── views/          # Vues API REST
│   │   └── serializers/    # Sérialiseurs DRF
│   ├── services/           # Logique métier (auth, projets, emails)
│   ├── core/
│   │   └── settings/
│   │       ├── base.py     # Paramètres communs
│   │       ├── dev.py      # Développement local
│   │       └── prod.py     # Production
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/         # CSS global (transitions.css)
│   │   ├── components/     # NavBar, KanbanColumn, TaskCard, AppModal
│   │   ├── services/       # Appels API Axios
│   │   ├── store/          # Pinia (auth, kanban, theme)
│   │   ├── types/          # Types TypeScript
│   │   └── views/          # Dashboard, KanbanView, LoginView…
│   ├── vercel.json
│   └── vite.config.ts
├── render.yaml             # Blueprint Render (backend + base PostgreSQL)
└── README.md
```

---

## Fonctionnalités

- **Authentification** : login username/password + magic link par email
- **Projets** : création, édition, archivage, suppression (owner uniquement)
- **Invitations** : lien d'invitation par email Gmail avec acceptation/refus
- **Kanban** : colonnes *À faire* / *En cours* / *Terminé*, drag & drop, réordonnancement
- **Tâches** : priorités (haute/moyenne/basse), date limite, assignation, indicateur de retard
- **Filtres** : recherche, priorité, assigné, tâches en retard
- **Temps réel** : synchronisation WebSocket entre utilisateurs
- **Thème** : mode clair / sombre

---

## Lancement en développement

### Prérequis

- Python 3.12+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Remplir .env avec les valeurs locales
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est accessible sur `http://localhost:5173`.

---

## Variables d'environnement

### Backend (`.env`)

```env
SECRET_KEY=...
DATABASE_URL=sqlite:///db.sqlite3
DJANGO_ENV=dev
ALLOWED_HOSTS=127.0.0.1,localhost
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=votre@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx   # Mot de passe d'application Google
DEFAULT_FROM_EMAIL=votre@gmail.com
MAGIC_LINK_MAX_AGE_SECONDS=900
USE_REDIS=false
```

> Le mot de passe Gmail doit être un **mot de passe d'application** (pas le mot de passe du compte).
> Générer sur : [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### Frontend (`.env`)

```env
VITE_API_URL=http://localhost:8000   # En développement
# VITE_API_URL=https://votre-backend.onrender.com   # En production
```

---

## Déploiement

### Render (Backend + Base de données)

1. Aller sur [render.com](https://render.com) → **New → Blueprint**
2. Connecter le dépôt GitHub et sélectionner `render.yaml`
3. Render crée automatiquement :
   - La base **PostgreSQL** (`gestion-taches-db`)
   - Le service web **Django** (`gestion-taches-backend`)
   - La connexion `DATABASE_URL` est injectée automatiquement
4. Renseigner manuellement dans **Environment** :
   - `ALLOWED_HOSTS` → `gestion-taches-backend.onrender.com`
   - `FRONTEND_URL` → URL Vercel
   - `CORS_ALLOWED_ORIGINS` → URL Vercel
   - `CSRF_TRUSTED_ORIGINS` → URL Vercel + URL Render
   - `EMAIL_HOST_USER` → adresse Gmail
   - `EMAIL_HOST_PASSWORD` → mot de passe d'application Gmail
   - `DEFAULT_FROM_EMAIL` → adresse Gmail

### Vercel (Frontend)

1. Aller sur [vercel.com](https://vercel.com) → **Add New → Project**
2. Importer le dépôt GitHub
3. **Root Directory** : `frontend`
4. **Framework** : Vite (détecté automatiquement)
5. Ajouter la variable d'environnement :
   - `VITE_API_URL` → `https://gestion-taches-backend.onrender.com`
6. Déployer

Le fichier `vercel.json` gère le routing SPA (toutes les routes redirigent vers `index.html`).

---

## Permissions

| Action | Propriétaire | Membre |
|---|---|---|
| Créer un projet | ✅ | ✅ |
| Modifier / Archiver un projet | ✅ | ❌ |
| Inviter un membre | ✅ | ❌ |
| Supprimer un projet | ✅ | ❌ (toast d'erreur) |
| Créer / Modifier une tâche | ✅ | ✅ |
| Supprimer une tâche | ✅ | ❌ (toast d'erreur) |

---

## Auteur

Projet développé par **JoJo** — 2026
