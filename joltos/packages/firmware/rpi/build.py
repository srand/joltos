from jolt import Download, Parameter


class RpiFirmware(Download):
    name = "pkg/firmware/rpi"
    version = Parameter("refs/heads/master")
    url = "https://github.com/raspberrypi/firmware/archive/{version}.zip"
    collect = [{"files": "*/boot", "dest": "boot", "flatten": True}]
