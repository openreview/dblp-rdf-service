#!/usr/bin/env python3
import subprocess
import threading
from typing import Optional
import typing as t
import os
import signal
import sys
import tempfile
import time
import asyncio
import re


async def waiter(event: asyncio.Event):
    print("waiter enter")
    await event.wait()
    print("waiter exit")

class FusekiServerManager:
    # startup_event: asyncio.Event
    startup_event: threading.Event

    def __init__(
        self,
        fuseki_executable: str = "fuseki-server",
        db_location: Optional[str] = None,
        file: Optional[str] = None,
    ):
        self.fuseki_executable = fuseki_executable
        self.db_location = db_location
        self.file = file
        self.process = None
        self.db_dir = None
        self.startup_event = threading.Event()
        print("done __init__")

    def _echo_output(self, stream: t.Any):
        """Echo subprocess output to stdout."""
        for line in iter(stream.readline, ''):
            if re.search(":: Started ", str(line)):
                print("found startup trigger")
                self.startup_event.set()

            # print(f'echo> {line}')
            # sys.stdout.buffer.write(line)
            bs = bytes(line, encoding="UTF-8")
            sys.stdout.buffer.write(bs)
            sys.stdout.buffer.flush()

    async def __aenter__(self):
        print("In aenter")
        cmd = [self.fuseki_executable, "--verbose", "--update"]
        # If db_location is not specified, use a temporary directory
        if self.db_location is None:
            cmd.append("--mem")
        else:
            db_path = self.db_location
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            cmd.extend(["--loc", db_path])

        cmd.append("/ds")
        print(f"Running fuseki cmd {cmd}")

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Start a thread to echo the output
        self.thread = threading.Thread(target=self._echo_output, args=(self.process.stdout,))
        self.thread.start()
        # time.sleep(2)
        # startup_task = threading.create_task(waiter(self.startup_event))
        # await asyncio.sleep(0)
        print(f"Awaiting server startup")
        self.startup_event.wait()
        # await startup_task
        print(f"Server startup okay")

        return self


    async def __aexit__(self, exc_type, exc_value, traceback):
        print("In aexit")
        print(f"Server exiting")
        # Terminate the Fuseki server process
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.wait()

        # Wait for the output thread to finish
        print(f"Joining.. ")
        self.thread.join()
        print(f"Joined ")

        # Clean up the temporary directory if used
        if self.db_dir:
            self.db_dir.cleanup()

# class FusekiServerManager:
#     def __init__(self,
#                  fuseki_executable: str = 'fuseki-server',
#                  db_location: Optional[str] = None):
#         self.fuseki_executable = fuseki_executable
#         self.db_location = db_location
#         self.process = None
#         self.db_dir = None

#     def _echo_output(self, stream):
#         """Echo subprocess output to stdout."""
#         for line in iter(stream.readline, b''):
#             sys.stdout.buffer.write(line)
#             sys.stdout.buffer.flush()

#     def __enter__(self):
#         # If db_location is not specified, use a temporary directory
#         if self.db_location is None:
#             self.db_dir = tempfile.TemporaryDirectory()
#             db_path = self.db_dir.name
#         else:
#             db_path = self.db_location
#             if not os.path.exists(db_path):
#                 os.makedirs(db_path)

#         # Start the Fuseki server process
#         cmd = [self.fuseki_executable]
#         if self.db_location is None:
#             cmd.append('--mem')
#         else:
#             cmd.extend(['--loc', db_path])

#         self.process = subprocess.Popen(
#             cmd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             preexec_fn=os.setsid,
#             text=True,
#             bufsize=1,
#             universal_newlines=True
#         )

#         # Start a thread to echo the output
#         self.thread = threading.Thread(target=self._echo_output, args=(self.process.stdout,))
#         self.thread.start()

#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         # Terminate the Fuseki server process
#         if self.process:
#             os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
#             self.process.wait()

#         # Wait for the output thread to finish
#         self.thread.join()

#         # Clean up the temporary directory if used
#         if self.db_dir:
#             self.db_dir.cleanup()

# # Example usage:
# with FusekiServerManager() as manager:
#     # Perform operations with the server
#     pass
