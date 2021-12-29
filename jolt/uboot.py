#!/usr/bin/env python3

from jolt import attributes, Parameter, Task
from jolt.plugins import git

supported_defconfigs = [
    "mx7dsabresd",
    "qemu_arm",
    "rpi_3",
    "rpi_4",
]

@git.influence("u-boot")
@attributes.attribute("sdk_arch", "sdk_arch_{defconfig}")
class UBoot(Task):
    defconfig = Parameter(values=supported_defconfigs)
    version = Parameter("v2021.10")

    requires = ["sdk:arch={sdk_arch}"]

    sdk_arch_mx7dsabresd = "armv7"
    sdk_arch_qemu_arm = "armv7"
    sdk_arch_rpi_3 = "aarch64"
    sdk_arch_rpi_4 = "aarch64"

    def run(self, deps, tools):
        self.outdir = tools.builddir()
        with tools.chroot(deps["tools"].paths.rootfs):
            tools.run("make -C {joltdir}/packages/u-boot KBUILD_OUTPUT={outdir} {defconfig}_defconfig")
            tools.run("make -C {joltdir}/packages/u-boot KBUILD_OUTPUT={outdir} ")

    def publish(self, artifact, tools):
        with tools.cwd(self.outdir):
            artifact.collect("u-boot*")
