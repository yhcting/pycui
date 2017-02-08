from cmdbase import BaseCmd


class CmdHistory(BaseCmd):
    def __init__(self, cmd_history):
        self.cmd_history = cmd_history  # collections.deque

    def cmd(self):
        return 'history', None

    def help(self):
        return 'Show command history'

    def run(self, argv, **kwargs):
        lines = []
        for cln in self.cmd_history:
            lines.append('{}: {}'.format(str(len(lines)), cln))
        return '\n'.join(lines)
