'''
Artifacts module
'''

class Artifact(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Artifact'

#
# def _get_str_name(obj):
#     return obj if isinstance(obj, six.string_types) else obj.name


class File(Artifact):

    def __init__(self, name, abs_path):
        super(File, self).__init__(name)
        split_path = abs_path.split('/')
        self.path = '/'.join(split_path[:-1])
        self.file = split_path[-1]

    @property
    def file_path(self):
        return self.path + '/' + self.file

    @property
    def format(self):
        pass

    def __str__(self):
        return 'File'


class DockerImage(Artifact):

    def __init__(self, attr):
        super(DockerImage, self).__init__('')
        self.name, self.tag = attr.split(':') if ':' in attr \
            else (attr, 'latest')

    @property
    def format(self):
        return '{}:{}'.format(self.name, self.tag)

    def __str__(self):
        return 'DockerImage'


class DockerImageExecutable(DockerImage):

    def __str__(self):
        return 'DockerImageExecutable'


class Dockerfile(Artifact):

    def __init__(self, attr, dockerfile):
        super(Dockerfile, self).__init__('')
        self.name, self.tag = attr.split(':') if ':' in attr \
            else (attr, 'latest')
        self.dockerfile = dockerfile

    @property
    def format(self):
        return '{}:{}'.format(self.name, self.tag)

    def __str__(self):
        return 'Dockerfile'


class DockerfileExecutable(Dockerfile):

    def __str__(self):
        return 'DockerfileExecutable'


class ToskosedImage(DockerImage):
    """ Represent a "toskosed" image.
    
    [repository/]user/image_name[:tag]
    """

    def __init__ (self, name, user, password, **kwargs):
        self.name = name
        self.user = user
        self.password = password
        
        self.repository = kwargs.get('repository')
        self.tag = kwargs.get('tag')
        if self.tag is not None:
            self.tag = str(kwargs['tag'])

    @property
    def full_name(self):
        """ Return the Docker Image name including the tag (if any). """
        repository = '' if self.repository is None else '{}/'.format(self.repository)
        tag = '' if self.tag is None else ':{}'.format(self.tag)

        return '{0}{1}/{2}{3}'.format(repository, self.user, self.name, tag) 