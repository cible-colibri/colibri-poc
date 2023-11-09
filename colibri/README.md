# COLIBRI (VF)
 
Le dépot COLIBRI est constitué de deux packages principaux :
- DATAMODEL : Ce package est destiné à la création et l'exploitation du modèle de donnée détaillé de COLIBRI associé à un set de modules définis et utilisés directement par le moteur de calcul généré.
- MODULES : Ce package contient les modèles et méthodes de calcul (au choix de l'utilisateur), ainsi que les connexions liant ces modules (ordonancement du calcul)

## DATAMODEL
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

## MODULES
A faire.