
``ProjectOrchestrator``
-----------------------

Le ``ProjectOrchestrator`` est le chef d'orchestre qui permet de faire jouer
tous les modules (indépendants les uns des autres) ensemble pour effectuer le
calcul global (à savoir la simulation).

Le ``ProjectOrchestrator`` connait tous les modules, qui contiennent tous les
fonctions suivantes :

- ``initialize``
- ``post_initialize``
- ``run``
- ``end_iteration``
- ``end_time_step``
- ``end_simulation``
- ``save_time_step``

Le ``ProjectOrchestrator`` peut donc initialiser tous les modules, faire une
passe sur ceux qui ont besoin d'une post-initialisation, les faire tourner
à chaque pas de temps, avant de leur permettre de finaliser chaque étape (
iteration, pas de temps et simulation) comme ils le souhaitent.

