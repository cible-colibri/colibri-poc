import abc

from colibri.core.models.model import Model


class Building(Model):
    @abc.abstractmethod
    def create_systems(self):
        ...
