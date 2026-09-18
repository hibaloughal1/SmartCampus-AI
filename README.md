# SmartCampus AI

Assistant universitaire intelligent basé sur le **Retrieval-Augmented Generation (RAG)**,
conforme au cahier des charges du projet. Cette implémentation utilise **MySQL** comme
base de données relationnelle.

## Architecture

```
Documents PDF / DOCX / PPTX / TXT
        ↓
Extraction du texte → Nettoyage → Chunking
        ↓
Embeddings (SentenceTransformers all-MiniLM-L6-v2)
        ↓
Base vectorielle FAISS  +  Index lexical BM25
        ↓
Recherche hybride (60% FAISS / 40% BM25, fusion pondérée)
        ↓
Construction du prompt (historique + documents + question)
        ↓
LLM Llama 3 (Ollama, exécution locale)
        ↓
Réponse + sources citées
```

## Stack technique

| Composant        | Technologie                          |
|------------------|---------------------------------------|
| Backend          | FastAPI (Python 3.12)                |
| Frontend         | ReactJS + Vite + Tailwind CSS        |
| Base de données  | **MySQL 8** (SQLAlchemy 2.0 + PyMySQL) |
| LLM              | Llama 3 via Ollama (local, hors ligne)|
| Embeddings       | SentenceTransformers (all-MiniLM-L6-v2)|
| Base vectorielle | FAISS (IndexFlatIP, cosine)          |
| Recherche lexicale| BM25 (rank_bm25)                    |
| Authentification | JWT + bcrypt                         |
| Conteneurisation | Docker / Docker Compose              |

## Démarrage rapide (Docker)

```bash
# 1. Cloner / copier le projet, puis à la racine :
docker compose up --build

# 2. Récupérer le modèle Llama 3 dans le conteneur Ollama (première fois seulement)
docker exec -it smartcampus-ollama ollama pull llama3

# 3. Accéder à l'application
#    Frontend : http://localhost:3000
#    Backend  : http://localhost:8000/docs (Swagger)
```

Au premier démarrage, le backend crée automatiquement les tables MySQL
(`init_db()`), il n'y a rien à faire côté migration pour du développement.
Pour la production, utilisez Alembic (déjà inclus dans `requirements.txt`).

## Démarrage manuel (sans Docker)

### Prérequis
- Python 3.12, Node.js 20, MySQL 8 installés localement
- [Ollama](https://ollama.ai) installé avec `ollama pull llama3`

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # adapter DATABASE_URL à votre instance MySQL locale
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173, proxy /api vers localhost:8000
```

### Créer un compte administrateur
Le premier compte créé via `/api/auth/register` a le rôle `student` par
défaut. Pour créer un administrateur, passez `"role": "admin"` dans le
corps de la requête d'inscription (via Swagger `/docs` ou un client REST),
ou mettez à jour le rôle directement en base MySQL :

```sql
UPDATE users SET role = 'admin' WHERE email = 'votre@email.com';
```

## Structure du projet

```
SmartCampus-AI/
├── backend/
│   ├── app/
│   │   ├── api/          # Routers FastAPI (auth, documents, chat, quiz, dashboard, admin)
│   │   ├── auth/          # JWT, hashing bcrypt, dépendances de rôle
│   │   ├── database/      # Session SQLAlchemy / MySQL
│   │   ├── models/        # Modèles SQLAlchemy (UUID CHAR(36))
│   │   ├── schemas/        # Schémas Pydantic
│   │   ├── services/       # Logique métier
│   │   ├── rag/            # Moteur RAG : chunking, embeddings, FAISS, BM25, LLM, prompt
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/         # Login, Register, Chat, History, Quiz, Flashcards, Documents, Dashboard
│   │   ├── components/    # Sidebar, Layout, ProtectedRoute
│   │   ├── context/        # AuthContext (JWT)
│   │   └── services/       # Client Axios par domaine
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml       # MySQL + Ollama + backend + frontend
└── README.md
```

## Fonctionnalités implémentées

- Authentification JWT avec rôles admin / étudiant
- Import de documents (PDF, DOCX, PPTX, TXT) avec pipeline d'ingestion automatique
- Recherche hybride FAISS + BM25 avec seuil anti-hallucination
- Assistant conversationnel avec mémoire de conversation et citation des sources
- Génération de quiz (QCM) et de flashcards via le LLM, au format JSON structuré
- Tableau de bord administrateur (statistiques d'utilisation, documents et matières les plus consultés)
- Gestion des documents, utilisateurs, départements et matières (admin)

## Notes de conception

- **MySQL** remplace PostgreSQL : les clés primaires UUID sont stockées en
  `CHAR(36)` pour rester portables entre moteurs SQL.
- Le chunking utilise LangChain par défaut, avec un **repli pur Python**
  automatique si LangChain est indisponible.
- Le score de similarité FAISS est comparé à `SIMILARITY_THRESHOLD` (0.35
  par défaut) : en dessous de ce seuil et sans correspondance BM25, l'assistant
  répond qu'il ne dispose pas de l'information plutôt que d'halluciner.
- L'ingestion de documents tourne en tâche de fond (`BackgroundTasks` FastAPI) ;
  pour une charge de production plus importante, remplacez-la par une file
  de tâches (Celery, RQ, etc.).
