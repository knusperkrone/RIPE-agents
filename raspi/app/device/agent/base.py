from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, name: str, type: str, failsafe):
        self.name = name
        self.type = type
        self.failsaife_state = failsafe

    @abstractmethod
    def set_state(self, _cmd: int):
        raise NotImplementedError('set_state not implemented')

    @abstractmethod
    def failsaife(self):
        raise NotImplementedError('set_state not implemented')
