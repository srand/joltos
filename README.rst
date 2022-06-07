JoltOS
======

The aim of JoltOS is to become a framework for building custom Linux images
based on popular distributions, such as Debian, Ubuntu, Alpine, etc. Unlike
Yocto, the intention is not to build distributions from scratch, but to
utilize pre-built binaries to the greatest extent possible through publically
available Docker images and package repositories.


Prerequisites
-------------

JoltOS is built upon the Jolt task execution tool. Install both with:

  .. code-block:: bash

    $ pip install joltos

Python 3.9 or later is required.

JoltOS also needs Docker. Version 20 or later is recommended. The latest version can be installed with:

  .. code-block:: bash

    $ curl https://get.docker.com | sh

For cross-platform builds, the binfmt-support and qemu-user-static packages are required. 
Install them with your system's package manager:

  .. code-block:: bash

    $ sudo apt install -y binfmt-support qemu-user-static


Building an Image
-----------------

A minimal example image is available in the `examples/minimal` subdirectory. Build it by running this Jolt command:

  .. code-block:: bash

    $ jolt build minimal/debian:board=qemu


Customizing Images
------------------

Create a Jolt Python class inheriting either AlpineImage or DebianImage. 
Both base classes define different attributes that can be overridden to 
customize the image.

 - install_files - List of files to be copied into the image.
 - install_pkgs - List of packages to be installed using the distro package manager.
 - install_tasks - List of Jolt task artifacts to be copied into the image.
 - remove_files - List of files to remove from the image.
 - remove_pkgs - List of packages to be removed using the distro package manager.

Image formats are chosen using decorators:

 - joltos.attributes.squashfs - Builds a squashfs image
 - joltos.attributes.tar - Builds a tar archive

Multiple image types can be built at once. 

  .. code-block:: python

    @joltos.attributes.squashfs
    @joltos.attributes.tar
    class MinimalDebianRootfs(DebianRootfs):
      """ A minimal rootfs with systemd, as squashfs and tar images """
      name = "minimal/debian"
      install_pkgs = ["nano"]
      remove_files = [
        "/usr/share/doc",
        "/usr/share/man",
      ]


To build different variants of an image for different types of boards you 
can add conditional attributes that are selected based on the values of 
build parameters. Example:

  .. code-block:: python

    @joltos.attributes.tar
    @joltos.attributes.install_pkgs("install_pkgs_{board}")
    @joltos.attributes.install_pkgs("install_pkgs_{variant}")
    class MinimalDebianRootfs(DebianRootfs):
      """ A minimal rootfs with systemd, as squashfs and tar images """
      name = "minimal/debian"

      # This attribute is always selected
      install_pkgs = ["nano"]

      # This attribute is selected when variant=debug
      install_pkgs_debug = ["gdb"]

      # This attribute is selected when board=qemu
      install_pkgs_qemu = []

  .. code-block:: bash

    $ jolt build minimal/debian:board=qemu,variant=debug
