from app.tosca.services.base_service import BaseService
from app.client.client import ToskoseClientFactory

from app.tosca.models import SubprocessInfoDTO
from app.tosca.models import SubprocessOperationResultDTO

from app.tosca.utils.utils import compute_uptime
from app.tosca.utils.exception_handler import client_handling_failures

from dataclasses import asdict


class SubProcessOperationService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    def __build_subprocess_info_dto(res):
        return SubprocessInfoDTO(
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

    def __build_subprocess_operation_result_dto(res):
        return SubprocessOperationResultDTO(
            name=res['name'],
            group=res['group'],
            status_code=res['status'],
            description=res['description']
        )

    @client_handling_failures
    def get_subprocess_info(self, name):
        return self.__build_subprocess_info_dto(
            self.client.get_process_info(name))

    @client_handling_failures
    def get_all_subprocesses_info(self):
        infos = self.client.get_all_process_info()
        result = list()
        for info in infos:
            result.append(self.__build_subprocess_info_dto(info))
        return result

    @client_handling_failures
    def start_subprocess(self, name, wait=True):
        res = self.client.start_process(name,wait)
        return 'OK' if res else 'Failed'

    @client_handling_failures
    def start_all_subprocesses(self, wait=True):
        results = self.client.start_all_subprocesses(wait)
        final_res = list()
        for res in results:
            final_res.append(self.__build_subprocess_operation_result_dto(res))

    @client_handling_failures
    def start_subprocess_group(self, name, wait=True):
        """ not implemented yet """
        pass

    @client_handling_failures
    def stop_subprocess(self, name, wait=True):
        res = self.client.stop_process(name,wait)
        return 'OK' if res else 'Failed'

    @client_handling_failures
    def stop_subprocess_group(self, name, wait=True):
        """ not implemented yet """
        pass

    @client_handling_failures
    def stop_all_subprocesses(self, wait=True):
        results = self.client.stop_all_processes(wait)
        final_res = list()
        for res in results:
            final_res.append(self.__build_subprocess_operation_result_dto(res))

    @client_handling_failures
    def signal_subprocess(self, name, signal):
        """ not implemented yet """
        pass

    @client_handling_failures
    def signal_process_group(self, name, signal):
        """ not implemented yet """
        pass

    @client_handling_failures
    def signal_all_subprocesses(self, signal):
        """ not implemented yet """
        pass

    @client_handling_failures
    def send_subprocess_stdin(self, name, chars):
        """ not implemented yet """
        pass


class SubProcessLoggingService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    @client_handling_failures
    def read_subprocess_stdout_log(self, name, offset, length):
        """ not implemented yet """
        pass

    @client_handling_failures
    def read_subprocess_stderr_log(self, name, offset, length):
        """ not implemented yet """
        pass

    @client_handling_failures
    def tail_subprocess_stdout_log(self, name, offset, length):
        """ not implemented yet """
        pass

    @client_handling_failures
    def tail_subprocess_stderr_log(self, name, offset, length):
        """ not implemented yet """
        pass

    @client_handling_failures
    def clear_subprocess_log(self, name):
        """ not implemented yet """
        pass

    @client_handling_failures
    def clear_all_subprocess_logs(self):
        """ not implemented yet """
        pass
