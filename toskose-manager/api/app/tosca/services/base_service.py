from app.client.client import ToskoseClientFactory
from app.tosca.models import ToskoseNode


# TODO
# will be changed with a "map" generated from an external yml
# we need id associated to a toskose-unit node

nodes = {
    '1': ToskoseNode('1','localhost','9001','admin','admin')
}
nodes_id = { id: '1' }

# TODO will be moved in the module for handling client
def get_client_instance(id):
    """ return the client instance """
    node = nodes[id]
    return ToskoseClientFactory.create(
        type='XMLRPC',  # TODO dynamic with configuration
        host=node.host,
        port=node.port,
        username=node.username,
        password=node.password
    )

class BaseService():

    def __init__(self, node_id):
        self._node_id = node_id
        self.client = get_client_instance(node_id)
