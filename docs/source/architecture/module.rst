
Module
------

Les algorithmes de calcul des sorties de l'interface de module à partir des
entrées de l'interface de module sont définis au niveau du **module**. Les
**paramètres** demandés par un module varient en fonction de ses algorithmes.
Par conséquent, le jeu de données d'entrée devra donc évoluer en fonction des
modules choisis afin d'inclure tous les paramètres nécessaires.

Un module est nécessairement défini par rapport à une interface, dont il hérite
les entrées et sorties (variable de simulation) pour être interchangeable avec
un autre module issu de la même interface.

Paramètres
^^^^^^^^^^

Les paramètres de modules sont des données constantes, non modifiées par le
temps, et sont directement dérivées des choix algorithmiques au sein des
modules. Contrairement aux variables de simulations, les valeurs associées aux
paramètres proviennent du jeu de données d'entrée (soit à via les
:ref:`project_objects_section` soit via les modules).





