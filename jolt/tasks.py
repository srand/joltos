#!/usr/bin/env python

from jolt import influence, Parameter, Task


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
