#!/usr/bin/env python3

import os, serial, posix


# Create a pySerial port and a binary file linked to a PTY (simulated
# serial cable).
def sim_serial():
    fd1, fd2 = posix.openpty()
    fd_file = os.fdopen(fd1, "wb")
    serial_port = serial.Serial(os.ttyname(fd2), 115200)
    os.close(fd2)

    return fd_file, serial_port


if __name__ == "__main__":
    fd_file, serial_port = sim_serial()
    fd_file.write(b'This is a test.\n')
    fd_file.flush()
    print(serial_port.read_until(b'\n'))
