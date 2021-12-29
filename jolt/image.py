#!/usr/bin/env python

import json


from jolt import attributes, influence, Parameter, Task, utils
from jolt.plugins.docker import DockerImage


@attributes.requires("install_tasks")
@influence.files("{template}")
@influence.files("{_install_files}")
@influence.files("images/{board}/{variant}.cfg")
class Image(DockerImage):
    abstract = True

    base = None
    variant = Parameter("default", values=["default"])

    ############################################################################

    install_pkgs = []
    install_tasks = []
    install_files = []
    remove_files = []
    remove_pkgs = []
    platform = None
    rootpass = "joltos"

    ############################################################################

    cleanup = False
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
    base = "debian:bullseye"
    template = "docker/Dockerfile.debian"


@attributes.attribute("platform", "platform_{board}")
class JoltOS(DebianImage):
    board = Parameter(values=["qemu", "qemu_arm"])

    platform_qemu = "linux/amd64"
    platform_qemu_arm = "linux/arm/v7"

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


@attributes.attribute("qemu", "qemu_{board}")
class Qemu(Task):
    """ Run Jolt OS in QEMU/KVM """

    board = Parameter(values=["qemu", "qemu_arm"])
    variant = Parameter("default", values=["default"])

    cacheable = False
    requires = ["joltos:board={board},variant={variant}"]

    qemu_qemu = "kvm"
    qemu_qemu_arm = "qemu-system-arm"

    def run(self, deps, tools):
        self.builddir = tools.sandbox(deps[self.requires[0]])
        with tools.cwd(self.builddir, "rootfs"):
            import subprocess
            subprocess.call(tools.expand("{qemu} -m 1G -kernel vmlinuz -initrd initrd.img -hda rootfs.qcow2 -append 'root=/dev/sda rw console=ttyS0' -serial stdio -net user"), shell=True, env=tools._env, cwd=tools.getcwd())
