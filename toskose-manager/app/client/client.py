from enum import Enum, auto
from app.client.impl.xmlrpc_client import ToskoseXMLRPCclient


class ProtocolType(Enum):
    XMLRPC = auto()

class ToskoseClientFactory:

    @staticmethod
    def create(*, type, **kwargs):
        type = type.upper()
        if type == ProtocolType.XMLRPC.name:
            return ToskoseXMLRPCclient(**kwargs)
        else:
            raise ValueError("Invalid client protocol: {p}".format(p=type))
