import os
import tempfile
import zipfile
import shutil

from app.common.logging import LoggingFacility
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaFatalError
from app.common.exception import ToscaParsingError
from app.common.exception import DockerOperationError
from app.common.commons import CommonErrorMessages
from app.common.commons import unpack_archive
from app.validator import validate_csar
from app.tosca.modeler import ToscaModeler
from app.docker.manager import DockerImageToskoser
from app.docker.compose import DockerComposeGenerator
from app.supervisord.config.configurator import SupervisordConfigGenerator
from app.supervisord.config.configurator import SupervisordTemplateType


logger = LoggingFacility.get_instance().get_logger()


class Toskoserizator:

    def __init__(self, 
        csar_path=None, 
        output_path=None,
        docker_url=None,
        debug=False, 
        quiet=False):

        self._docker_url = docker_url
        self._csar_path = csar_path
        self._output_path = output_path

        Toskoserizator.setup_logging(debug=debug, quiet=quiet)

    @property
    def docker_url(self):
        return self._docker_url

    @docker_url.setter
    def docker_url(self, docker_url):
        self._docker_url = docker_url

    @property
    def csar_path(self):
        return self._csar_path

    @csar_path.setter
    def csar_path(self, path):
        self._csar_path = path

    @property
    def output_path(self):
        return self._output_path

    @output_path.setter
    def output_path(self, path):
        self._output_path = path
    
    @staticmethod
    def setup_logging(debug, quiet):
        
        if quiet:
            LoggingFacility.get_instance().quiet()

        if debug: # override quiet
            LoggingFacility.get_instance().debug()

    @staticmethod
    def build_output_dir(output_path):
        """ """

        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        except OSError as err:
            logger.error('Failed to create {0} directory'.format(output_path))
            logger.exception(err)
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
        else:
            logger.info('Output dir {0} built'.format(output_path))

    @staticmethod
    def build_app_context(csar_path, output_path, tosca_model):
        """ 
        
        """

        try:

            root_dir = os.path.join(output_path, tosca_model.name)
            if os.path.exists(root_dir):
                shutil.rmtree(root_dir, ignore_errors=True)
            
            os.makedirs(root_dir)
            for container in tosca_model.containers:
                
                # name and lifecycle ops for each component within the same container
                # (need for generating the supervisord.conf)
                components_data = []
                
                node_dir = os.path.join(root_dir, container.name)
                os.makedirs(node_dir)
                for component in container.components:
                    component_dir = os.path.join(node_dir, component.name)

                    component_data = {
                        'name': component.name,
                        'interfaces': {},
                        'artifacts': {},
                    }
                    
                    #copy artifacts
                    os.makedirs(os.path.join(component_dir, 'artifacts'))
                    for artifact in component.artifacts:
                        artifact_filename = os.path.basename(artifact.path)
                        shutil.copy2(
                            os.path.join(csar_path, artifact.path), 
                            os.path.join(component_dir, 'artifacts', artifact_filename)
                        )
                        
                        # update artifacts data (supervisord.conf)
                        component_data['artifacts'][artifact.name] = \
                            os.path.join(
                                '/toskose/apps',
                                component.name,
                                'artifacts',
                                artifact_filename
                            )

                    # copy scripts   
                    os.makedirs(os.path.join(component_dir, 'scripts'))                 
                    for interface in component.interfaces:
                        implementation_filename = os.path.basename(interface.implementation)
                        shutil.copy2(
                            os.path.join(csar_path, interface.implementation),
                            os.path.join(component_dir, 'scripts', implementation_filename)
                        )
                        
                        # update interfaces/lifecycle ops (supervisord.conf)
                        component_data['interfaces'][interface.name] = \
                            os.path.join(
                                '/toskose/apps', 
                                component.name, 
                                'scripts', 
                                implementation_filename
                            )

                    components_data.append(component_data)

                    # initialize logs
                    logs_path = os.path.join(component_dir, 'logs')
                    log_name ='{0}.log'.format(component.name)
                    os.makedirs(logs_path)
                    open(os.path.join(logs_path, log_name), 'w').close()

                # generate supervisord conf
                args = {'components_data': components_data}
                SupervisordConfigGenerator(node_dir) \
                    .build(SupervisordTemplateType.Unit, **args)

        except OSError as err:
            raise
        except Exception as err:
            raise

    def toskosed(self):
        """ """

        # check_requirements() ? script for checking:
        # - docker is installed
        # - docker-compose is installed
        # other?

        # Output dir
        if self._output_path is None:
            output_path = os.path.join(os.getcwd(), 'toskose_out')
            Toskoserizator.build_output_dir(output_path)
            self._output_path = output_path

        # Docker Client
        dm = DockerImageToskoser(base_url=self._docker_url)

        # CSAR Validation
        #TODO validate_csar() !!!need fix!!!
        csar_metadata = validate_csar(self._csar_path)

        # temporary dir for unpacking data from .CSAR archive
        # temporary dir for building docker images
        with tempfile.TemporaryDirectory() as tmp_dir_docker:
            with tempfile.TemporaryDirectory() as tmp_dir_csar:
                try:
                    # Unpack archive
                    unpack_archive(self._csar_path, tmp_dir_csar)
                    manifest_path = os.path.join(tmp_dir_csar, csar_metadata['manifest_filename'])
                    
                    # Build Model
                    tm = ToscaModeler(manifest_path)
                    tm.build()
                    app_name = tm.model.name

                    # Build app context and generate Supervisord's configurations
                    Toskoserizator.build_app_context(tmp_dir_csar, tmp_dir_docker, tm.model)

                    # "toskosing" the docker images specified in the .CSAR
                    dit = DockerImageToskoser()
                    
                    for container in tm.model.containers:
                        
                        context_path = os.path.join(
                            tmp_dir_docker,
                            app_name,
                            container.name
                        )

                        dst_image = '{0}-{1}-toskosed'.format(
                            app_name,
                            container.name
                        )
                        
                        #repository = container.image_repository
                        #ports = container.ports

                        dit.toskose_image(
                            src_image=container.image,
                            dst_image=dst_image,
                            context_path=context_path
                        )

                    # Generating the compose file                  
                    dcg = DockerComposeGenerator()
                    dcg.generate(
                        tosca_model=tm.model,
                        output_path=self._output_path
                    )
                
                except Exception as err:
                    if not isinstance(err, ToscaParsingError):
                        logger.exception(err)
                    raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
                finally:
                    dm.close()
