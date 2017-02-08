import sys
import time
from cStringIO import StringIO


def add_line_indent(string, size, ch=' '):
    return '\n'.join([ch * size + ln for ln in string.split('\n')])


def stdout_as_string(func, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    func(*args, **kwargs)
    sys.stdout = old_stdout
    return mystdout.getvalue()


def split_to_lines_excluding_empty_line(text):
    lns = []
    for ln in text.split('\n'):
        ln = ln.strip()
        if 0 == len(ln):
            continue
        lns.append(ln)
    return lns


# noinspection PyPep8Naming
_HEARTBEAT = ['|', '/', '-', '\\']
# noinspection PyPep8Naming
_PROG_PARAGRAPH = 80


def show_progress(is_done):
    # print heart-beat while command thread is running
    cnt = 0
    len_heartbeat = len(_HEARTBEAT)
    while not is_done():
        if cnt >= _PROG_PARAGRAPH * len_heartbeat:
            cnt -= _PROG_PARAGRAPH * len_heartbeat
            sys.stdout.write('\r' + '#' * _PROG_PARAGRAPH + '\n')
        sys.stdout.write('\r{}{}'.format(
            int(cnt / len_heartbeat) * '#',
            _HEARTBEAT[cnt % len_heartbeat]))
        sys.stdout.flush()
        cnt += 1
        time.sleep(0.5)
    sys.stdout.write('\r')
    sys.stdout.flush()
