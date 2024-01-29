import os
import shutil
import sys
from subprocess import PIPE, Popen


NAME = "file-backup"


def popen(args):
    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)


def build_command():
    return [
        "pyinstaller -F -c --clean",
        "--distpath .",
        f"--name {NAME}",
        "-i src/shell32_172.ico",
        "--noupx",
        "--hidden-import src.backend.local",
        "--hidden-import src.backend.server",
        "--hidden-import src.backend.baidu",
        "--hidden-import src.strategy.compress",
        "--hidden-import src.strategy.increment",
        "--hidden-import src.backend.backend_cmd",
        "--hidden-import src.backup.backup_cmd",
        "--hidden-import src.console.console_cmd",
        "--hidden-import src.recover.recover_cmd",
        "main.py",
    ]


def build():
    p = popen("poetry about")
    p.communicate()
    POETRY = p.returncode == 0
    env_setup_cmd = (
        "poetry install --no-root" if POETRY else "pip install -r requirements.txt"
    )
    popen(env_setup_cmd).communicate()

    args = build_command()
    if POETRY:
        args.insert(0, "poetry run")
    build_cmd = " ".join(args)

    os.system(build_cmd)

    shutil.rmtree("build")
    os.remove(f"{NAME}.spec")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "actions":
        command = " ".join(build_command())
        print(command)
        os.system(command)
    else:
        build()
