#!/usr/bin/env python

from jolt import attributes as jolt_attributes
from jolt import influence, Parameter, Task
from jolt.plugins import ninja


class BoardParameter(Parameter):
    def __init__(self, default=None, values=None):
        super().__init__(
            default,
            values,
            help="Board name.")


class DistroArchParameter(Parameter):
    def __init__(self, default=None, values=None):
        super().__init__(
            default or "amd64",
            values or ["amd64", "aarch64", "armv7", "host"],
            help="Target architecture.")


class DistroNameParameter(Parameter):
    def __init__(self, default=None, values=None):
        super().__init__(
            default or "debian",
            values or ["alpine", "debian"],
            help="Base distribution name.")


class DistroVersionParameter(Parameter):
    def __init__(self, default=None, values=None):
        super().__init__(
            default,
            values,
            help="Distribution version or codename.")


@influence.files("{tree}")
class TreeTask(Task):
    abstract = True

    tree = "tree"

    def run(self, deps, tools):
        pass

    def publish(self, artifact, tools):
        with tools.cwd("{tree}"):
            artifact.collect("*", symlinks=True)


@jolt_attributes.requires("requires_sdk")
class CXXExecutable(ninja.CXXExecutable):
    abstract = True

    distro = DistroNameParameter()
    sdk = Parameter()

    @property
    def requires_sdk(self):
        return ["sdk=" + str(self.sdk)]

    def run(self, deps, tools):
        with tools.chroot(deps["sdk"]):
            super().run(deps, tools)


@jolt_attributes.requires("requires_sdk")
class CXXLibrary(ninja.CXXLibrary):
    abstract = True

    distro = DistroNameParameter()
    sdk = Parameter()

    @property
    def requires_sdk(self):
        return ["sdk=" + str(self.sdk)]

    def run(self, deps, tools):
        with tools.chroot(deps["sdk"]):
            super().run(deps, tools)
