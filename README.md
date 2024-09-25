# py_moteur_3cl_tribu [![Latest Release](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/badges/release.svg)](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/releases)

|                        | **main branch** | **develop branch** |
|------------------------|-----------------|--------------------|
| Status                 | [![pipeline status](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/badges/main/pipeline.svg)](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/commits/main)                                                                                                                                                                                 | [![pipeline status](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/badges/develop/pipeline.svg)](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/commits/develop)                                                                                                                                                               |
| Coverage               | [![coverage report](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/badges/main/coverage.svg)](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/commits/main)                                                                                                                                                                                 | [![coverage report](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/badges/develop/coverage.svg)](https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/commits/develop)                                                                                                                                                               |
| Quality gate sonarqube | [![Quality Gate Status](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=alert_status&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric&branch=main)          | [![Quality Gate Status](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=alert_status&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric&branch=develop)
| Maintainability        | [![Maintainability Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=sqale_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)   | [![Maintainability Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=sqale_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)   |
| Reliability            | [![Reliability Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=reliability_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main) | [![Reliability Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=reliability_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop) |
| Security               | [![Security Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=security_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)       | [![Security Rating](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=security_rating&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)       |

## Table des matières

* [Informations générales](#informations-générales)
* [Documentation](#documentation)
* [Installation](#installation)
* [Voir toutes les versions](#voir-toutes-les-versions)
* [Directives pour le développement](#directives-pour-le-développement)
* [Projets en lien avec ce répertoire](#projets-en-lien-avec-ce-répertoire)
* [Badges additionnels](#badges-additionnels)

## Informations générales

Le paquet `py_moteur_3cl_tribu` permet de faire tourner le moteur DPE (Diagnostic de Performance Énergétique). 

## Documentation

La documentation est actuellement hébergée à l'adresse suivante :

https://dee.scm-pages.cstb.fr/py_moteur_3cl_tribu/

### Mise à jour de la DLL du moteur

Étapes :

* Récupérer la DLL auprès du ministère (contact: clement.dimanche@developpement-durable.gouv.fr) ;
* Si la DLL n'est pas déjà compilée, c'est-à-dire si le fichier .dll n'est pas déjà présent, alors il faut demander à Patrick de compiler le projet C# (fichier "Moteur_DPE.dll") ;
* Aller dans : dll/x64/net452 récupérer le fichier "Moteur_DPE.dll" et remplacer celui existant dans le dossier correspondant dll du module (py_moteur_3cl_tribu/py_moteur_3cl_tribu/dll).

### Notes de développement

* paroi ancienne -> combinaison inertie lourde + paroi ancienne = oui. (cf. méthode de calcul)
* type_logement -> methode_application_log
* SSE on refait le point avec antoine. 

## Installation

Installation du paquet se fait via l'artifactory comme suit :

```bash
pip install py_moteur_3cl_tribu
```

Si besoin, voir [Comment se connecter au pypi interne CSTB DEE pour installer des paquets Python](https://scm.cstb.fr/dee/menta/wiki/-/wikis/Comment-se-connecter-au-pypi-interne-CSTB-DEE-pour-installer-des-paquets-Python).

## Voir toutes les versions

Toutes les versions et les modifications apportées d'une version à l'autre sont disponibles dans le document : `CHANGELOG.md`.

Ce document se trouve à la racine du projet ou est accessible à : https://scm.cstb.fr/dee/py_moteur_3cl_tribu/-/blob/main/CHANGELOG.md

## Projets/Outils en lien avec ce répertoire

Les projets et outils en lien avec ce répertoire sont les suivants (et sont donc à prévenir en cas de modifications majeures) :

### Projets actuels et à venir 

- https://scm.cstb.fr/dee/epcrecast/epc-recast-webservice

### Outils en lien :

- A définir

## Badges additionnels

|                        | **main branch** | **develop branch** |
|------------------------|-----------------|--------------------|
| Bugs                   | [![Bugs](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=bugs&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)                                     | [![Bugs](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=bugs&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)                                     |
| Code smells            | [![Code Smells](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=code_smells&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)                       | [![Code Smells](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=code_smells&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)                       |
| Duplicated lines       | [![Duplicated Lines (%)](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=duplicated_lines_density&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main) | [![Duplicated Lines (%)](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=duplicated_lines_density&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop) |
| Security hotspots      | [![Security Hotspots](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=security_hotspots&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)           | [![Security Hotspots](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=security_hotspots&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)           |
| Technical debt         | [![Technical Debt](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=sqale_index&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)                    | [![Technical Debt](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=sqale_index&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)                    |
| Vulnerabilities        | [![Vulnerabilities](https://sonar.cstb.fr/api/project_badges/measure?branch=main&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=vulnerabilities&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=main)               | [![Vulnerabilities](https://sonar.cstb.fr/api/project_badges/measure?branch=develop&project=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&metric=vulnerabilities&token=sqb_71aad6a7138eacd731b826fddd3430396ee891d5)](https://sonar.cstb.fr/dashboard?id=dee_py_moteur_3cl_tribu_AZEoDWt3Xl1KtPpJsVp0&branch=develop)                                 |