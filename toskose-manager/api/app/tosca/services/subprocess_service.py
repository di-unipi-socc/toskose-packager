from tosca.services.base_service import BaseService

from tosca.models import SubprocessInfoDTO
from tosca.models import SubprocessOperationResultDTO

from tosca.exception_handler import OperationNotValid

from tosca.utils.utils import compute_uptime

from dataclasses import asdict


class SubProcessOperationService(BaseService):

    def __init__(self):
        super().__init__()

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

    def __build_subprocess_multi_operation_result_dto(self, res):
        return SubprocessOperationResultDTO(
            name=res['name'],
            group=res['group'],
            status_code=res['status'],
            description=res['description']
        )

    def __join_group_and_subprocess_ids(self, group_id, subprocess_id):
        return ':'.join([group_id, subprocess_id])

    @BaseService.init_client(validate_node=True, validate_connection=True)
    def get_all_subprocesses_info(self, *, node_id):
        infos = self._client.get_all_process_info()
        result = list()
        for info in infos:
            result.append(self.__build_subprocess_info_dto(info))
        return result


    @BaseService.init_client(validate_node=True, validate_connection=True)
    def manage_subprocesses(
        self, *args,
        operation, node_id, is_signal=False,
        **kwargs):

        """ single result operations """
        if operation == 'info':
            return self.__build_subprocess_info_dto(
                self._client.get_process_info(  # group:name
                    self.__join_group_and_subprocess_ids(
                        kwargs['group_id'], kwargs['subprocess_id'])
                ))
        elif operation == 'start':
            if is_signal:
                return self._client.signal_process(
                    kwargs['subprocess_id'], kwargs['signal'])

            return self._client.start_process(  # group:name
                self.__join_group_and_subprocess_ids(
                    kwargs['group_id'], kwargs['subprocess_id']),
                kwargs['wait']
            )
        elif operation == 'stop':
            return self._client.stop_process(   # group:name
                self.__join_group_and_subprocess_ids(
                    kwargs['group_id'], kwargs['subprocess_id']),
                kwargs['wait']
            )

        """ multiple results operations """
        results = None
        if operation == 'start_group':
            if is_signal:
                return NotImplementedError('not implemented yet')

            results = self._client.start_process_group(
                kwargs['group_id'], kwargs['wait']
            )
        elif operation == 'stop_group':
            results = self._client.stop_process_group(
                kwargs['group_id'],kwargs['wait']
            )
        elif operation == 'info_all':
            results = self._client.get_all_process_info()
        elif operation == 'start_all':
            if is_signal:
                return NotImplementedError('not implemented yet')

            results = self._client.start_all_processes(kwargs['wait'])
        elif operation == 'stop_all':
            results = self._client.stop_all_processes(kwargs['wait'])
        else:
            raise OperationNotValid('operation {0} not valid'.format(operation))

        final_res = list()
        for res in results:
            final_res.append(
                self.__build_subprocess_multi_operation_result_dto(res))
        return final_res

    @BaseService.init_client(validate_node=True, validate_connection=True)
    def send_subprocess_stdin(self, *, node_id, name, chars):
        return NotImplementedError('not implemented yet')


class SubProcessLoggingService(BaseService):

    def __init__(self, node_id):
        super().__init__(node_id)

    def read_subprocess_stdout_log(self, name, offset, length):
        """ not implemented yet """
        pass

    def read_subprocess_stderr_log(self, name, offset, length):
        """ not implemented yet """
        pass

    def tail_subprocess_stdout_log(self, name, offset, length):
        """ not implemented yet """
        pass

    def tail_subprocess_stderr_log(self, name, offset, length):
        """ not implemented yet """
        pass

    def clear_subprocess_log(self, name):
        """ not implemented yet """
        pass

    def clear_all_subprocess_logs(self):
        """ not implemented yet """
        pass
