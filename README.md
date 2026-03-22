# Gestion des Taches

Application de gestion de projets et de taches developpee avec Django.

## Fonctionnalites principales

- Authentification des utilisateurs
- Gestion des utilisateurs par roles (Administrateur, Membre, Lecteur)
- Creation et gestion de projets
- Creation et assignation de taches
- Affichage des taches sous forme de tableau Kanban

## Installation

1. Creer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate
```

2. Installer les dependances :
```bash
pip install -r requirements.txt
```

3. Appliquer les migrations de la base de donnees :
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Lancer le serveur de developpement :
```bash
python manage.py runserver
```

## Structure du projet

- apps/project/ : Gestion des projets
- apps/task/ : Gestion des taches
- apps/users/ : Authentification et profils
- templates/ : Fichiers HTML globaux
- static/ : Fichiers CSS et medias
