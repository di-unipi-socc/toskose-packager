'''
Template module
'''
import six

from .nodes import Container, Root, Software, Volume


class Template:

    def __init__(self, name):
        self._nodes = {}
        self._name = name
        self._description = 'No description.'
        self._outputs = []
        self.tmp_dir = None

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if description or description != '':
            self._description = description

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        if outputs:
            self._outputs = outputs

    @property
    def nodes(self):
        return (v for k, v in self._nodes.items())

    @property
    def containers(self):
        """ The container nodes associated with the template.

        Returns a generator expression.
        """
        return (v for k, v in self._nodes.items() if isinstance(v, Container))

    @property
    def volumes(self):
        """ The volume nodes associated with the template.

        Returns a generator expression.
        """
        return (v for k, v in self._nodes.items() if isinstance(v, Volume))

    @property
    def software(self):
        """ The software nodes associated with the template.

        Returns a generator expression.
        """
        return (v for k, v in self._nodes.items() if isinstance(v, Software))

    def push(self, node):
        self._nodes[node.name] = node

    def __getitem__(self, name):
        return self._nodes.get(name, None)

    def __contains__(self, item):
        if isinstance(item, six.string_types):
            return self[item] is not None
        if isinstance(item, Root):
            return self[item.name] is not None
        return False

    def __str__(self):
        return ', '.join((i.name for i in self.nodes))
