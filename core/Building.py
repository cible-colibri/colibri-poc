import abc

from core.model import Model


class Building(Model):
    @abc.abstractmethod
    def create_systems(self):
        raise NotImplementedError