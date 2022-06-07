#!/usr/bin/env python3

from jolt import Task

from .image import attributes
from .image import BareAlpineRootfs, BareDebianRootfs
from .tasks import DistroArchParameter


@attributes.install_pkgs("install_pkgs_default")
class DebianSdk(BareDebianRootfs):
    abstract = True
    arch = DistroArchParameter()
    board = None
    extract = True

    install_pkgs_default = [
        "build-essential",
        "crossbuild-essential-armhf",
        "ninja-build",
    ]

    def publish(self, artifact, tools):
        super().publish(artifact, tools)
        getattr(self, tools.expand("publish_{arch}"))(artifact, tools)

    def publish_aarch64(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "aarch64-linux-gnu-"

    def publish_armv7(self, artifact, tools):
        artifact.environ.CROSS_COMPILE = "arm-linux-gnueabihf-"
        artifact.environ.AS = "arm-linux-gnueabihf-as"
        artifact.environ.CC = "arm-linux-gnueabihf-gcc"
        artifact.environ.CXX = "arm-linux-gnueabihf-g++"
        artifact.environ.LD = "arm-linux-gnueabihf-g++"
        artifact.environ.OBJCOPY = "arm-linux-gnueabihf-objcopy"
        artifact.environ.OBJDUMP = "arm-linux-gnueabihf-objdump"

    def publish_amd64(self, artifact, tools):
        pass

    def publish_host(self, artifact, tools):
        pass


@attributes.install_pkgs("install_pkgs_default")
class AlpineSdk(BareAlpineRootfs):
    abstract = True
    board = None
    extract = True

    install_pkgs_default = [
        "squashfs-tools",
    ]