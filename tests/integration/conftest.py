import os
import sys

import pytest
from xprocess import ProcessStarter


@pytest.fixture(scope="module")
def mbox_process(xprocess):
    main_path = os.path.join(pytest.__pytestPDB._config.rootdir, "main.py")

    class Starter(ProcessStarter):
        python_executable_full_path = sys.executable

        timeout = 20
        max_read_lines = 150
        # startup pattern
        pattern = "Music Box is all set up and ready to go!"

        # command to start process
        args = [python_executable_full_path, main_path, "debug"]

    # ensure process is running and return its logfile
    logfile = xprocess.ensure("mbox_process", Starter)

    yield logfile

    # clean up whole process tree afterwards
    xprocess.getinfo("mbox_process").terminate()
