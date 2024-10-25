
Création des modules
--------------------

Tous les modules sont récupérables depuis ``colibri.modules``. Seul le nom
(``name``) d'un module est obligatoire à sa création :

.. code-block:: python

    from colibri.modules import LimitedGenerator

    limited_generator: LimitedGenerator = LimitedGenerator(name="limited_generator-1")


Tous les modules contiennent des champs suivants :

- ``_fields_metadata``
- ``inputs``
- ``name``
- ``outputs``,
- ``parameters``
- ``project``

Tous les modules contiennent des fonctions suivantes :

Fonctions à redéfinir pour chaque module liées au cycle de vie des modules

- ``initialize``
- ``run``
- ``has_converged``
- ``end_iteration``
- ``end_time_step``
- ``end_simulation``


Autres fonctions

- ``get_field``
- ``get_fields``
- ``get_link``
- ``is_field_linked``
- ``save_time_step``
- ``to_scheme``
- ``to_template``
- ``from_template``
