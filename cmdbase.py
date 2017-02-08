import abc


class BaseCmd(object):
    """
    Command object.
    Command object MUST be stateless and re-runnable!
    That is, command object may be run multiple-times at one-instance!
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def cmd(self):
        """\
        Return command string of this command. (name, alias) tuple is returned.
        """
        pass

    def cmdset_string(self):
        """/
        get command set string. Usually used at error message
        """
        name, alias = self.cmd()
        if not name:
            AssertionError('Command name is mandatory!')
        t = name
        if alias:
            t += ', ' + alias
        return t

    @abc.abstractmethod
    def help(self):
        """Return short help string for this command"""
        pass

    @abc.abstractmethod
    def run(self, argv, **kwargs):
        """\
        This function is run on non-main(UI) thread-context.
        This function SHOULD return text that should be displayed at console.

        :param argv: (list) arguments
        :param kwargs: {
            'stin': (path) input file path passed from pipe command
            'is_cancelled': (func) function to check command is cancelled
            'prmsg': (func) function to print progress message.
        }
        """
        pass


class CmdRuntimeError(object):
    def __init__(self, message='', maybe=None):
        """
        :param message: (str)
        :param maybe: (BaseCmd)
        """
        self.message = message
        self.maybe = maybe
