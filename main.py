from __future__ import print_function

import collections
import shlex
import shutil
import sys
import tempfile
import threading
import time
import traceback

import ut
from cmdbase import CmdRuntimeError
from cmdgroup import CmdHandler
from cmdhelp import CmdHelp
from cmdhistory import CmdHistory
from cmdsh import CmdSh
from cmdfile import CmdFile


class AsyncRunner(threading.Thread):
    def __init__(self, runnable, cancellable,
                 *args, **kwargs):
        super(AsyncRunner, self).__init__()
        if not runnable:
            AssertionError('Invalid argument: runnable MUST not be None')
        self.runnable = runnable
        self.cancellable = cancellable
        self.args = args
        self.kwargs = kwargs
        self.ret = None
        self.excep = None
        self._cancelled = False

    def cancel(self):
        if self.cancellable:
            self._cancelled = self.cancellable()
            return self._cancelled
        return False

    def is_cancelled(self):
        return self._cancelled

    def run(self):
        try:
            if 'is_cancelled' not in self.kwargs:
                self.kwargs['is_cancelled'] = self.is_cancelled
            self.ret = self.runnable(*self.args, **self.kwargs)
        except BaseException as e:
            traceback.print_exc()
            self.excep = e


def _run_async_runner(async_runner,
                      pre_text=None, post_text=None):
    if pre_text:
        sys.stdout.write('\n' + pre_text + '\n')
    async_runner.start()
    while async_runner.is_alive():
        try:
            time.sleep(0.1)
            ut.show_progress(lambda: not async_runner.is_alive())
            if async_runner.excep:
                raise async_runner.excep
        except KeyboardInterrupt:
            sys.stdout.write('\rInterrupted!, Now cancelling...\n')
            if not async_runner.cancel():
                sys.stdout.write('\rCancel fails(Or nothing to cancel)! Interrupt ignored!\n')
    if async_runner.is_cancelled():
        sys.stdout.write('\rCancelled!\n')
        return False
    if post_text:
        sys.stdout.write('\n' + post_text + '\n')
    return True


def _split_cmds_via_pipe(shargs):
    ls = []
    while len(shargs) > 0:
        try:
            i = shargs.index('|')
        except ValueError:
            ls.append(shargs)
            break
        ls.append(shargs[0:i])
        shargs = shargs[i + 1:]
    return ls


def _prmsg(text):
    sys.stdout.write(text)


def __run_prompt(ch, cmd_history, history_size):
    sys.stdout.write('>>> ')
    line = sys.stdin.readline()
    if 0 == len(line):
        return False  # end of prompt
    line = line.rstrip()
    try:
        shargs = shlex.split(line)
    except ValueError as e:
        sys.stdout.write('Syntax error: {}\n'.format(e.message))
        return True
    cmdlist = _split_cmds_via_pipe(shargs)
    last_result = None
    interrupted = False
    for cmd in cmdlist:
        crnr = AsyncRunner(ch.run, ch.cancel, cmd,
                           stin=last_result,
                           prmsg=_prmsg)
        if not _run_async_runner(crnr):
            interrupted = True
            break
        if isinstance(crnr.ret, CmdRuntimeError):
            msg = 'E:{}\n'.format(crnr.ret.message)
            if crnr.ret.maybe:
                name, alias = crnr.ret.maybe.cmd()
                msg += 'You may intend: ' + name
                if alias:
                    msg += ', ' + alias
            sys.stdout.write(msg + '\n')
            last_result = None
            break
        else:
            last_result = crnr.ret

    if interrupted or not last_result:
        return True  # command is not successfully completed.
    print(last_result)
    if len(cmd_history) > 0:
        prev_line = cmd_history.pop()
        if shlex.split(prev_line) != shlex.split(line):
            cmd_history.append(prev_line)
    if len(cmd_history) >= history_size:
        cmd_history.popleft()
    cmd_history.append(line)
    return True


def _run_prompt(cmds,
                prepare_runnable,
                prepare_cancellable,
                history_size, tmpdir):
    cmd_history = collections.deque()  # a kind of LRU cache
    ch = CmdHandler(CmdHelp())
    # add builtin commands
    ch.register(CmdSh(tmpdir))
    ch.register(CmdHistory(cmd_history))
    ch.register(CmdFile())
    # add custom commands
    for c in cmds:
        ch.register(c)

    if prepare_runnable:
        arunner = AsyncRunner(prepare_runnable,
                              prepare_cancellable,
                              prmsg=_prmsg)
        if not _run_async_runner(
                arunner,
                pre_text='Preparing...',
                post_text='Ready!'):
            sys.stdout.write('Preparation is NOT completed! Terminated!\n')
            sys.exit(1)
    while True:
        try:
            if not __run_prompt(ch, cmd_history, history_size):
                break  # exit from loop
        except KeyboardInterrupt:
            sys.stdout.write('Plase use CTRL-D to exit from prompt!')


def run_prompt(cmds,
               prepare_func=None,
               cancel_prepare_func=None,
               history_size=1000):
    tmpdir = tempfile.mkdtemp()
    try:
        _run_prompt(cmds,
                    prepare_func, cancel_prepare_func,
                    history_size, tmpdir)
    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    run_prompt([])
