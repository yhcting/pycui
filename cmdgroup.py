import abc
from difflib import SequenceMatcher

from cmdbase import BaseCmd, CmdRuntimeError
from cmdhelp import CmdHelpOpt, CmdHelp


class CmdGroup(BaseCmd):
    def __init__(self, cmds):
        self.cmdh = CmdHandler(CmdHelpOpt())
        for c in cmds:
            self.cmdh.register(c)

    @abc.abstractmethod
    def cmd(self):
        pass

    def cancel(self):
        return self.cmdh.cancel()

    def help(self):
        return '(Command group) '

    def run(self, argv, **kwargs):
        r = self.cmdh.run(argv, **kwargs)
        if isinstance(r, CmdRuntimeError):
            r.message = '[{}] '.format(self.cmdset_string()) + r.message
        return r


def _similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


class CmdRunner(object):
    def __init__(self, cmd):
        if not cmd:
            raise AssertionError('')
        self.cmd = cmd
        self.cancelled = False

    def is_cancelled(self):
        return self.cancelled

    def cancel(self):
        """Cancel this command"""
        if self.cancelled:
            return False
        self.cancelled = True
        return self.cancelled

    def run(self, argv, **kwargs):
        if 'is_cancelled' not in kwargs:
            kwargs['is_cancelled'] = self.is_cancelled
        return self.cmd.run(argv, **kwargs)


class CmdHandler(object):
    def __init__(self, help_cmd):
        self.crunner = None  # current command runner
        self._lastcmd_cancelled = False
        self.cmds = dict()
        self._help_cmd = help_cmd
        if help_cmd:
            if not isinstance(help_cmd, CmdHelp):
                raise AssertionError('Invalid help command object')
            self.register(help_cmd)
        help_cmd.set_cmdlist(self.cmds)

    def register(self, cmd):
        if not isinstance(cmd, BaseCmd):
            raise AssertionError('Cmd MUST be subclass of BaseCmd')
        name, alias = cmd.cmd()
        if ((name and name in self.cmds)
                or (alias and alias in self.cmds)):
            raise AssertionError('Duplicated command name(long or short)')
        if name:
            self.cmds[name] = cmd
        if alias:
            self.cmds[alias] = cmd

    def cancel(self):
        try:
            self.crunner.cancel()
            return self.crunner.is_cancelled()
        except AttributeError as e:
            print(str(e))
            return False  # self.crunner may be NONE and it is not-a-problem.

    def is_lastcmd_cancelled(self):
        try:
            return self.crunner.is_cancelled()
        except AttributeError:
            return False  # self.crunner may be NONE and it is not-a-problem.

    def run(self, argv, **kwargs):
        """
        :param argv: (list) argument list
        :return: (str) if success, otherwise predefined-object.
        """
        self.crunner = None
        if 0 == len(argv):
            return CmdRuntimeError('Missing command', self._help_cmd)
        cmd = argv[0]
        if cmd in self.cmds:
            self.crunner = CmdRunner(self.cmds[cmd])
            cmdret = self.crunner.run(argv[1:], **kwargs)
            self.crunner = None
            return cmdret

        # Fail to find command
        similar_cmd = None
        max_similarity = 0
        for c in self.cmds.values():
            name, alias = c.cmd()
            similarity = _similarity_ratio(name, cmd)
            if similarity > max_similarity:
                max_similarity = similarity
                similar_cmd = c
            similarity = 0
            if alias:
                similarity = _similarity_ratio(alias, cmd)
            if similarity > max_similarity:
                max_similarity = similarity
                similar_cmd = c
        if not similar_cmd:
            if 'help' in self.cmds:
                similar_cmd = self.cmds['help']
            elif '--help' in self.cmds:
                similar_cmd = self.cmds['--help']
        return CmdRuntimeError('Unknown command', similar_cmd)
