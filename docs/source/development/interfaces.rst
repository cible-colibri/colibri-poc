
Interface de module
-------------------

L'interface de module est la première brique dans le développement d'un module,
étant donné que l'interface d'un module définit les entrées et les sorties que
le module doit avoir afin d’encadrer le processus de calcul.

Interface existante
^^^^^^^^^^^^^^^^^^^

Si une interface existe déjà (par exemple ``InterfaceModuleExample``),
il suffira de l'importer pour que le module puisse en hériter :

.. code-block:: python

    from colibri.interfaces import InterfaceModuleExample

    class ModuleExample(InterfaceModuleExample):
        """Class representing a ModuleExample."""

        def __init__(
            self,
            name: str,
            input_or_output_for_interface: float = 0.0,
            parameter_for_module: bool = False,
        ) -> None:
            """Initialize a new ModuleExample instance."""
            super().__init__(
                name=name,
                input_or_output_for_interface=input_or_output_for_interface,
            )
            self.parameter_for_module = parameter_for_module


Création d'une interface
^^^^^^^^^^^^^^^^^^^^^^^^

Si une interface n'existe pas encore, elle peut être ajoutée dans le dossier
``src/colibri/interfaces/modules``:

.. code-block:: bash

    src
    ├── colibri
    │ ├── config
    │ ├── core
    │ ├── interfaces
    │ │ ├── __init__.py
    │ │ ├── module.py
    │ │ ├── modules
    │ │ └── project_objects
    │ ├── mixins
    │ ├── modules

    ...

Une interface (par exemple ``InterfaceModuleExample``) prend la forme suivante :

.. code-block:: python

    """
    ModuleExample interface.
    """

    import abc
    from typing import Dict

    from colibri.interfaces.module import Module
    from colibri.utils.colibri_utils import Attachment
    from colibri.utils.enums_utils import (
        ColibriProjectObjects,
        Units,
    )


    class InterfaceModuleExample(Module, metaclass=abc.ABCMeta):
        """Class representing a ModuleExample interface."""

        def __init__(
            self,
            name: str,
            interface_input: Dict[str, float],
            interface_output: Dict[str, float],
        ) -> None:
            """Initialize a new InterfaceModuleExample instance."""
            super().__init__(name=name)
            self.interface_input = self.define_input(
                name="interface_input",
                default_value=interface_input,
                description="Description of the interface input.",
                format=Dict[str, float],
                min=0,
                max=float("inf"),
                unit=Units.WATT,
                attached_to=Attachment(
                    category=ColibriProjectObjects.SPACE,
                    description="Description of the interface input for the object it is attached to.",
                    format=float,
                ),
            )
            self.interface_output = self.define_output(
                name="interface_output",
                default_value=interface_output,
                description="Description of the interface output.",
                format=Dict[str, float],
                min=0,
                max=float("inf"),
                unit=Units.WATT,
                attached_to=Attachment(
                    category=ColibriProjectObjects.BOUNDARY_OBJECT,
                    class_name="Emitter",
                    description="Power provided by the emitter.",
                    format=float,
                ),
            )

Une interface de module doit :

- Hériter de la class ``Module`` (afin d'avoir toutes les fonctions
  ``initialize``, ``run``, etc.) ;
- Hériter de la meta-class ``abc.ABCMeta`` (afin d'éviter que l'interface soit
  instanciable) ;
- Créer des entrées et/ou sorties via les fonctions ``self.define_input`` et
  ``self.define_output`` issues de la class ``Module``.

Une interface peut avoir uniquement une ou plusieurs entrées ou une ou
plusieurs sorties, mais doit définir au moins une entrée ou une sortie.

.. _fonctions_define_input_output_section:

Fonctions ``define_input`` et  ``define_output``
""""""""""""""""""""""""""""""""""""""""""""""""

Les fonctions ``define_input`` et ``define_output`` demande:

- ``name`` : le nom de l'entrée ou la sortie ;
- ``default_value`` : la valeur par défaut de l'entrée ou la sortie ;
- ``description`` : la description par défaut de l'entrée ou la sortie ;
- ``format`` : le format de l'entrée ou la sortie ;
- ``min`` : la valeur minimum de l'entrée ou la sortie ;
- ``max`` : la valeur maximum de l'entrée ou la sortie ;
- ``unit`` : unité de l'entrée ou la sortie ;
- ``attached_to`` : object auquel l'entrée ou la sortie est attachée.

.. WARNING::
  Le format ne doit pas être une chaîne de charactères, mais le format Python.

Plus d'informations sur ces fonctions dans :ref:`meta_fields_mixin_section`,
étant donné qu'elles sont héritées de ``Module``, qui les hérite
``MetaFieldMixin``.

Attached_to
"""""""""""

La paramètre ``attached_to`` permet d'attacher une entrée ou une sortie à un des
:ref:`project_objects_section` au travers de la classe ``Attachment`` issue de
``colibri.utils.colibri_utils`` (voir :ref:`colibri_utils_section`).

La variable ``self.interface_input`` (dans l'exemple ``InterfaceModuleExample``
plus haut) pourrait provenir d'un module (et donc d'une sortie d'une interface
de module) qui pour chaque ProjectObject ``Space`` associe une valeur (par
exemple la température d'air moyenne de l'espace). À chaque pas de temps,
``self.interface_input`` recevra un dictionnaire ``Dict[str, float]`` avec la
valeur ``float`` pour chaque ``Space`` (dont le ``id`` est utilisée, d'où le
``str``). Cependant, pour initialiser le cas, dans le jeu de données d'entrée,
chaque espace devra avoir cette variable. Le format ainsi que la description de
cette variable pour l'objet espace dans le jeu de données d'entrée peuvent être
spécifiés dans l'objet ``Attachment``:

.. code-block:: python

    Attachment(
        category=ColibriProjectObjects.SPACE,
        description="Description of the interface input for the object it is attached to.",
        format=float,
    )

