#!/usr/bin/env python

from jolt import influence, Task


@influence.files("{tree}")
class TreeTask(Task):
    abstract = True

    tree = "tree"

    def run(self, deps, tools):
        pass

    def publish(self, artifact, tools):
        with tools.cwd("{tree}"):
            artifact.collect("*", symlinks=True)
