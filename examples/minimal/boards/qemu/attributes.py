{
    "platform": "linux/amd64",
    "qemu": "kvm -M virt -kernel boot/vmlinuz -initrd boot/initrd.img -m 1G -append 'root=/dev/sda1 rw' -net user -drive file=disk.qcow2,id=hd,if=none,media=disk -device virtio-scsi-device -device scsi-hd,drive=hd -serial stdio"
}
