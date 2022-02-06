#!/usr/bin/env python

import json


from jolt import attributes, influence, Parameter, Task, utils
from jolt.plugins.docker import DockerImage

from joltos.jolt.tasks import DistroNameParameter
from joltos.jolt.tasks import DistroVersionParameter



@attributes.attribute("platform", "platform_{board}")
@attributes.requires("install_tasks")
@influence.files("{template}")
@influence.files("{_install_files}")
@influence.files("images/{board}/{variant}.cfg")
class Image(DockerImage):
    abstract = True

    base = None
    distro = DistroNameParameter()
    version = DistroNameParameter()
    variant = Parameter("default", values=["default"], help="Image variant")

    ############################################################################

    template = "docker/Dockerfile.{distro}"

    commands = []
    install_pkgs = []
    install_tasks = []
    install_files = []
    remove_files = []
    remove_pkgs = []
    platform = None
    rootpass = "joltos"

    ############################################################################

    platform_qemu = "linux/amd64"
    platform_qemu_arm = "linux/arm/v7"

    ############################################################################

    context = "images"
    extract = True
    imagefile = None
    pull = True

    def run(self, deps, tools):
        content = tools.render(self.template, deps=deps)
        with tools.cwd(tools.builddir("dockerfile")):
            self.dockerfile = tools.expand_path("Dockerfile")
            tools.write_file(self.dockerfile, content, expand=False)

        self.prepare_context(deps, tools)

        super().run(deps, tools)

    def prepare_context(self, deps, tools):
        self.context = tools.builddir("context")
        with tools.cwd(self.context):
            for task in self.install_tasks:
                deps[task].copy(".", "artifacts/")
        for src, dst in self.install_files:
            tools.copy(src, f"{self.context}/files/{src}")
        tools.copy("images/{board}/{variant}.cfg", self.context)

    def _install_files(self):
        return [self.tools.expand(src) for src, _ in self.install_files]


class DebianImage(Image):
    abstract = True
    distro = DistroNameParameter("debian")
    version = DistroVersionParameter("bullseye")


class JoltOS_Debian(DebianImage):
    name = "joltos/debian"

    board = Parameter(values=["qemu", "qemu_arm"])

    install_pkgs = [
        "linux-image-generic",
        "systemd-sysv",
    ]

    install_files = [
    ]

    install_tasks = [
        "joltos/base-files",
    ]

    remove_files = [
        "/lib/firmware",
        "/usr/share/doc",
        "/usr/share/man",
    ]


class AlpineImage(Image):
    abstract = True
    distro = DistroNameParameter("alpine")
    version = DistroVersionParameter("3.15")


class JoltOS_Alpine(AlpineImage):
    name = "joltos/alpine"

    board = Parameter(values=["qemu", "qemu_arm"])

    install_pkgs = [
        "alpine-base",
        "linux-lts",
    ]

    commands = [
        "rc-update add savecache shutdown",
        "rc-update add killprocs shutdown",
        "rc-update add mount-ro shutdown",

        "rc-update add modules boot",
        "rc-update add hwclock boot",
        "rc-update add hostname boot",
        "rc-update add sysctl boot",
        "rc-update add bootmisc boot",
        "rc-update add syslog boot",

        "rc-update add sysfs sysinit",
        "rc-update add dmesg sysinit",
        "rc-update add mdev sysinit",
        "rc-update add hwdrivers sysinit",
    ]

    install_files = [
    ]

    install_tasks = [
        "joltos/base-files",
    ]

    remove_files = [
        "/lib/firmware",
        "/usr/share/doc",
        "/usr/share/man",
    ]
