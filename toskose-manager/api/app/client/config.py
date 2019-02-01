import os
from client.client import ProtocolType


class Config:

    CLIENT_PROTOCOL = os.environ.get('CLIENT_PROTOCOL', default=ProtocolType.XMLRPC)
