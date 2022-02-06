JoltOS
======

The aim of JoltOS is to become a framework for building custom Linux images
based on popular distributions, such as Debian, Ubuntu, Alpine, etc. Unlike
Yocto, the intention is not to build distributions from scratch, but to
utilize pre-built binaries to the greatest extent possible through publically
available Docker images and package repositories.


Prerequisites
-------------

JoltOS is built upon the Jolt task execution tool. Install it with:

  .. code-block:: bash

    $ pip install jolt

Python 3.9 or later is required.

JoltOS also needs Docker. Version 20 or later is recommended. The latest version can be installed with:

  .. code-block:: bash

    $ curl https://get.docker.com | sh

To emulate images, install Qemu using your operating system's package manager.


Building an Image
-----------------

A demo image for the Qemu virt machine can be built with the ``joltos`` Jolt task:

  .. code-block:: bash

    $ jolt build joltos/debian:board=qemu

Or, if you prefer an image based on Alpine:

  .. code-block:: bash

    $ jolt build joltos/alpine:board=qemu

It can then be emulated with:

  .. code-block:: bash

    $ jolt build qemu/debian:board=qemu

The built image is currently based on Debian. Supported boards are ``qemu`` and ``qemu_arm``.


Customizing Images
------------------

Work in progress.

Create a subclass of the JoltOS Python class and assign class attributes as appropriate.
