# 💊 Dashboard Médicaments Maroc

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Plotly](https://img.shields.io/badge/Plotly-5.17.0-red.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🏥 **Dashboard interactif pour l'analyse et la visualisation des données pharmaceutiques marocaines**

Un tableau de bord moderne permettant d'explorer une base de données de plus de **5000 médicaments** avec des visualisations interactives et des statistiques détaillées du marché pharmaceutique marocain.

## 🎯 Aperçu

![Dashboard Preview](https://via.placeholder.com/800x400/667eea/ffffff?text=Dashboard+M%C3%A9dicaments+Maroc)

### ✨ Fonctionnalités Principales

- 📊 **6 Visualisations Interactives** avec Plotly.js
- 🎨 **Design Moderne** avec Glass Morphism
- 📱 **Interface Responsive** (Desktop, Tablet, Mobile)
- 🔍 **Recherche en Temps Réel** (interface préparée)
- 📈 **Statistiques Détaillées** du marché pharmaceutique
- ⚡ **Performance Optimisée** avec mise en cache

## 🚀 Démo en Direct

🌐 **[Voir la Démo](https://votre-demo-url.com)** *(Remplacez par votre URL de déploiement)*

## 📋 Table des Matières

- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)
- [Technologies](#-technologies)
- [Structure du Projet](#-structure-du-projet)
- [Visualisations](#-visualisations)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

## 🛠️ Installation

### Prérequis

- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/HamzaBraik01/Dashboard_M-dicaments.git
cd Dashboard_M-dicaments

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

### 🌐 Accès

Ouvrez votre navigateur et accédez à : **http://localhost:5000**

## 🎮 Utilisation

### Dashboard Principal

Le dashboard affiche automatiquement :

- **📊 Statistiques Générales** : Total médicaments, prix moyen, distributeurs, classes thérapeutiques
- **📈 6 Graphiques Interactifs** : Classes thérapeutiques, distribution des prix, top distributeurs, etc.
- **🔄 Actualisation Automatique** : Données mises à jour en temps réel

### Navigation

```
/ ...................... Dashboard principal
/data .................. Vue tabulaire des données
/api/search ............ Recherche de médicaments
```

## 🔌 API Endpoints

| Endpoint | Description | Méthode |
|----------|-------------|---------|
| `/` | Dashboard principal | GET |
| `/api/classe-therapeutique` | Top 10 classes thérapeutiques | GET |
| `/api/distribution-prix` | Histogramme des prix | GET |
| `/api/top-distributeurs` | Top 8 distributeurs | GET |
| `/api/formes-medicaments` | Formes pharmaceutiques | GET |
| `/api/prix-comparaison` | Comparaison prix public/hospitalier | GET |
| `/api/substances-psychoactives` | Substances contrôlées | GET |
| `/api/search?q={query}` | Recherche médicaments | GET |
| `/data` | Vue tabulaire complète | GET |

### Exemple d'utilisation API

```javascript
// Récupérer les données des classes thérapeutiques
fetch('/api/classe-therapeutique')
  .then(response => response.json())
  .then(data => {
    // Données au format Plotly.js
    Plotly.newPlot('chart-div', data.data, data.layout);
  });
```

## 🏗️ Technologies

### Backend
- **Flask 2.3.3** - Framework web Python
- **Pandas 2.0.3** - Manipulation des données
- **NumPy 1.24.3** - Calculs numériques
- **Plotly 5.17.0** - Visualisations interactives

### Frontend
- **HTML5 / CSS3** - Structure et style
- **JavaScript ES6** - Interactions dynamiques
- **Plotly.js** - Graphiques interactifs
- **Font Awesome 6** - Icônes modernes

### Design
- **Glass Morphism** - Effet de verre moderne
- **Gradients CSS** - Dégradés vibrants
- **Responsive Design** - Compatible tous écrans
- **Animations CSS** - Transitions fluides

## 📁 Structure du Projet

```
Dashboard_Médicaments/
├── 📄 app.py                      # Application Flask principale
├── 📊 medicament_ma_top5000.csv   # Dataset des médicaments (5000+)
├── 📋 requirements.txt            # Dépendances Python
├── 📘 README.md                   # Documentation (ce fichier)
├── 📝 RAPPORT_PROJET.md           # Rapport technique détaillé
├── 🐍 scraper.py                  # Script de collecte de données
└── 📁 templates/
    └── 🎨 dashboard.html          # Interface utilisateur principale
```

## 📊 Visualisations

### 1. 🧬 Classes Thérapeutiques
Graphique en barres horizontales affichant le top 10 des classes médicamenteuses les plus représentées.

### 2. 💰 Distribution des Prix
Histogramme moderne montrant la répartition des prix des médicaments (en DHS).

### 3. 🏭 Top Distributeurs
Graphique circulaire (donut chart) des 8 principaux distributeurs/fabricants.

### 4. 💊 Formes de Médicaments
Barres horizontales des différentes formes pharmaceutiques (comprimés, sirops, etc.).

### 5. 📈 Comparaison des Prix
Graphique linéaire comparant les prix publics vs hospitaliers.

### 6. ⚠️ Substances Psychoactives
Analyse des médicaments contenant des substances contrôlées.

## 🔍 Données

### 📊 Dataset
- **5000+ médicaments** référencés
- **15+ attributs** par médicament
- **Sources** : Données du marché pharmaceutique marocain

### 🧹 Traitement des Données
- Nettoyage automatique des balises HTML
- Normalisation des prix et formats
- Suppression des doublons
- Validation et contrôle qualité

### 📋 Attributs Principaux
- `name` - Nom du médicament
- `Classe thérapeutique` - Classification médicale
- `PPV` / `Prix hospitalier` - Tarification
- `Distributeur ou fabriquant` - Entreprise
- `Forme` - Forme pharmaceutique
- `Composition` - Principes actifs
- `Indication(s)` - Utilisations thérapeutiques

## 🤝 Contribuer

Les contributions sont les bienvenues ! 

### Comment contribuer

1. **Fork** le projet
2. Créez une **branche feature** (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

### 🐛 Signaler un Bug

Utilisez les [Issues GitHub](https://github.com/HamzaBraik01/Dashboard_M-dicaments/issues) pour signaler des bugs ou proposer des améliorations.

## 📸 Screenshots

<details>
<summary>Voir les captures d'écran</summary>

### Dashboard Principal
![Dashboard](https://via.placeholder.com/600x400/667eea/ffffff?text=Dashboard+Principal)

### Visualisations
![Graphiques](https://via.placeholder.com/600x400/764ba2/ffffff?text=Graphiques+Interactifs)

### Mobile Responsive
![Mobile](https://via.placeholder.com/300x600/f093fb/ffffff?text=Version+Mobile)

</details>

## 🗺️ Roadmap

- [ ] 🔍 **Recherche avancée** avec filtres multiples
- [ ] 📤 **Export des données** (PDF, Excel, CSV)
- [ ] 🔄 **Comparateur** de médicaments
- [ ] 📊 **Historique des prix** et tendances
- [ ] 🔐 **Authentification** utilisateur
- [ ] 🌐 **API publique** pour développeurs
- [ ] 🗄️ **Base de données** PostgreSQL/MongoDB
- [ ] 📱 **Application mobile** native

## 📝 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Hamza Braik**
- GitHub: [@HamzaBraik01](https://github.com/HamzaBraik01)
- LinkedIn: [HamzaBraik](www.linkedin.com/in/hamza-braik-a221b326a)
- Email: hamzabraik02@gmail.com


---

## 🙏 Remerciements

- 🏥 **Ministère de la Santé Maroc** pour les données pharmaceutiques
- 🎨 **Plotly** pour les visualisations interactives
- 🐍 **Flask Community** pour le framework web
- 💎 **CSS Glass Morphism** inspirations de design moderne

---

⭐ **N'oubliez pas de donner une étoile si ce projet vous aide !**

[![GitHub stars](https://img.shields.io/github/stars/HamzaBraik01/Dashboard_M-dicaments.svg?style=social&label=Star)](https://github.com/HamzaBraik01/Dashboard_M-dicaments/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/HamzaBraik01/Dashboard_M-dicaments.svg?style=social&label=Fork)](https://github.com/HamzaBraik01/Dashboard_M-dicaments/network/members)