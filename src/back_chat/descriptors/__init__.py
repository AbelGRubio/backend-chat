"""This package contains custom Python descriptors.

Used to control attribute access and behavior within models or services.
"""

from .message import MessageMode, MessageType

__all__ = [MessageType.__name__, MessageMode.__name__]
