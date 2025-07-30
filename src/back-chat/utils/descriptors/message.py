from enum import Enum


class MessageType(Enum):
    MESSAGE: str = 'message'
    CONNECT: str = 'connect'
    DISCONNECT: str = 'disconnect'
    NOTICE: str = 'notice'
    WARNING: str = 'warning'
    CONNECTION: str = 'connection'
    ALARM: str = 'alarm'
    CONFIGURATION: str = 'configuration'


class MessageMode:
    def __init__(self, name=None):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if isinstance(value, MessageType):
            value = value.value
        if value not in MessageType:
            raise ValueError(f"Invalid value: {value}. "
                             f"Must be in {MessageType.__name__}")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
