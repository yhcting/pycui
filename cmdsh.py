import copy
import os
import shlex
from signal import signal, SIGPIPE, SIG_DFL
from subprocess import Popen, PIPE

from cmdbase import BaseCmd, CmdRuntimeError


class CmdSh(BaseCmd):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def cmd(self):
        return 'sh', None

    def help(self):
        return 'execute shell command'

    def run(self, argv, **kwargs):
        if 1 != len(argv):
            return CmdRuntimeError('one and only one shell command is allowed')
        stin = kwargs.get('stin')
        environ = copy.copy(os.environ)
        environ['SHELL'] = '/bin/bash'
        try:
            proc = Popen(
                shlex.split(argv[0]),
                env=environ,
                stdin=PIPE if stin else None,
                stdout=PIPE,
                stderr=PIPE,
                preexec_fn=lambda: signal(SIGPIPE, SIG_DFL))
            if stin:
                proc.stdin.write(stin)
            out, err = proc.communicate()
            if 0 != proc.returncode:
                errmsg = 'Exit code: {}'.format(str(proc.returncode))
                if err:
                    errmsg += '\n{}'.format(err)
                return CmdRuntimeError(errmsg)
        except StandardError as e:
            return CmdRuntimeError('Fail to run shell: ' + str(e))

        return out
