
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

- ``end_iteration``
- ``end_simulation``
- ``end_time_step``
- ``get_field``
- ``get_fields``
- ``get_link``
- ``initialize``
- ``is_field_linked``
- ``post_initialize``
- ``run``
- ``save_time_step``
- ``to_scheme``
