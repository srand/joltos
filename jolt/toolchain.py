#!/usr/bin/env python3

from jolt import attributes, Task
from jolt.tasks import Alias, Parameter
from jolt.plugins import docker
from jolt.plugins import git

import functools


class Tools(docker.DockerImage):
    dockerfile = """
    FROM debian:latest
    ARG DEBIAN_FRONTEND=noninteractive
    ENTRYPOINT ["sh"]
    RUN apt-get update
    RUN apt-get install -y automake bc bison dosfstools flex libpython3-dev libssl-dev libtool lzop make mtools pkg-config python3 python3-distutils python3-pkg-resources swig
    RUN apt-get install -y build-essential
    RUN apt-get install -y crossbuild-essential-armhf
    RUN apt-get install -y crossbuild-essential-arm64
    RUN apt-get install -y libconfuse-dev # genimage
    """
    context = "packages/tools"
    extract = True
    imagefile = None


@attributes.method("publish", "publish_{arch}")
class SDK(Task):
    arch = Parameter(values=["armv7", "aarch64", "host"])

    requires = ["tools"]

    def publish_aarch64(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "aarch64-linux-gnu-"

    def publish_armv7(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "arm-linux-gnueabihf-"

    def publish_host(self, artifact, tools):
        pass


def docker_wrap(container):
    def decorate(f):
        @functools.wraps(f)
        def run(self, deps, tools):
            try:
                f(self, deps, tools)
            finally:
                pass
        return run
    return decorate


class _Default(Alias):
    requires = ["kernel"]


