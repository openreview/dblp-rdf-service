import subprocess
import threading
from typing import Optional
import typing as t
import os
import signal
import sys
import re


class FusekiServerManager:
    startup_event: threading.Event

    def __init__(
        self,
        fuseki_executable: str = "fuseki-server",
        db_location: Optional[str] = None,
        verbose: bool = False,
    ):
        self.fuseki_executable = fuseki_executable
        self.db_location = db_location
        self.process = None
        self.db_dir = None
        self.startup_event = threading.Event()
        self.verbose = verbose

    def _echo_output(self, stream: t.Any):
        """Echo subprocess output to stdout."""
        for line in iter(stream.readline, ""):
            if re.search(":: Started ", str(line)):
                print("Fuseki server ready...")
                self.startup_event.set()

            if self.verbose:
                bs = bytes(line, encoding="UTF-8")
                sys.stdout.buffer.write(bs)
                sys.stdout.buffer.flush()

    async def __aenter__(self):
        cmd = [self.fuseki_executable, "--update"]
        if self.db_location is None:
            cmd.append("--mem")
        else:
            db_path = self.db_location
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            cmd.extend(["--loc", db_path])

        cmd.append("/ds")

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Start a thread to echo the output
        self.thread = threading.Thread(target=self._echo_output, args=(self.process.stdout,))
        self.thread.start()
        self.startup_event.wait()

        return self

    async def __aexit__(self, exc_type: t.Any, exc_value: object, traceback: object):
        print("Fuseki exiting")
        # Terminate the Fuseki server process
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()

        # Wait for the output thread to finish
        self.thread.join()

        # Clean up the temporary directory if used
        if self.db_dir:
            self.db_dir.cleanup()
