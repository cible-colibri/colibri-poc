
Interface de module
-------------------

Une interface de module définit les entrées et les sorties que les modules
doivent avoir afin d'encadrer le processus de calcul. Les entrées proviennent
de calculs antérieurs, faits par d'autres modules. Le module exécute son
processus de calcul afin de mettre à disposition les sorties pour d'autres
modules. Les entrées et sorties sont des données dynamiques de calcul appelées
**variables de simulation**.

^^^^^^^^^^^^^^^^^^^^^^^
Variables de simulation
^^^^^^^^^^^^^^^^^^^^^^^

Les variables de simulation sont les entrées et sorties des modules, imposées
par les interfaces de module. Ce sont des variables mesurables qui évoluent dans
le temps et influencent le comportement d'un système ou d'un processs.

Chaque variable de simulation (entrées et sorties d'un module) est rattachée à
un type de :ref:`project_objects_section`. Si un module ``M-X`` basé sur
l'interface ``IM-X`` a besoin d'une entrée (variable de simulation) ``INP_1``
qui correspond à la température moyenne de l'air d'un espace, alors chaque
espace devra posséder ``INP_1`` dans le fichier d'entrée.




