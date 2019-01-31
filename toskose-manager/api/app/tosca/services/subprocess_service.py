from app.tosca.services.base_service import BaseService

from app.tosca.models import SubprocessInfoDTO
from app.tosca.models import SubprocessOperationResultDTO
from app.tosca.models import SubprocessSingleOperationResultDTO

from app.tosca.utils.utils import compute_uptime
from app.tosca.exception_handler import client_handling_failures

from dataclasses import asdict


class SubProcessOperationService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    def __build_subprocess_info_dto(self, res):
        return SubprocessInfoDTO(
            name=res['name'],
            group=res['group'],
            description=res['description'],
            time_start=str(res['start']),
            time_end=str(res['stop']),
            uptime=compute_uptime(res['start'], res['stop']),
            state_code=str(res['state']),
            state_name=res['statename'],
            logfile_path=res['logfile'],
            stdout_logfile_path=res['stdout_logfile'],
            stderr_logfile_path=res['stderr_logfile'],
            spawn_error=res['spawnerr'],
            exit_status=str(res['exitstatus']),
            pid=str(res['pid'])
        )

    def __build_subprocess_multi_operation_result_dto(res):
        return SubprocessOperationResultDTO(
            name=res['name'],
            group=res['group'],
            status_code=res['status'],
            description=res['description']
        )

    def __build_subprocess_single_operation_result_dto(res):
        return SubprocessSingleOperationResultDTO(
            message=res['message']
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
        return self.__build_subprocess_single_operation_result_dto(
            {'message': 'OK'})

    @client_handling_failures
    def start_all_subprocesses(self, wait=True):
        results = self.client.start_all_subprocesses(wait)
        final_res = list()
        for res in results:
            final_res.append(self.__build_subprocess_multi_operation_result_dto(res))

    @client_handling_failures
    def start_subprocess_group(self, name, wait=True):
        return { 'message': 'not implemented yet'}

    @client_handling_failures
    def stop_subprocess(self, name, wait=True):
        res = self.client.stop_process(name,wait)
        return self.__build_subprocess_single_operation_result_dto(
            {'message': 'OK'})

    @client_handling_failures
    def stop_subprocess_group(self, name, wait=True):
        return { 'message': 'not implemented yet'}

    @client_handling_failures
    def stop_all_subprocesses(self, wait=True):
        results = self.client.stop_all_processes(wait)
        final_res = list()
        for res in results:
            final_res.append(self.__build_subprocess_multi_operation_result_dto(res))

    @client_handling_failures
    def signal_subprocess(self, name, signal):
        return { 'message': 'not implemented yet'}

    @client_handling_failures
    def signal_subprocess_group(self, name, signal):
        return { 'message': 'not implemented yet'}

    @client_handling_failures
    def signal_all_subprocesses(self, signal):
        return { 'message': 'not implemented yet'}

    @client_handling_failures
    def send_subprocess_stdin(self, name, chars):
        return { 'message': 'not implemented yet'}


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
