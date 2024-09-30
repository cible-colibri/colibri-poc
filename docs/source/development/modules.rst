
Module
------

Un module est nécessairement défini par rapport à une interface, dont il hérite
les entrées et sorties (variable de simulation) pour être interchangeable avec
un autre module issu de la même interface.

Un module (par exemple ``ModuleExample``) doit donc importer une interface
pour qu'il puisse en hériter :

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
                input_or_output_interface=input_or_output_for_interface,
            )
            self.parameter_for_module = parameter_for_module

Un paramètre du module peut être créé directement comme dans l'exemple
ci-dessus ; dans ce cas, ce paramètre ne sera jamais renseigné dans le jeu de
données d'entrée et ne contiendra aucune information.

Comme pour les entrées et sorties (voir
:ref:`fonctions_define_input_output_section`), il est possible de définir un
paramètre grâce à la fonction ``define_parameter`` issue de la class ``Module``
(qui est amenée par l'interface) :

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
                input_or_output_interface=input_or_output_for_interface,
            )
            self.parameter_for_module = self.define_parameter(
                name="parameter_for_module",
                default_value=parameter_for_module,
                description="Description of the parameter module.",
                format=bool,
                min=None,
                max=None,
                unit=Units.UNITLESS,
                attached_to=None,
                required=None,
            )

.. NOTE::

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



