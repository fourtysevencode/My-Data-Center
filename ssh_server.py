
import fcntl
import os
import pty
import select
import signal
import socket
import struct
import subprocess
import sys
import termios
import threading

import paramiko

HOST = "localhost"
PORT = 2222
HOST_KEY_FILE = "host_key"
GAME_SCRIPT = os.path.abspath("game.py")


class GameServer(paramiko.ServerInterface):
    def __init__(self):
        self.shell_requested = threading.Event()
        self.width = 80
        self.height = 24
        self.term = "xterm-256color"

    def get_allowed_auths(self, username):
        return "none"

    def check_auth_none(self, username):
        # The game handles its own account registration and login.
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(
        self, channel, term, width, height,
        pixelwidth, pixelheight, modes
    ):
        self.term = term.decode() if isinstance(term, bytes) else term
        self.width = max(1, width)
        self.height = max(1, height)
        return True

    def check_channel_shell_request(self, channel):
        self.shell_requested.set()
        return True

    def check_channel_window_change_request(
        self, channel, width, height, pixelwidth, pixelheight
    ):
        self.width = max(1, width)
        self.height = max(1, height)
        return True


def handle_client(client, address, host_key):
    transport = None
    channel = None
    master_fd = None
    slave_fd = None
    process = None

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)

        server = GameServer()
        transport.start_server(server=server)

        channel = transport.accept(30)
        if channel is None:
            return

        if not server.shell_requested.wait(30):
            return

        # Create a separate terminal for this player.
        master_fd, slave_fd = pty.openpty()

        def resize_terminal():
            size = struct.pack(
                "HHHH",
                server.height,
                server.width,
                0,
                0,
            )
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)

        resize_terminal()

        env = os.environ.copy()
        env["TERM"] = server.term

        process = subprocess.Popen(
            [sys.executable, GAME_SCRIPT],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            cwd=os.path.dirname(GAME_SCRIPT),
            env=env,
            close_fds=True,
            start_new_session=True,
        )

        os.close(slave_fd)
        slave_fd = None

        channel.sendall(b"\x1b[2J\x1b[H")

        while not channel.closed and process.poll() is None:
            resize_terminal()

            readable, _, _ = select.select(
                [channel, master_fd], [], [], 0.1
            )

            if channel in readable:
                data = channel.recv(4096)
                if not data:
                    break
                os.write(master_fd, data)

            if master_fd in readable:
                try:
                    data = os.read(master_fd, 4096)
                    if not data:
                        break
                    channel.sendall(data)
                except OSError:
                    break

    except Exception as exc:
        print(f"Session {address}: {exc}")

    finally:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=3)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                process.kill()
                process.wait()

        for fd in (master_fd, slave_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass

        if channel is not None:
            channel.close()
        if transport is not None:
            transport.close()
        client.close()


def main():
    host_key = paramiko.Ed25519Key.from_private_key_file(
        HOST_KEY_FILE
    )

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(50)

    print(f"Terminal Tycoon listening on port {PORT}")

    try:
        while True:
            client, address = sock.accept()
            threading.Thread(
                target=handle_client,
                args=(client, address, host_key),
                daemon=True,
            ).start()
    finally:
        sock.close()


if __name__ == "__main__":
    main()
