import os
import shutil
import sys
from subprocess import PIPE, Popen

NAME = "file-backup"


def popen(args: str):
    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)


def build_command(poetry: bool = False, dist: str = "."):
    return [
        "python -m",
        "poetry run" if poetry else "",
        "pyinstaller -F -c --clean",
        f"--distpath {dist}",
        f"--name {NAME}",
        "-i src/shell32_172.ico",
        "--noupx",
        "--hidden-import src.backend.local",
        "--hidden-import src.backend.server",
        "--hidden-import src.backend.baidu",
        "--hidden-import src.backend.tx_cos",
        "--hidden-import src.strategy.compress",
        "--hidden-import src.strategy.increment",
        "--hidden-import src.backend.backend_cmd",
        "--hidden-import src.backup.backup_cmd",
        "--hidden-import src.console.console_cmd",
        "--hidden-import src.recover.recover_cmd",
        "main.py",
    ]


def build_actions():
    command = " ".join(build_command(True, "dist"))
    print(command)
    os.system(command)


def build():
    p = popen("poetry about")
    p.communicate()
    POETRY = p.returncode == 0
    env_setup_cmd = (
        "poetry install --no-root" if POETRY else "pip install -r requirements.txt"
    )
    popen(env_setup_cmd).communicate()

    build_cmd = " ".join(build_command(poetry=POETRY))

    os.system(build_cmd)

    shutil.rmtree("build")
    os.remove(f"{NAME}.spec")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "actions":
        build_actions()
    else:
        build()
