"""This file contains the Connector class."""

from typing import Self


class Connector:
    __slots__ = ("connections",)

    def __init__(self) -> None:
        self.connections: list = []

    def add(self, from_variable_name: str, to_variable_name: str) -> Self:
        """Add connection to the Connector instance

        Parameters
        ----------
        from_variable_name : str
           Name of the variable from which the connection starts
        to_variable_name : str
            Name of the variable from which the connection ends

        Returns
        -------
        Self
            Return the Connector instance

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        self.connections.append((from_variable_name, to_variable_name))
        return self

    def __str__(self) -> str:
        """Return the string representation of the object

        Returns
        -------
        string_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        join_adds: str = "".join(
            [
                f".add({formatted_connection})"
                for formatted_connection in [
                    ", ".join(f'"{element}"' for element in condition)
                    for condition in getattr(self, "connections")
                ]
            ]
        )
        string_representation: str = f"{self.__class__.__name__}(){join_adds}"
        return string_representation

    def __repr__(self) -> str:
        """Return the object representation as a string

        Parameters
        ----------

        Returns
        -------
        object_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        object_representation: str = self.__str__()
        return object_representation


if __name__ == "__main__":
    variable_connector: Connector = Connector()
    print(variable_connector.__str__())
    print(variable_connector.__repr__())
    print(variable_connector)
    variable_connector = Connector()
    variable_connector.add("outlet_temperature", "inlet_temperature")
    variable_connector.add("outlet_flow_rate", "inlet_flow_rate")
    print(variable_connector.__str__())
    print(variable_connector.__repr__())
    print(variable_connector)
