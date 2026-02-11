# Jenkins Security Log Analysis Project

**Mini-projet du cours "Sécurité systèmes"**  
Construction de jeux de données de logs applicatifs pour la détection d'attaques

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation rapide](#installation-rapide)
- [Utilisation](#utilisation)
- [Scénarios implémentés](#scénarios-implémentés)
- [Règles de détection](#règles-de-détection)
- [Structure du projet](#structure-du-projet)
- [Analyse des logs dans Kibana](#analyse-des-logs-dans-kibana)
- [Documentation technique](#documentation-technique)

---

## 🎯 Vue d'ensemble

Ce projet implémente une plateforme complète de génération et d'analyse de logs de sécurité pour Jenkins, un serveur CI/CD populaire. Il permet de :

1. **Générer des logs réalistes** via des scénarios d'utilisation normale et malveillante
2. **Collecter et centraliser** les logs avec Elastic Stack (ELK)
3. **Détecter les attaques** via des règles de détection
4. **Visualiser** les incidents de sécurité dans Kibana

### Objectifs pédagogiques atteints

✅ Déploiement d'applications réelles (Jenkins)  
✅ Collecte de logs applicatifs avec Elastic Stack  
✅ Conception de scénarios légitimes et malveillants  
✅ Tests de charge multi-utilisateurs  
✅ Transformation et annotation des logs  
✅ Création de règles de détection  
✅ Production d'un dataset scientifiquement exploitable

---

## 🏗️ Architecture

```
┌─────────────┐
│   Jenkins   │ ← Application cible
│   :8080     │
└──────┬──────┘
       │ logs
       ↓
┌─────────────┐
│  Filebeat   │ ← Collecte des logs
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Logstash   │ ← Parsing et enrichissement
└──────┬──────┘
       │
       ↓
┌─────────────┐
│Elasticsearch│ ← Stockage et indexation
│   :9200     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Kibana    │ ← Visualisation et détection
│   :5601     │
└─────────────┘
```

### Composants

- **Jenkins** : Serveur CI/CD générant les logs applicatifs
- **Filebeat** : Agent de collecte des logs Jenkins
- **Logstash** : Pipeline de traitement et enrichissement des logs
- **Elasticsearch** : Moteur de recherche et stockage des logs
- **Kibana** : Interface de visualisation et d'analyse

---

## 💻 Prérequis

### Logiciels requis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python 3** (version 3.8+)
- **Pip3** pour les dépendances Python

### Ressources système recommandées

- **RAM** : 8 GB minimum
- **Espace disque** : 10 GB minimum
- **CPU** : 4 cores minimum

### Vérification

```bash
docker --version
docker-compose --version
python3 --version
```

---

## 🚀 Installation rapide

### 1. Cloner ou extraire le projet

```bash
cd jenkins-security-logs
```

### 2. Lancer tous les services

```bash
./run.sh
```

Sélectionnez l'option **5** pour exécuter la démonstration complète.

### 3. Accéder aux interfaces

Une fois les services démarrés :

- **Jenkins** : http://localhost:8080
  - Username: `admin`
  - Password: `admin123`

- **Kibana** : http://localhost:5601
  - Pas d'authentification requise

- **Elasticsearch** : http://localhost:9200

---

## 📖 Utilisation

### Menu interactif

Le script `run.sh` offre un menu interactif :

```
1) Start all services              - Démarrer Jenkins + ELK
2) Setup Kibana                    - Configurer les dashboards
3) Run normal usage scenarios      - Trafic légitime
4) Run attack scenarios            - Trafic malveillant
5) Run full demo                   - Démo complète
6) Show service logs               - Afficher les logs Docker
7) Stop all services               - Arrêter les services
8) Cleanup                         - Supprimer toutes les données
9) Exit                            - Quitter
```

### Exécution manuelle

#### Démarrer les services

```bash
cd docker
docker-compose up -d
```

#### Configurer Kibana

```bash
python3 scripts/setup_kibana.py
```

#### Exécuter les scénarios normaux

```bash
python3 scripts/normal_scenarios.py
```

#### Exécuter les scénarios d'attaque

```bash
python3 scripts/attack_scenarios.py
```

---

## 🎭 Scénarios implémentés

### Scénarios normaux (trafic légitime)

| Scénario | Description | Fréquence |
|----------|-------------|-----------|
| **Login utilisateur** | Authentification légitime | Haute |
| **Consultation dashboard** | Visualisation de la page d'accueil | Haute |
| **Liste des jobs** | Récupération de la liste des projets | Moyenne |
| **Visualisation job** | Consultation d'un job spécifique | Moyenne |
| **Déclenchement build** | Lancement d'un build légitime | Moyenne |
| **Consultation logs** | Lecture des logs de build | Moyenne |
| **Vérification statut** | Monitoring de l'état des builds | Haute |

### Scénarios d'attaque

| Attaque | MITRE ATT&CK | Gravité | Description |
|---------|--------------|---------|-------------|
| **Brute Force Login** | T1110.001 | 🔴 HIGH | Tentatives multiples de connexion avec différents mots de passe |
| **Credential Stuffing** | T1110.004 | 🔴 HIGH | Test de couples username/password volés |
| **Path Traversal** | T1083 | 🔴 HIGH | Tentative d'accès aux fichiers système via traversée de répertoires |
| **Script Console Exploitation** | T1059.007 | 🔴 CRITICAL | Exécution de code malveillant via la console Groovy |
| **API Enumeration** | T1087 | 🟡 MEDIUM | Scan des endpoints API pour découvrir des informations |
| **DoS Build Triggering** | T1499 | 🔴 HIGH | Déni de service par déclenchement massif de builds |
| **Unauthorized Access** | T1078 | 🔴 HIGH | Tentative d'accès à des ressources protégées |

---

## 🛡️ Règles de détection

### Règles implémentées dans Elasticsearch

#### 1. Multiple Failed Login Attempts
```kql
log_type: "jenkins_access" AND response_code: (401 OR 403)
```
**Seuil** : 5 tentatives par IP en 5 minutes  
**Gravité** : HIGH

#### 2. Suspicious API Enumeration
```kql
log_type: "jenkins_access" AND request_path: /api/*
```
**Seuil** : 10 requêtes par IP en 1 minute  
**Gravité** : MEDIUM

#### 3. Script Console Access
```kql
log_type: "jenkins_access" AND request_path: "/script"
```
**Seuil** : 1 accès  
**Gravité** : CRITICAL

#### 4. Path Traversal Attempt
```kql
log_type: "jenkins_access" AND request_path: (*../* OR *..\\* OR *%2e%2e*)
```
**Seuil** : 1 tentative  
**Gravité** : HIGH

#### 5. Excessive Build Triggering
```kql
log_type: "jenkins_access" AND request_path: */build
```
**Seuil** : 10 builds par IP en 1 minute  
**Gravité** : HIGH

#### 6. Unauthorized Admin Access
```kql
log_type: "jenkins_access" AND 
request_path: (/configure OR /manage OR /script OR /systemInfo) AND
response_code: (401 OR 403)
```
**Seuil** : 1 tentative  
**Gravité** : CRITICAL

---

## 📁 Structure du projet

```
jenkins-security-logs/
├── docker/
│   ├── docker-compose.yml          # Configuration Docker Compose
│   ├── filebeat/
│   │   └── filebeat.yml            # Config Filebeat
│   ├── logstash/
│   │   ├── pipeline/
│   │   │   └── jenkins.conf        # Pipeline Logstash
│   │   └── config/
│   │       └── logstash.yml        # Config Logstash
│   └── jenkins/
│       └── init.groovy.d/          # Scripts d'initialisation Jenkins
│           ├── 01-configure-jenkins.groovy
│           └── 02-create-sample-jobs.groovy
├── scripts/
│   ├── normal_scenarios.py         # Scénarios d'utilisation normale
│   ├── attack_scenarios.py         # Scénarios d'attaque
│   └── setup_kibana.py             # Configuration Kibana
├── scenarios/                       # Documentation des scénarios
├── docs/                           # Documentation détaillée
├── run.sh                          # Script principal
└── README.md                       # Ce fichier
```

---

## 📊 Analyse des logs dans Kibana

### 1. Accéder à Kibana

Ouvrir http://localhost:5601

### 2. Naviguer vers Discover

Menu latéral → **Discover**

### 3. Sélectionner l'index pattern

Choisir **jenkins-logs-*** dans le sélecteur d'index

### 4. Exemples de recherches KQL

#### Voir tous les échecs d'authentification
```kql
log_type: "jenkins_access" AND response_code: (401 OR 403)
```

#### Identifier les tentatives de brute force
```kql
log_type: "jenkins_access" AND response_code: 401 
| stats count by client_ip 
| where count > 5
```

#### Détecter le path traversal
```kql
log_type: "jenkins_access" AND request_path: (*../* OR *..\\* OR *%2e%2e*)
```

#### Accès à la console script
```kql
log_type: "jenkins_access" AND request_path: "/script"
```

#### Analyse temporelle des attaques
```kql
log_type: "jenkins_access" AND response_code >= 400
| stats count by @timestamp
```

---

## ⚠️ Avertissements

### Utilisation éthique

⚠️ **IMPORTANT** : Ce projet est destiné uniquement à des fins éducatives et de recherche.

- ✅ Utiliser **uniquement** dans un environnement contrôlé
- ✅ Ne **jamais** tester sur des systèmes externes
- ✅ Respecter les lois et réglementations en vigueur
- ❌ Ne **pas** utiliser les techniques d'attaque sur des systèmes réels

### Sécurité

- Les credentials par défaut (`admin:admin123`) sont **intentionnellement faibles**
- Désactiver CSRF et SSL pour faciliter les tests
- Ne **jamais** exposer cette configuration sur Internet

---

## 🔧 Dépannage

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d
```

### Elasticsearch ne démarre pas

```bash
# Augmenter la mémoire virtuelle (Linux/Mac)
sudo sysctl -w vm.max_map_count=262144
```

### Jenkins ne répond pas

```bash
# Vérifier l'état du conteneur
docker ps
docker logs jenkins

# Redémarrer Jenkins
docker-compose restart jenkins
```

---

## 📚 Documentation

Pour plus d'informations, consultez :

- [QUICKSTART.md](QUICKSTART.md) - Guide de démarrage rapide
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Guide d'installation détaillé
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture technique
- [scenarios/SCENARIOS.md](scenarios/SCENARIOS.md) - Détails des scénarios

---

**Projet réalisé dans le cadre du cours "Sécurité systèmes"**  
*Construction de jeux de données de logs applicatifs pour la détection d'attaques*
