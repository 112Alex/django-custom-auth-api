import socket
import time
import os
import sys

host = os.environ.get("POSTGRES_HOST")
port = int(os.environ.get("POSTGRES_PORT"))
timeout = 1

def wait_for_db():
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                sys.stdout.write("Database is ready!\n")
                break
        except (socket.timeout, ConnectionRefusedError):
            sys.stdout.write("Database is not ready yet, waiting...\n")
            time.sleep(1)
        if time.time() - start_time > 60:
            sys.stderr.write("Timeout waiting for database.\n")
            sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
