#!/usr/bin/env python

import json
import os


from jolt import attributes as jolt_attributes, influence, Parameter, Task, utils
from jolt.plugins.docker import DockerImage, _Tarfile

from .tasks import BoardParameter
from .tasks import DistroNameParameter
from .tasks import DistroVersionParameter


class attributes:
    @staticmethod
    def commands(name):
        return utils.concat_attributes("commands", name)

    @staticmethod
    def install_files(name):
        return utils.concat_attributes("install_files", name)

    @staticmethod
    def install_pkgs(name):
        return utils.concat_attributes("install_pkgs", name)

    @staticmethod
    def install_tasks(name):
        def decorator(cls):
            cls = jolt_attributes.requires("install_tasks")(cls)
            cls = utils.concat_attributes("install_tasks", name)(cls)
            return cls

        return decorator
    
    @staticmethod
    def remove_files(name):
        return utils.concat_attributes("remove_files", name)

    @staticmethod
    def remove_pkgs(name):
        return utils.concat_attributes("remove_pkgs", name)

    def squashfs(cls):
        class SquashFS(cls):
            def run(self, deps, tools):
                super().run(deps, tools)
                self.run_build_directory(deps, tools)
                self.run_build_squashfs(deps, tools)

            def run_build_squashfs(self, deps, tools):
                with tools.cwd(tools.builddir()):
                    with tools.unshare() as ns, ns:
                        self.info("Building squashfs")
                        tools.run("mksquashfs rootfs/ {canonical_name}.squashfs")

            def publish(self, artifact, tools):
                super().publish(artifact, tools)
                with tools.cwd(tools.builddir()):
                    artifact.collect("{canonical_name}.squashfs")

            def publish_default(self, artifact, tools):
                pass
        
        return SquashFS

    def tar(cls):
        class Tar(cls):
            def run(self, deps, tools):
                super().run(deps, tools)
                self.run_build_directory(deps, tools)
                self.run_build_tar(deps, tools)

            def run_build_tar(self, deps, tools):
                with tools.cwd(tools.builddir()):
                    with tools.unshare() as ns, ns:
                        self.info("Building tar")
                        tools.archive("rootfs/", "{canonical_name}.tar")

            def publish(self, artifact, tools):
                super().publish(artifact, tools)
                with tools.cwd(tools.builddir()):
                    artifact.collect("{canonical_name}.tar")

            def publish_default(self, artifact, tools):
                pass
        
        return Tar




@attributes.commands("commands")
@attributes.install_files("install_files")
@attributes.install_pkgs("install_pkgs")
@attributes.install_tasks("install_tasks")
@attributes.remove_files("remove_files")
@attributes.remove_pkgs("remove_pkgs")
class Rootfs(DockerImage):
    abstract = True

    base = None
    distro = DistroNameParameter()
    version = DistroVersionParameter()
    variant = Parameter("default", values=["default"], help="Image variant")
    board = Parameter(help="Board name")

    ############################################################################

    commands = []
    install_pkgs = []
    install_tasks = []
    install_files = []
    remove_files = []
    remove_pkgs = []
    platform = None
    rootpass = "joltos"
    requires_image = []

    ############################################################################

    context = "images"
    pull = True
    squash = True
    taint = 1

    def _render(self, template, **kwargs):
        from jinja2 import Environment, PackageLoader, select_autoescape
        from jolt.tools import JinjaTaskContext
        env = Environment(
            loader=PackageLoader("joltos"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True)
        env.context_class = JinjaTaskContext
        tmpl = env.get_template(template)
        return tmpl.render(task=self, tools=self.tools, **kwargs)

    def run(self, deps, tools):
        content = self._render(tools.expand("Dockerfile.{distro}"), deps=deps)
        with tools.cwd(tools.builddir("dockerfile")):
            self.dockerfile = tools.expand_path("Dockerfile")
            tools.write_file(self.dockerfile, content, expand=False)

        self.prepare_context(deps, tools)
        super().run(deps, tools)

    def run_build_directory(self, deps, tools):
        with tools.cwd(tools.builddir()):
            targetpath = tools.expand_path("rootfs/")
            if os.path.exists(targetpath):
                return
            self.info("Extracting Docker image")
            with tools.unshare() as ns, ns:
                tools.extract(self._imagefile, "layers/")
                manifest = json.loads(tools.read_file("layers/manifest.json"))
                for image in manifest:
                    for layer in image.get("Layers", []):
                        self.info("- {}", os.path.dirname(layer))
                        layerpath = tools.expand_path(os.path.join("layers", layer))
                        with _Tarfile.open(layerpath, 'r') as tar:
                            tar.extractall(targetpath)

    def publish(self, artifact, tools):
        self.publish_default(artifact, tools)

    def publish_default(self, artifact, tools):
        super().publish(artifact, tools)

    def prepare_context(self, deps, tools):
        self.context = tools.builddir("context")
        with tools.cwd(self.context):
            tools.mkdir("artifacts")
            for task in self._install_tasks():
                deps[task].copy(".", "artifacts/")
        for src, dst in self._install_files():
            tools.copy(src, f"{self.context}/files/{src}")


class BareDebianRootfs(Rootfs):
    abstract = True
    distro = DistroNameParameter("debian")
    version = DistroVersionParameter("bullseye")


@attributes.install_pkgs("install_pkgs_default")
class DebianRootfs(BareDebianRootfs):
    name = "joltos/debian"

    board = BoardParameter()

    install_pkgs_default = [
        "linux-image-generic",
        "systemd-sysv",
    ]


class BareAlpineRootfs(Rootfs):
    abstract = True
    distro = DistroNameParameter("alpine")
    version = DistroVersionParameter("3.15")


@attributes.commands("commands_default")
@attributes.install_pkgs("install_pkgs_default")
class AlpineRootfs(BareAlpineRootfs):
    abstract = True

    board = BoardParameter()

    install_pkgs_default = [
        "alpine-base",
        "linux-lts",
    ]

    commands_default = [
        "rc-update add savecache shutdown",
        "rc-update add killprocs shutdown",
        "rc-update add mount-ro shutdown",

        "rc-update add modules boot",
        "rc-update add hwclock boot",
        "rc-update add hostname boot",
        "rc-update add bootmisc boot",
        "rc-update add syslog boot",

        "rc-update add sysfs sysinit",
        "rc-update add dmesg sysinit",
        "rc-update add mdev sysinit",
        "rc-update add hwdrivers sysinit",
    ]
