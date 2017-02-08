import argparse

from cmdbase import BaseCmd, CmdRuntimeError
from cmdgroup import CmdGroup


class _CmdFileSave(BaseCmd):
    def __init__(self):
        self._argp = _CmdFileSave._mk_argparser()

    @classmethod
    def _mk_argparser(cls):
        p = argparse.ArgumentParser(prog='file save')
        p.add_argument('dest', nargs=1,
                       type=argparse.FileType('wb'),
                       help='Output file generated. If file already exists, it is overwritten')
        return p

    def cmd(self):
        return 'save', 's'

    def help(self):
        return '''Save text passed via pipe(stin) as file. For details use "file save -h"'''

    def run(self, argv, **kwargs):
        try:
            args = self._argp.parse_args(argv)
        except SystemExit:
            return CmdRuntimeError()  # error message already displayed
        fdst = args.dest[0]
        try:
            stin = kwargs.get('stin')
            if stin:
                fdst.write(stin)
        finally:
            fdst.close()


##############################################################################
#
#
#
##############################################################################
class CmdFile(CmdGroup):
    def __init__(self):
        subs = [
            _CmdFileSave(),
        ]
        super(CmdFile, self).__init__(subs)

    def help(self):
        return super(CmdFile, self).help() + '''do file operation.
    Usage: file <sub-command> <sub-command-args> ...'''

    def cmd(self):
        return 'file', None
