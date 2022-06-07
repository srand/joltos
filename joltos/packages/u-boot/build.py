#!/usr/bin/env python3

from jolt import attributes, Parameter, Task, utils
from jolt.plugins import git

from joltos.jolt.tasks import DistroNameParameter
from joltos.jolt.tasks import DistroVersionParameter


supported_defconfigs = [
    "edison",
    "mx7dsabresd",
    "qemu-x86_64",
    "qemu_arm",
    "rpi_3",
    "rpi_4",
]

@git.influence("packages/u-boot")
@attributes.attribute("arch_from_config", "arch_from_config_{_config}")
class UBoot(Task):
    config = Parameter(values=supported_defconfigs)
    sdk = Parameter()

    requires = ["sdk/{sdk}:arch={arch_from_config}"]

    arch_from_config_edison = "amd64"
    arch_from_config_mx7dsabresd = "armv7"
    arch_from_config_qemu_x86_64 = "amd64"
    arch_from_config_qemu_arm = "armv7"
    arch_from_config_rpi_3 = "aarch64"
    arch_from_config_rpi_4 = "aarch64"

    @property
    def _config(self):
        return utils.canonical(str(self.config))

    def run(self, deps, tools):
        self.outdir = tools.builddir(incremental=True)
        with tools.chroot(deps["sdk/{sdk}:arch={arch_from_config}"].paths.rootfs):
            tools.run("make KBUILD_OUTPUT={outdir} {config}_defconfig")
            tools.run("make KBUILD_OUTPUT={outdir} ")

    def publish(self, artifact, tools):
        with tools.cwd(self.outdir):
            artifact.collect("u-boot*")
