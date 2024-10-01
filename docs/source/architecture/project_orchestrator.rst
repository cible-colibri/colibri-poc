
Project Orchestrator
--------------------

Le **Project Orchestrator** est le chef d'orchestre qui permet de faire jouer
tous les modules (indépendants les uns des autres) ensemble pour effectuer le
calcul global (à savoir la simulation).

À partir d'un schéma de calcul qui lui est transmis (par le
:ref:`project_data_section`), le Project Orchestrator va:

- Préparer le moteur ;
- Exécuter la simulation (calcul global) ;
- Finaliser la simulation.

Préparation du moteur
^^^^^^^^^^^^^^^^^^^^^

Le Project Orchestrator va:

- Analyser la liste des variables de simulations (entrées et sorties des
  interfaces de modules) du schéma pour les connecter entre elles, c'est-à-dire,
  "quel module doit alimente quel module";
- toto.