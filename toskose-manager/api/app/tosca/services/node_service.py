from tosca.services.base_service import BaseService

from tosca.models import ToskoseNodeInfoDTO
from tosca.models import ToskoseNodeLogDTO
from core.toskose_manager import ToskoseManager

from client.exceptions import SupervisordClientConnectionError

from config import AppConfig

from dataclasses import asdict
from typing import List, Dict


class NodeService(BaseService):

    def __init__(self):
        super().__init__()

    def __build_node_info_dto(self, *, node_id, node_data, client=None):
        """ builds the NodeInfoDTO

        If the node is not reacheable (client=None) the data fetched from the
        node API are omitted (using default value in the associated dataclass).
        """

        mandatory = {
            'reacheable': bool(client),
            'id': node_id,
            'name': node_data['name'],
            'description': node_data['description'],
            'hostname': node_data['hostname'],
            'port': node_data['port'],
            'username': node_data['username'],
            'password': node_data['password'],
            'api_protocol': AppConfig._CLIENT_PROTOCOL
        }

        optional = dict()
        if client:
            optional = {
                'api_version': client.get_api_version(),
                'supervisor_version': client.get_supervisor_version(),
                'supervisor_id': client.get_identification(),
                'supervisor_state':  \
                    (lambda x : {
                        'name': x['statename'],
                        'code': x['statecode']
                    })(client.get_state()),
                'supervisor_pid': client.get_pid()
            }

        return asdict(ToskoseNodeInfoDTO(**mandatory, **optional))

    def get_all_nodes_info(self) -> List:
        """ Retrieve info about the nodes, mixing info from the the application
        configuration and info fetched from the Node API through the client.
        """

        """ retrieve node data from the app configuration """
        nodes = ToskoseManager.get_instance().nodes

        results = list()
        for node_id, node_data in nodes.items():

            is_reacheable = True
            try:
                client = ToskoseManager.get_instance().get_node_client_instance(node_id)
                client.get_identification()
            except SupervisordClientConnectionError as conn_err:
                is_reacheable = False

            results.append(
                self.__build_node_info_dto(
                    node_id=node_id,
                    node_data=node_data,
                    client=client if is_reacheable else None))

        return results

    @BaseService.init_client(validate_node=True)
    def get_node_info(self, *, node_id):

        """ retrieve node data from app configuration """
        node_id, node_data = ToskoseManager.get_instance().get_node_data(
            node_id=node_id)

        return self.__build_node_info_dto(
            node_id=node_id,
            node_data=node_data,
            client=self._client if self._is_reacheable else None)


    @BaseService.init_client(validate_node = True, validate_connection=True)
    def get_node_log(self, *, node_id, offset=0, length=0):

        return asdict(ToskoseNodeLogDTO(
            log=self._client.read_log(offset, length)
        ))

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def clear_log(self, *, node_id):
        return self._client.clear_log()

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def shutdown(self, *, node_id):
        return self._client.shutdown()

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def restart(self, *, node_id):
        return self._client.restart()

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def send_remote_comm_event(self, *, node_id, type, data):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def reload_config(self, *, node_id):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def add_process_group(self, *, node_id, name):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def remove_process_group(self, *, node_id, name):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def list_methods(self, *, node_id):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def method_help(self, *, node_id, name):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def method_signature(self, *, node_id, name):
        """ not implemented yet """
        pass

    @BaseService.init_client(validate_node = True, validate_connection=True)
    def multicall(self, *, node_id, calls):
        """ not implemented yet """
        pass
