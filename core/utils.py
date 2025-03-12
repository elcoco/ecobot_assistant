import os
from pathlib import Path
from typing import Optional
import subprocess
from threading import Thread
import numpy as np


class StoppableThread(Thread):
    def __init__(self):
        super().__init__()
        self._is_stopped = False

    def stop(self):
        self._is_stopped = True

    def is_stopped(self):
        return self._is_stopped



class Buffer():
    def __init__(self):
        self._data = np.array([0,1])
        self._had_data = False

    def put(self, data):
        #self._data += data
        self._data = np.concatenate((self._data, data))
        self._had_data = True

    def is_empty(self):
        return not self._data.size and self._had_data

    def get(self, size: int):
        ret = self._data[:size]
        self._data = self._data[size:]
        if ret.size < size:
            ret = np.pad(ret, (0,size-ret.size), mode='constant', constant_values=0)

        return ret



def run_cmd(cmd: list[str], timeout: int=-1, user: Optional[str]=None, envs: Optional[dict[str,str]]=None, cwd: Optional[Path]=None, raise_on_err=True):
    # this fixes all sort of localisation issues like ',' for '.' in numbers
    env = os.environ.copy()
    env["LC_ALL"] = "C"

    if envs:
        for k,v in envs.items():
            env[k] = v

    # raises FileNotFoundError if command is not found
    try:
        if timeout > 0:
            result = subprocess.run(cmd, capture_output=True, encoding="utf8", user=user, env=env, cwd=cwd, timeout=timeout)
        else:
            result = subprocess.run(cmd, capture_output=True, encoding="utf8", user=user, env=env, cwd=cwd)

    except subprocess.TimeoutExpired as e:
        raise OSError(e)
    except FileNotFoundError as e:
        raise OSError(e)

    # raises subprocess.CalledProcessError if exitcode is not 0
    try:
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        print(result.stdout)
        print(result.stderr)
        if raise_on_err:
            raise OSError(e)

    return result
