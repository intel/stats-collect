<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

This file is converted to a man page using pandoc. The ":   " prefix uses the
pandoc definition list syntax to produce proper option entries in the man output.
-->

# Command *'deploy'*

Deploy stats-collect helpers to a remote SUT (System Under Test).

## General options

**-h**

:   Show this help message and exit.

**-q**

:   Be quiet (print only important messages like warnings).

**-d**

:   Print debugging information.

**--debug-modules** *MODNAME[,MODNAME1,...]*

:   Print debugging information only from the specified modules.

**--force-color**

:   Force colorized output even if the output stream is not a terminal (adds ANSI escape codes).

**--tmpdir-path** *TMPDIR_PATH*

:   When 'stats-collect' is deployed, a random temporary directory is used. Use this option to
    provide a custom path instead. It will be used as a temporary directory on both local and
    remote hosts. This option is meant for debugging purposes.

**--keep-tmpdir**

:   Do not remove the temporary directories created while deploying 'stats-collect'. This option
    is meant for debugging purposes.

**-H** *HOSTNAME*, **--host** *HOSTNAME*

:   Host name or IP address of the remote host to deploy to over SSH. Defaults to local host.

**-U** *USERNAME*, **--username** *USERNAME*

:   Name of the user to use for logging into the remote host over SSH. By default, look up the
    user name in SSH configuration files. If not found, use the current user name.

**-K** *PRIVKEY*, **--priv-key** *PRIVKEY*

:   Path to the private SSH key for logging into the remote host. If not specified, keys
    configured for the host in SSH configuration files (e.g. `~/.ssh/config`) are used. If no
    keys are configured there, standard key files (e.g. `~/.ssh/id_rsa`) and the SSH agent are
    tried.
