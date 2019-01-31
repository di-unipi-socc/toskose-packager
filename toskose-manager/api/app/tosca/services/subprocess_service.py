from app.client.client import ToskoseClientFactory
from app.client.exceptions import SupervisordClientOperationError
from app.tosca.models import SubprocessInfoDTO
from app.tosca.services.base_service import BaseService
from app.tosca.utils.utils import compute_uptime

from app.tosca.utils.exception_handler import client_handling_failures

from dataclasses import asdict


class SubProcessService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    @client_handling_failures
    def get_process_info(self, name):
        return None # TODO

    @client_handling_failures
    def get_all_process_info(self):
        infos = self.client.get_all_process_info()
        result = list()

        for info in infos:
            dto = SubprocessInfoDTO(
                name=info['name'],
                group=info['group'],
                description=info['description'],
                time_start=str(info['start']),
                time_end=str(info['stop']),
                uptime=compute_uptime(info['start'], info['stop']),
                state_code=str(info['state']),
                state_name=info['statename'],
                logfile_path=info['logfile'],
                stdout_logfile_path=info['stdout_logfile'],
                stderr_logfile_path=info['stderr_logfile'],
                spawn_error=info['spawnerr'],
                exit_status=str(info['exitstatus']),
                pid=str(info['pid'])
            )
            result.append(dto)
        return result
