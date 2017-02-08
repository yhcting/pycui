import ut
from cmdbase import BaseCmd


class CmdHelp(BaseCmd):
    def __init__(self, cmds=None):
        self.cmds = cmds
        self.text = None

    def cmd(self):
        return 'help', 'h'

    def help(self):
        return 'Show help text'

    def run(self, argv, **kwargs):
        cmdsets = set()
        for c in self.cmds.itervalues():
            cmdsets.add(c)
        cnames = []
        for c in cmdsets:
            n, a = c.cmd()
            cnames.append(n)
        cnames.sort()
        texts = []
        for name in cnames:
            c = self.cmds[name]
            texts.append('{}\n{}'.format(
                c.cmdset_string(), ut.add_line_indent(c.help(), 4)))
        return '\n\n'.join(texts)

    def set_cmdlist(self, cmds):
        self.cmds = cmds


class CmdHelpOpt(CmdHelp):
    def __init__(self, cmds=None):
        super(CmdHelpOpt, self).__init__(cmds)

    def cmd(self):
        return '--help', '-h'
