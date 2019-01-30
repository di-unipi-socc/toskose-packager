from ...client.client import ToskoseClientFactory
from ...client.exceptions import SupervisordClientOperationError


# TODO
# will be changed with a "map" generated from an external yml
# we need id associated to a toskose-unit node
from ..models import ToskoseNode
nodes = {
    '1': ToskoseNode('1','localhost','9001','admin','admin')
}
nodes_id = { id: '1' }

class ToskoseNodeService(object):

    def _handling_failures(func):
        """"""

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except SupervisordClientOperationError as ex:
                print('todo')

        return wrapper


    def __init__(self, id):

        node = nodes[id]
        self.client = ToskoseClientFactory.create(
            type='XMLRPC',  # TODO dynamic with configuration
            host=node.host,
            port=node.port,
            username=node.username,
            password=node.password
        )


    @_handling_failures
    def get_state(self):
        state = self.client.get_state()
        return {
            'name': state['statename'],
            'code': state['statecode']
        }
