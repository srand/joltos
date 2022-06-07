#!/usr/bin/env python3

from jolt import attributes, Parameter, Task
from jolt.plugins import git


@git.influence("u-boot")
@attributes.attribute("sdk_arch", "sdk_arch_{arch}")
class Kernel(Task):
    name = "pkg/linux"

    arch = Parameter("armv7")
    sdk = Parameter()
    defconfig = Parameter(required=False)

    requires = ["sdk/{sdk}:arch={arch}"]
    sdk_arch_armv7 = "arm"

    @property
    def _defconfig(self):
        return self.tools.expand("{defconfig}_defconfig") if self.defconfig.is_set() else "defconfig"

    def run(self, deps, tools):
        self.outdir = tools.builddir(incremental=True)
        with tools.chroot(deps["tools/{sdk}"].paths.rootfs):
            tools.run("make ARCH={sdk_arch} KBUILD_OUTPUT={outdir} {_defconfig}")
            tools.run("make ARCH={sdk_arch} KBUILD_OUTPUT={outdir} -j {}", tools.thread_count())
            tools.run("make ARCH={sdk_arch} KBUILD_OUTPUT={outdir} INSTALL_MOD_PATH={outdir}/modules -j {} modules_install", tools.thread_count())

    def publish(self, artifact, tools):
        with tools.cwd(self.outdir):
            artifact.collect("*.deb")
