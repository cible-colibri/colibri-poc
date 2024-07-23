# COLIBRI
 
Colibri est la démonstration d'une infrastructure de création de modèles numérique versatile, stable, facile à comprendre et à utiliser.

Son but est de fournir 
- un modèle de donnée décrivant un ou plusieurs bâtiments (enveloppe et systèmes)
- une infrastructure permettant de
  - implémenter des modèles numériques de bâtiments et de systèmes, de la météo, de phénomènes physiques, etc.
  - connecter les modèles numériques pour définir un projet de simulation
  - simuler des projets dans le cadre rigoureux de la réglementation, avec un ensemble de modèles et de liens entre modèles prédéfinies et connectés de mannière normalisé
  - simuler des projets définis librement hors de ce contexte

Les objectifs de conception sont :

- _intuitif_ : il devrait être possible d'apprendre à utiliser et à étendre le système simplement en le regardant 
- _modulaire_ : il doit être possible d'ajouter un nouveau phénomène sans aucune connaissance de ceux déjà existants
- _rigoureux_ : il permet de figer une version d'une modélisation pour un contexte donnée (notamment réglementaire)
- _ouvert_ : il devrait pouvoir utiliser la plupart des modèles existants implémentés pour des outils comme MATLAB, TRNSYS, Modellica, ...

L'optimisation du temps de calcul n'est pas abordé à ce stade. 


