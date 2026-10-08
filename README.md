# Système de Vérification d'Authenticité de Diplômes

Projet de Fin d'Études réalisé à l'Université Mohammed V de Rabat — Département Informatique, sous la supervision de Pr. Zakaria Izouaoune.

---

## Présentation

La falsification de diplômes et de certificats académiques est un phénomène en progression constante, facilité par la qualité croissante des outils de retouche numérique. Les mécanismes de vérification actuels reposent souvent sur des processus manuels lents ou sur des bases de données centralisées vulnérables.

Ce projet propose une solution décentralisée combinant **filigranage invisible** de documents PDF et **ancrage cryptographique sur blockchain**, permettant à n'importe quel recruteur ou organisme de vérifier l'authenticité d'un diplôme en quelques secondes — sans contacter l'établissement émetteur.

---

## Fonctionnement général

Le système implique deux acteurs principaux : l'**établissement émetteur** et le **vérificateur** (recruteur, organisme, administration).

### 1. Émission

1. L'établissement génère le diplôme en PDF.
2. Un filigrane invisible est intégré au document, contenant un identifiant unique lié à l'étudiant et à sa promotion.
3. Le hash cryptographique SHA-256 du document filigrané est calculé.
4. Ce hash est ancré sur une blockchain, créant une empreinte infalsifiable horodatée.
5. Le diplôme filigrané est remis à l'étudiant.

### 2. Vérification

1. Le vérificateur soumet le diplôme PDF à l'interface de vérification.
2. Le filigrane invisible est extrait du document.
3. Le hash SHA-256 du fichier soumis est recalculé.
4. La blockchain est interrogée pour retrouver l'enregistrement correspondant.
5. Le hash calculé est comparé au hash stocké.
6. Toute modification du document (nom, note, date) altère le hash et déclenche une alerte de falsification.

Le résultat est un booléen : **authentique** ou **falsifié**.

---

## Propriétés clés

- **Décentralisé** — aucun besoin de contacter l'établissement pour vérifier.
- **Auto-portant** — le document lui-même porte sa preuve d'authenticité.
- **Infalsifiable** — toute altération du PDF invalide immédiatement le hash.
- **Public** — n'importe quel vérificateur peut utiliser l'interface sans accès particulier.

---

## Livrables

- **Module d'émission** — insertion de filigrane invisible dans un PDF et calcul du hash.
- **Ancrage blockchain** — écriture du hash sur une chaîne privée ou un réseau de test public.
- **Interface de vérification web** — dépôt de PDF, extraction du filigrane, interrogation blockchain et affichage du résultat.
- **Scénario de démonstration** — émission d'un diplôme test, tentative de falsification et détection automatique.
- **Rapport technique** — protocole d'émission et de vérification reproductible.

---

## Architecture

```
Émission                   Distribution         Vérification
──────────────────────     ──────────────────   ──────────────────────────
Établissement              Étudiant             Vérificateur
  │                          │                    │
  ├─ Générer le PDF           ├─ Reçoit le PDF     ├─ Soumet le PDF
  ├─ Intégrer le filigrane    └─ Partage librement ├─ Extraire le filigrane
  ├─ Calculer le SHA-256                           ├─ Recalculer le hash
  └─ Ancrer le hash                                ├─ Interroger la blockchain
       │                                           └─ Comparer → booléen
       ▼
   Blockchain
```

---

## Diagrammes de séquence

Deux diagrammes PlantUML sont fournis dans le dossier `/docs` :

- `sequence_diagramme_creation_de_diplome_securise.puml` — couvre le flux d'émission complet, de `issueDiploma()` jusqu'à la confirmation blockchain.
- `sequence_diagramme_validation_du_diplome.puml` — couvre le flux de vérification, du dépôt du fichier jusqu'au résultat booléen `isAuthentic`.

---
# Comment demarer l'application

1. Créez un wallet Ethereum et assurez-vous qu'il possède un peu d'ETH Sepolia (testnet).
2. Créez un compte Alchemy (https://www.alchemy.com/), créez une app sur le réseau
   "Ethereum Sepolia", et récupérez votre clé API (juste la clé, pas l'URL complète).
3. Créez un fichier `.env` dans le dossier `Blockchain/` avec :

PRIVATE_KEY=<votre-cle-privee-wallet>
API_KEY=<votre-cle-alchemy>
CONTRACT_ID=

4. Installez la dépendance manquante pour le déploiement :

pip install py-solc-x
5. Creez un fichier `data.json` dans le dossier `Embedding/` 
6. Déployez le smart contract :

cd Blockchain
python3 deploy.py

   Cela compile et déploie `DiplomaRegistry.sol` sur Sepolia, puis remplit
   automatiquement `CONTRACT_ID` dans `.env`.
7. Pour exécuter la plateforme :
   - Sous Windows, exécutez `run.bat`.
   - Sous Ubuntu / n'importe quelle distro Linux, exécutez `run.sh`.
## Informations projet

| Champ | Détail |
|---|---|
| Etablissement | Direction des systemes de l'information |
| Encadrant | M. Allali Abd Alhadi |
| Sujet | Filigranage & Blockchain |
| Duree | Juin-Septembre 2026 |
