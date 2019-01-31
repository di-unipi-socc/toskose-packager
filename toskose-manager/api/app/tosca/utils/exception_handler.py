def client_handling_failures(func):
    """ decorator for handling client failures """

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except SupervisordClientOperationError as ex:
            print('todo')

    return wrapper
