def popen(args):
    from subprocess import Popen, PIPE

    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)


def build(name: str):
    import os
    import shutil

    p = popen("poetry about")
    p.communicate()
    POETRY = p.returncode == 0
    env_setup_cmd = "poetry install --no-root" if POETRY else "pip install -r requirements.txt"
    popen(env_setup_cmd).communicate()

    args = [
        "pyinstaller -F -c --clean",
        "--distpath .",
        f"--name {name}",
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
    if POETRY:
        args.insert(0, "poetry run")
    build_cmd = " ".join(args)

    os.system(build_cmd)

    shutil.rmtree("build")
    os.remove(f"{name}.spec")


if __name__ == "__main__":
    build("file-backup")