Le dépôt COLIBRI est constitué des packages suivants :
- **datamodel** : Ce package est destiné à la création et l'exploitation du modèle de donnée détaillé de COLIBRI associé à un ensemble de modules définis et utilisés directement par le moteur de calcul généré.
- **models** : Ce package contient les modèles et méthodes de calcul (au choix de l'utilisateur)
- **core** : les objets de l'infrastructure permettant d'instancier les modèles, créer des connexions liant ces modèles et lancer le calcul
- **utils** : fonctions axillaires

Le répertoire test contient des tests unitaires et d'intégration ainsi que des tests de performance. Ces tests sont éxécutés à chaque modification dans chaque branche, ce qui rend le système stable.




## Installation

### Python
Nous utilisons Python 3.11. Un bon moyen de créer un environnement est d'utiliser conda : 
[distribution Anaconda](https://www.anaconda.com/distribution/) 
ou la [distribution Miniconda3](https://docs.conda.io/en/latest/miniconda.html>). 


### Création de l'environnement conda

Ouvrez une console de commande dans le dossier racine de colibri, puis exécutez :

     conda env create -f ci/environment.yml

Activez l'environnement que vous venez de créer comme ceci :

     conda activate colibri

Pour plus d'informations sur les environnements conda, veuillez visiter https://conda.io/docs/using/envs.html.


### PyCharm

PyCharm est utile pour le développement et la navigation dans le code source. Par exemple, vous pouvez facilement retrouver les **Classes** mentionnées dans cette description en tapant Ctrl-N et le nom de la classe.
La version communautaire est gratuite.
Il peut être [téléchargé ici](https://www.jetbrains.com/fr-fr/pycharm/download/#section=windows>).

## Datamodel
Le package DATAMODEL est constitué des dossiers suivants
- **utils** : On retrouve notamment dans ce dossier "dataset_classes.py" qui rassemble l'ensemble des classes génériques permettant la création ou l'édition d'un modèle de données COLIBRI (class DataSet() ).
- **schemes** : On retrouve les différents schémas de données (et informations associées permettant de le consulter comme une doc via les fonctions describe() ou info() de la class DataSet) utilisés par le modèle de données COLIBRI.
- **examples** : On y retrouve quelques exemples de jeu de données d'entrée au format .json, associé à un plan de situation (en png, lisible dans pycharm) et un module python permettant de générer ou éditer facilement le jeu de données associé en utilisant les fonctions de création et d'édition de utils/dataset_classes.py (DataSet()) 

Créez une nouvelle instance DataSet de la façon suivante :
from datamodel.utils import dataset_classes as dc
jdd = dc.DataSet() (jdd sera utilisé dans la suite du readme)

### DataSet()

La classe DataSet() permet de créer et d'éditer en invite de commande un jeu de données COLIBRI.

DataSet() contrôle que la structure du jeu de données fabriqué répond bien au formalisme imposé par COLIBRI tout en permettant facilement de prendre en compte la modularité de COLIBRI :
- les propriétés des objets ne sont pas toujours les mêmes selon les modules choisis,
- il est facile de faire évoluer la structure du datamodel COLIBRI grâce aux fonctions génériques de DataSet et aux fichiers schemes du dossier "schemes"

Un jeu de donnée COLIBRI est organisé autour de la structure suivante définis par 3 grandes collections :
#### 1. "boundary_collection" : le point de départ, tout élément du bâtiment peut se rattacher et se positionner par rapport à une paroi :
Les "boundaries" (une "boundary") représentent généralement les murs, et cloisons qui cloisonnent les pièces du bâtiment.
De façon plus générique, les boundaries sont les frontières qui séparent des "spaces" (volumes, ex : une pièce). <br>
A chaque boundary sont associés les autres éléments (objects) constituant le bâtiment : des fenêtres, des entrées d'airs, un émetteur qui y est fixé, une chaise qui est posée sur un plancher... <br><br>
**Tous les objects d'une autre nature que boundary sont nécessairement rattachés à une boundary à travers la liste de la boundary "object_collection" (principe de base du jeu de donnée COLIBRI)**.<br><br>
Selon si une représentation 3D du jeu de données est prévue (pas obligatoire !), ce rattachement topologique est associé à un positionnement en x,y,(z) de l'élément **dans le plan de la boundary** (positionnement relatif).
<br>Pour comprendre la manière dont est décrit chaque objet boundary (à ne pas confondre avec les archetype boundary, cf plus bas), n'hésitez pas à utiliser la commande dc.Boundary().describe().

#### 2. "archetype_collection" : la bibliothèque des propriétés des objets :
Si la structure des boundaries et des objets qui leurs sont liés est imposée (cette structure est utilisée pour fixer les propriétés d'intégration des éléments du bâtiment), **les propriétés intrinsèques de chaque objet est décrite au travers d'archetypes**.
Les archetypes permettent :
- de factoriser des propriétés communes à plusieurs objets (bibliothèque de composants) :
<br>Ex : j'ai un type de fenetre double vitrage de dimension 80cm*180cm installé 10 fois dans mon bâtiment. Si il y aura bien 10 objets window positionnés sur différentes façades (boundaries), leurs propriétés intrinsèques seront factorisées dans l'archetype et non répétés dans chaque window. Elles vont se contenter de pointer vers un archetype donné. 
- de faire facilement évoluer les propriétés et caractéristiques intrinsèques demandées en fonction des modules de calculs choisis : ce sont les modules de calculs qui indiquent les paramètres dont ils ont besoin pour simuler. Selon le choix des modules, alors les archetype_scheme évoluent avec les propriétés demandées par chaque module de calcul.
<br>Pour trouver les propriétés demandées par chaque archetype, n'hésitez pas à utiliser la commande jdd.describe("nom de l'archetype") (ex : jdd.describe("layer")).

#### 3. "node_collection" : ce qui lie les élements
Cette collection rassemble les "noeuds" permettant notamment de lier les éléments matériels du bâtiment, à commencer par les boundaries. Les noeuds suivants existent :
- Les spaces : ce sont les volumes délimités par un ensemble clos de boundaries. Cela peut etre usuellement une pièce. Un space est l'unité de calcul spatiale la plus petite : une température par space, etc.
- Les linear_junction : ce sont les connexions linéiques entre objets, typiquement utilisé pour lier les boundaries entre elles sur leurs arrêtes (segments). Même sans interet 3D, les linear_junction sont utilisées pour renseigner des ponts thermiques par exemple.
- Les ponctual_junction : ce sont des connexions point à point entre objets. Utilisées par exemple pour relier des tuyaux entre eux.
- Les boundary_condition : ce sont des noeuds permettant d'imposer des conditions aux limites (à une boundary, à un réseau aréaulique...)
<br>Pour trouver les propriétés demandées par chaque archetype, n'hésitez pas à utiliser la commande jdd.describe("nom du type de noeud") (ex : jdd.describe("linear_junction")).

### Schemes

Dans le dossier "schemes", il existe un .py pour chaque famille d'élément COLIBRI : object, archetype, node.
Si dans le futur object_scheme et node_scheme sont bien sensés s'imposer (être communs) à l'ensemble des modèles de données COLIBRI (et donc rester là), ce n'est pas le cas de archetype_schemes.py qui sera lui dépendant des modules choisis dans l'assemblage moteur de COLIBRI par chacun.
Ainsi les schema écrits aujourd'hui dans archetype_scheme sont voués à disparaitre de "schemes" car ils seront générés à la volée comme la concaténation des paramètres demandés (avec toujours la documentation associée) pour chaque type d'objet par chaque module de calcul COLIBRI.

## Models

Ce package contient les modèles standards fournis, organisés par thème. 

Chaque modèle est une classe qui dérive (directement ou indirectement) de la classe **Model** du package **core**. 

L'API du modèle (l'interface du modèle avec l'extérieur, i.e. sa façon d'échanger des informations avec d'autres modèles) est défini par des objets **Field** (champ), 
définis en tant que dictionnaire attaché automatiquement à la classe Model.

Il définit 

- le nom du champ
- l'unité du champ
- la valeur par défaut du champ
- le role du champ 
  - input : variable d'entrée : la variable reçoit potentiellement des valeurs d'un autre modèle
  - output : variable de sortie : la variable est calculé par le modèle et potentiellement transmis à un autre modèle
  - parameter : valeur constante (ne change pas au fil du temps) mais peut être changé par l'utilisateur pour paramétrer le modèle


Dans un projet (classe **Project**), les modèles peuvent être liés entre eux via les champs d'entrée / sortie pour définir un projet de simulation.

En plus de communiquer via les liens (champs d'entrée / sortie), les modèles peuvent faire appell à des services fournis par le noyau, par exemple :
- un data store représentant le bâtiment avec son enveloppe et ses systèmes (**BuildingData**)
- les données météo pre-calculés par orientation (**Weather**)

Chaque modèle doit implémenter un ensemble de méthodes définissant son comportement. Par exemple : 
- *initialize()* : initialisation du modèle lors de sa création
- *run()* : calcul à chaque itération
- *iteration_done()* : calculs à la fin d'une itération (avant de passer à l'itération suivante)
- *timestep_done()* : calculs à la fin d'un pas de temps (avant de passer au pas de temps suivant)
- *simulation_done()* : calculs à la fin de la simulation (post-traitement)

Ces méthodes sont définies au niveau de la classe **Model** en tant que méthodes abstraites (il n'est pas possible de dériver une classe qui ne définie pas ces méthodes).

La classe **Project** fourni une méthode de résolution numérique de type substitution successive qui permet d'éxécuter la boucle 
de temps et d'itérer au sein d'un même pas de temps si nécessaire : méthode Project.run(). 

Un projet peut être créée en instantiant des objets Python ou à partir d'un fichier de configuration qui défini seulement 
l'ensemble de modèles (classes) utilisées et leurs paramètres (Project.project_from_config()), avec création automatique de liens basés 
sur les noms des champs (méthode Project.auto_link()). 

L'infrastructure permet aussi d'implémenter toute autre méthode de résolution numériques ou de perfectionné la méthode 
basique proposée. On imagine, par exemple, l'ajout d'un facteur de relaxation pour des problèmes de couplage 
thermo-aéraulique, etc.  

## Tests

Les tests sont d'une importance extrême, à la fois pour assurer la stabilité du système et pour assurer sa prise en main. 
Chaque fonctionnalité et chaque concept est couvert par un test. Il est interdit de merger une branche de code dans main tant qu'un teste ne passe pas. 

Actuellement, le test de référence pour le modèle de bâtiment avec ses systèmes est

    colibri/tests/models/thermal/buildings/test_coupled_building.py

Ce test nous sert comme laboratoire pour expérimenter toutes les fonctionnalités et leur intégration. 
Il montre comment créer manuellement un projet en utilisant tous les concepts décrits.
C'est un bon point de départ pour comprendre comment Colibri fonctionne. 