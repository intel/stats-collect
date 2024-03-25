.. -*- coding: utf-8 -*-
.. vim: ts=4 sw=4 tw=100 et ai si

:Date:  25-03-2024
:Title: DEPLOY

.. Contents::
    :depth: 2
..

==================
Command *'deploy'*
==================

Deploy stats-collect helpers to a remote SUT (System Under Test).

General options
===============

**-h**
   Show this help message and exit.

**-q**
   Be quiet.

**-d**
   Print debugging information.

**--tmpdir-path** *TMPDIR_PATH*
   When 'stats-collect' is deployed, a random temporary directory is
   used. Use this option provide a custom path instead. It will be used
   as a temporary directory on both local and remote hosts. This option
   is meant for debugging purposes.

**--keep-tmpdir**
   Do not remove the temporary directories created while deploying
   'stats-collect'. This option is meant for debugging purposes.

**-H** *HOSTNAME*, **--host** *HOSTNAME*
   Name of the host to run the command on.

**-U** *USERNAME*, **--username** *USERNAME*
   Name of the user to use for logging into the remote host over SSH.
   The default user name is 'root'.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*
   Path to the private SSH key that should be used for logging into the
   remote host. By default the key is automatically found from standard
   paths like '~/.ssh'.

**-T** *TIMEOUT*, **--timeout** *TIMEOUT*
   SSH connect timeout in seconds, default is 8.
