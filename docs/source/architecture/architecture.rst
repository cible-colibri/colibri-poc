
Architecture de ``colibri``
===========================

L'architecture de colibri est organisé en **modules**, chacun permettant de
faire des calculs distincts de manière autonome. L'objectif de cette structure
est de développer, modifier ou remplacer des modules sans affeter le reste du
code, à condition que chaque module respecte les spécifications d'entrée et de
sortie prévues. Ainsi,

- Chaque module est uniquement contraint par ses entrées et sorties (variables
  de simulation) définies par son **interface de module**, qui constitue le
  contrat d'interaction avec les autres modules et détermine le rôle du module
  (implémentant l'interface) dans le calcul global ;
- Le contenu algorithme d'un module peut être entièrement modifié, à condition
  de maintenir la conformité des entrées et sorties imposées par l'interface de
  module.

.. include:: interface.rst
.. include:: module.rst
.. include:: schema.rst
.. _project_orchestrator_section:
.. include:: project_orchestrator.rst
.. _project_data_section:
.. include:: project_data.rst
.. _project_objects_section:
.. include:: project_objects.rst
