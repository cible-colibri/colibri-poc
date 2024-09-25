
Module
------

Afin d'éviter la multiplication de constantes qui peuvent être similaires entre
des modules (par exemple, la densité de l'air), un fichier
``modules_constants.py`` se trouve dans ``colibri/modules``:

.. code-block:: python

   ...

   # Specific heat capacities
   CP_AIR: float = 1_006.0  # [J/(kg.K)]
   CP_WATER: float = 4_186.0  # [J/(kg.K)]
   # Volumetric air density
   DENSITY_AIR: float = 1.204785775  # [kg/m³]

   ...


