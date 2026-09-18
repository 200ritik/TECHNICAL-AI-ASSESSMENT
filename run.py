import subprocess
import sys
import time


def main():

    api = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000"
        ]
    )

    time.sleep(3)

    ui = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "ui/app.py"
        ]
    )

    try:

        api.wait()

    except KeyboardInterrupt:

        api.terminate()
        ui.terminate()


if __name__ == "__main__":
    main()