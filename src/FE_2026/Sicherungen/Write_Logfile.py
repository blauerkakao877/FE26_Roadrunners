import time
from datetime import datetime
import os
import threading


class Logwriter:
    def __init__(self):
        self.folder = "/home/pi/FE_2026/Logs/"
        os.makedirs(self.folder, exist_ok=True)

        self.filename = os.path.join(
            self.folder,
            f"Logfile_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.dat"
        )

        self.logging = False
        self.myfile = None
        self.lock = threading.Lock()

    def write_Log(self, line):
        if self.logging and self.myfile:
            with self.lock:
                logline = (
                    datetime.now().strftime('%H:%M:%S.%f')
                    + " "
                    + str(line)
                    + "\n"
                )

                self.myfile.write(logline)
                self.myfile.flush()
                os.fsync(self.myfile.fileno())

                print(logline, end="")

    def open_Log(self, start_Log):
        if start_Log:
            self.myfile = open(
                self.filename,
                "w",
                encoding="utf-8"
            )
            self.logging = True

    def close_Log(self):
        if self.myfile:
            self.myfile.close()
            self.myfile = None
            self.logging = False