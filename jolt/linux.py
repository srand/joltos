#!/usr/bin/env python3

from jolt import attributes, Parameter, Task
from jolt.plugins import git


@git.influence("u-boot")
@attributes.attribute("sdk_arch", "sdk_arch_{arch}")
class Kernel(Task):
    arch = Parameter()
    defconfig = Parameter(required=False)

    requires = ["sdk:arch={sdk_arch}"]
    sdk_arch_arm = "armv7"

    @property
    def _defconfig(self):
        return self.tools.expand("{defconfig}_defconfig") if self.defconfig.is_set() else "defconfig"

    def run(self, deps, tools):
        self.outdir = tools.builddir(incremental=True)
        with tools.chroot(deps["tools"].paths.rootfs):
            tools.run("make -C {joltdir}/packages/linux ARCH={arch} KBUILD_OUTPUT={outdir} {_defconfig}")
            tools.run("make -C {joltdir}/packages/linux ARCH={arch} KBUILD_OUTPUT={outdir} -j {}", tools.thread_count())
            tools.run("make -C {joltdir}/packages/linux ARCH={arch} KBUILD_OUTPUT={outdir} INSTALL_MOD_PATH={outdir}/modules -j {} modules_install", tools.thread_count())

    def publish(self, artifact, tools):
        with tools.cwd(self.outdir):
            artifact.collect("*.deb")
