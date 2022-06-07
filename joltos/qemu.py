from jolt import attributes, Parameter, Task


@attributes.attribute("qemu", "qemu_{board}")
class Qemu(Task):
    """ Run Jolt OS in QEMU/KVM """

    abstract = True

    board = Parameter(values=["qemu", "qemu_arm"])
    variant = Parameter("default", values=["default"])

    cacheable = False

    append = ""
    kernel = "vmlinuz"
    initrd = "initrd.img"
    qemu_qemu = "kvm"
    qemu_qemu_arm = "qemu-system-arm"
    root = "/dev/sda1"

    def run(self, deps, tools):
        self.builddir = tools.sandbox(deps[self.requires[0]])
        with tools.cwd(self.builddir, "rootfs"):
            import subprocess
            subprocess.call(tools.expand("{qemu} -m 1G -kernel {kernel} -initrd {initrd} -hda rootfs.qcow2 -append 'root={root} rw console=ttyS0 {append}' -net nic -net user -nographic"), shell=True, env=tools._env, cwd=tools.getcwd())


class QemuAlpine(Qemu):
    name = "qemu/alpine"
    requires = ["joltos/alpine:board={board},variant={variant}"]
    kernel = "vmlinuz-*"
    initrd = "initramfs-*"
    append = "modules=ext4"


class QemuDebian(Qemu):
    name = "qemu/debian"
    requires = ["joltos/debian:board={board},variant={variant}"]
