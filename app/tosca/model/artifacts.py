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

    def __init__(self, attr=None):
        super(DockerImage, self).__init__('')
        if attr is None:
            self.name = None
            self.tag = None
        else:
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

    def __init__ (self, name, tag=None, registry_password=None,
                  base_name=None, base_tag=None):
        self.name = name
        self.registry_password = registry_password
        self.tag = str(tag) if tag is not None else 'latest'

        # base toskose image
        # used by toskose for the "toskosing" process
        self.base_name = base_name        
        self.base_tag = base_tag

    @staticmethod
    def _build_image_name(name, tag):
        return '{0}:{1}'.format(name, tag) 

    @property
    def full_name(self):
        """ Return the Docker Image name including the tag (if any). """

        return ToskosedImage._build_image_name(self.name, self.tag)

    @property
    def full_name_base(self):
        """ Return the Docker base Image name including the tag (if any). """

        return ToskosedImage._build_image_name(self.base_name, self.base_tag) 