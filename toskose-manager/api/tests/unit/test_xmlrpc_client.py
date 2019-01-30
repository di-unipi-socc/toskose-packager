import unittest
from app.client.impl.xmlrpc_client import ToskoseXMLRPCclient


class TestXMLRPCclient(unittest.TestCase):

    def setUp(self):
        self.client = ToskoseXMLRPCclient(
            host='localhost',
            port='9001',
            username='admin',
            password='admin'
        )
        self.log_offset = 0
        self.log_length = 0

    def test_api_version(self):
        print(self.client.get_api_version())

    def test_supervisor_version(self):
        print(self.client.get_supervisor_version())

    def test_identification(self):
        print(self.client.get_identification())

    def test_state(self):
        print(self.client.get_state())

    def test_pid(self):
        print(self.client.get_pid())

    def test_read_log(self):
        print(self.client.read_log(self.log_offset, self.log_length))

    def test_clear_log(self):
        res = self.client.clear_log()
        if res:
            print('log cleared')
        else:
            print('failed')

    def test_shutdown(self):
        down = self.client.shutdown()
        if down:
            print('supervisor shutted down')
        else:
            print('failed')

    def test_restart(self):
        re = self.client.restart()
        if re:
            print('supervisor restarted')
        else:
            print('failed')




if __name__ == '__main__':
    unittest.main()
