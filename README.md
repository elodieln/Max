# Max - Assistant IA pour étudiants en électronique

Max est un assistant IA basé sur un système RAG (Retrieval-Augmented Generation) multimodal, spécialement conçu pour aider les élèves en école d'ingénieur en électronique. Il permet aux étudiants de poser des questions sur des concepts d'électronique et reçoit des réponses précises basées sur des cours et documents pertinents.

![Logo Max](./src/assets/images/logo-max.png)

## 🌟 Fonctionnalités

- **Chatbot interactif** avec formatage Markdown pour des réponses structurées
- **Système RAG multimodal** capable de comprendre et analyser texte et images
- **Conservation de l'historique des conversations**
- **Interface utilisateur intuitive** avec effet de frappe pour une expérience naturelle
- **Possibilité d'upload de documents de cours** pour enrichir la base de connaissances
- **Différents types de requêtes** : questions générales, résumés de cours, explications de concepts, etc.

## 🛠️ Technologies utilisées

### Frontend
- React
- Tailwind CSS
- Vite
- Axios pour les appels API
- React Router pour la navigation
- React Markdown pour le formatage des réponses

### Backend
- Python
- FastAPI
- Supabase pour la base de données
- OpenRouter pour l'accès aux modèles LLM
- PyMuPDF pour l'extraction de contenu PDF

## 📋 Prérequis

- Node.js (v16+)
- npm ou yarn
- Python (v3.9+)
- pip
- Un compte Supabase et ses identifiants
- Une clé API OpenRouter

## 🚀 Installation

### Préparation de l'environnement

1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/elodieln/Max.git
   cd Max
   ```

2. Créez et activez un environnement virtuel Python pour le backend :
   ```bash
   python -m venv venv
   
   # Sur Windows
   venv\Scripts\activate
   
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. Installez les dépendances frontend :
   ```bash
   npm install
   ```


4. Installez les dépendances backend :
   ```bash
   cd rag
   pip install -r requirements.txt
   ```

### Configuration

1. Créez un fichier `.env` dans le dossier `rag` avec les informations suivantes :
   ```
   # Supabase
   SUPABASE_URL=votre_url_supabase
   SUPABASE_KEY=votre_cle_supabase

   # OpenRouter
   OPENROUTER_API_KEY=votre_cle_openrouter

   # Configuration LLM
   DEFAULT_MODEL=gpt-3.5-turbo-16k
   ADVANCED_MODEL=gpt-4o
   ```

## 🎮 Démarrage

1. Démarrez le serveur backend API :
   ```bash
   cd rag
   # Assurez-vous que l'environnement virtuel est activé
   python src/main_api.py
   ```
   Le serveur démarrera sur `http://localhost:8000`

2. Dans un autre terminal, démarrez l'application frontend :
   ```bash
   # À la racine du projet
   npm run dev
   ```
   L'application sera accessible sur `http://localhost:5173` (ou sur le port indiqué)

## 💬 Utilisation du chatbot

1. Naviguez vers la page du chatbot via le menu principal
2. Posez une question liée à l'électronique dans le champ de texte
3. Max analysera votre question et fournira une réponse détaillée basée sur sa base de connaissances
4. L'historique de vos conversations est sauvegardé automatiquement

### Types de requêtes supportées

- **question** : Question générale (par défaut)
- **json** : Génération d'une fiche de cours au format JSON
- **concept** : Explication d'un concept spécifique
- **cours** : Génération d'un résumé de cours
- **probleme** : Résolution d'un problème électronique

## 📚 Gestion des documents

L'interface permet également de :
1. Télécharger des documents PDF de cours
2. Visualiser les cours disponibles dans le système
3. Explorer le contenu des cours existants

## 🧪 Développement et tests

Pour les développeurs souhaitant contribuer au projet, voici quelques commandes utiles :

```bash
# Construction du projet pour la production
npm run build

# Prévisualisation de la build
npm run preview
```

## 🔨 Structure du projet

```
max/
├── public/                # Fichiers statiques
├── rag/                   # Backend RAG multimodal
│   ├── config/            # Configuration backend
│   ├── data/              # Données et images extraites
│   ├── src/               # Code source backend
│   │   ├── api/           # API FastAPI
│   │   ├── embeddings/    # Gestion des embeddings
│   │   ├── processing/    # Traitement des documents
│   │   └── ...
│   └── tests/             # Tests backend
├── src/                   # Frontend React
│   ├── assets/            # Images et ressources
│   ├── components/        # Composants React réutilisables
│   ├── pages/             # Pages de l'application
│   │   ├── Chatbot/       # Page du chatbot
│   │   └── ...
│   ├── services/          # Services et API clients
│   └── ...
└── ...
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commitez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence [MIT](LICENSE).

## 👥 Équipe

Développé par l'équipe Max avec :
- Équipe Frontend : Développement de l'interface utilisateur
- Équipe Backend : Développement du système RAG multimodal et de l'API

---

© 2025 Projet Max - Tous droits réservés