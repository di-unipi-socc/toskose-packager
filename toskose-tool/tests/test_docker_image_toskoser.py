import pytest

from app.docker.manager import DockerImageToskoser


def test_docker_image_toskoser():

    src_image = 'stephenreed/jenkins-java8-maven-git:latest'
    dst_image = 'stephenreed/jenkins-java8-maven-git-toskosed:latest'
    context_path = '/home/matteo/git/toskose/tests/thinking/node-1'

    try:
        dit = DockerImageToskoser()
        dit.toskose_image(
            src_image,
            dst_image,
            context_path
        )

    except Exception as err:
        print(err)
        assert False