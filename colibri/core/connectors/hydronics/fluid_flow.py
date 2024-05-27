"""
This file contains the FluidFlowConnector class (inherited from the
Connector class).
"""

from typing import List, Self

from colibri.core.connectors.connector import Connector


class FluidFlowConnector(Connector):
    def __init__(self) -> None:
        self.connections: List[tuple] = [
            # (from_variable, to_variable)
            ("outlet_temperature", "inlet_temperature"),
            ("outlet_flow_rate", "inlet_flow_rate"),
        ]

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
        None

        Raises
        ------
        NotImplementedError
            FluidFlowConnector instances must not add connections

        Examples
        --------
        >>> None
        """
        raise NotImplementedError(
            f"FluidFlowConnector instances must not add connections. "
            f"The connection ({from_variable_name}, {to_variable_name}) "
            f"cannot be added. Connections available: {self.connections}"
        )


if __name__ == "__main__":
    fluid_flow_connector: FluidFlowConnector = FluidFlowConnector()
    print(fluid_flow_connector.__str__())
    print(fluid_flow_connector.__repr__())
    print(fluid_flow_connector)
    fluid_flow_connector = FluidFlowConnector()
    try:
        fluid_flow_connector.add("outlet_temperature", "inlet_temperature")
        fluid_flow_connector.add("outlet_flow_rate", "inlet_flow_rate")
    except NotImplementedError as error:
        print(error)
