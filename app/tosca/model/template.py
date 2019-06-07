'''
Template module
'''
import six
import os

from .nodes import Container, Root, Software, Volume


class Template:

    def __init__(self, name):
        self._nodes = {}
        self.name = name
        self.description = 'No description.'
        self._outputs = []
        self.tmp_dir = None
        self.manifest_path = None
        self.imports = []
        self.toskose_config_path = None

    def add_import(self, name, path):
        if not os.path.exists(path):
            raise ValueError('The file {} doesn\'t exists'.format(path))
        entry = dict()
        entry[name] = path
        self.imports.append(entry)

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
