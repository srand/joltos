#!/usr/bin/env python3

from jolt import attributes, Task
from jolt.tasks import Alias, Parameter
from jolt.plugins import docker
from jolt.plugins import git

import functools

from joltos.jolt.tasks import DistroArchParameter
from joltos.jolt.tasks import DistroNameParameter
from joltos.jolt.tasks import DistroVersionParameter


class Tools(docker.DockerImage):
    distro = DistroNameParameter()
    version = DistroVersionParameter()
    dockerfile = "docker/Dockerfile.{distro}.tools"
    context = "docker"
    extract = True
    imagefile = None

    def run(self, deps, tools):
        dockerfile = tools.render(self.dockerfile)
        with tools.cwd(tools.builddir()):
            self.dockerfile = tools.expand_path("Dockerfile")
            tools.write_file(self.dockerfile, dockerfile)
        super().run(deps, tools)


@attributes.method("publish", "publish_{distro}_{arch}")
class SDK(Task):
    arch = DistroArchParameter()
    distro = DistroNameParameter()
    version = DistroVersionParameter()

    requires = ["tools:distro={distro},version={version}"]

    def publish_debian_aarch64(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "aarch64-linux-gnu-"

    def publish_debian_armv7(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "arm-linux-gnueabihf-"

    def publish_debian_host(self, artifact, tools):
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


