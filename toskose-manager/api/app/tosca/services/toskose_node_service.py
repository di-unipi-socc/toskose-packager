from app.client.client import ToskoseClientFactory
from app.client.exceptions import SupervisordClientOperationError
from app.tosca.models import ToskoseNodeInfoDTO, ToskoseNodeLogDTO

from dataclasses import asdict


# TODO
# will be changed with a "map" generated from an external yml
# we need id associated to a toskose-unit node
from app.tosca.models import ToskoseNode
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
        self.id = id
        self.client = ToskoseClientFactory.create(
            type='XMLRPC',  # TODO dynamic with configuration
            host=node.host,
            port=node.port,
            username=node.username,
            password=node.password
        )

    @_handling_failures
    def get_node_info(self):
        return asdict(ToskoseNodeInfoDTO(
            id=self.id,
            host=self.client.host,
            port=self.client.port,
            api_protocol='XMLRPC',
            api_version=self.client.get_api_version(),
            supervisor_version=self.client.get_supervisor_version(),
            supervisor_id=self.client.get_identification(),
            supervisor_state=(lambda x : {
                'name': x['statename'],
                'code': x['statecode']
            })(self.client.get_state()),
            supervisor_pid=self.client.get_pid()
        ))

    @_handling_failures
    def get_node_log(self, offset=0, length=0):
        return asdict(ToskoseNodeLogDTO(
            log=self.client.read_log(offset, length)
        ))

    @_handling_failures
    def clear_log(self):
        return self.client.clear_log()

    @_handling_failures
    def shutdown(self):
        return self.client.shutdown()

    @_handling_failures
    def restart(self):
        return self.client.restart()
