from app.tosca.services.base_service import BaseService
from app.tosca.models import ToskoseNodeInfoDTO, ToskoseNodeLogDTO

from app.tosca.utils.exception_handler import client_handling_failures

from dataclasses import asdict


class NodeService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    @client_handling_failures
    def get_node_info(self):
        return asdict(ToskoseNodeInfoDTO(
            id=self._node_id,
            host=self.client.host,
            port=self.client.port,
            api_protocol='XMLRPC',
            api_version=self.client.get_api_version(),
            supervisor_version=self.client.get_supervisor_version(),
            supervisor_id=self.client.get_identification(),
            supervisor_state= \
                (lambda x : {
                    'name': x['statename'],
                    'code': x['statecode']
                })(self.client.get_state()),
            supervisor_pid=self.client.get_pid()
        ))

    @client_handling_failures
    def get_node_log(self, offset=0, length=0):
        return asdict(ToskoseNodeLogDTO(
            log=self.client.read_log(offset, length)
        ))

    @client_handling_failures
    def clear_log(self):
        return self.client.clear_log()

    @client_handling_failures
    def shutdown(self):
        return self.client.shutdown()

    @client_handling_failures
    def restart(self):
        return self.client.restart()

    @client_handling_failures
    def send_remote_comm_event(self, type, data):
        """ not implemented yet """
        pass

    @client_handling_failures
    def reload_config(self):
        """ not implemented yet """
        pass

    @client_handling_failures
    def add_process_group(self, name):
        """ not implemented yet """
        pass

    @client_handling_failures
    def remove_process_group(self, name):
        """ not implemented yet """
        pass

    @client_handling_failures
    def list_methods(self):
        """ not implemented yet """
        pass

    @client_handling_failures
    def method_help(self, name):
        """ not implemented yet """
        pass

    @client_handling_failures
    def method_signature(self, name):
        """ not implemented yet """
        pass

    @client_handling_failures
    def multicall(self, calls):
        """ not implemented yet """
        pass
