
Project Data
------------

Le **Project Data** traduit le jeu de données d'entrée en objets Python prêt à
être utiliser par le :ref:`project_orchestrator_section`. Ainsi, le Project
Data:

- Contrôle que les paramètres du jeu de données d'entrée transmis sont
  compatibles avec ce que le moteur attend ;
- Si les données sont cohérentes, le Project Data crée les
  :ref:`project_objects_section` (transformation des données d'entrée en objets
  Python) afin de faciliter leur manipulation ;
- Transmet au Project Orchestrator le schéma de calcul via les modules
  sélectionnés.
