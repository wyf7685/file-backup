def popen(args):
    from subprocess import Popen, PIPE

    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)


def build(name: str):
    import os
    import shutil

    p = popen("poetry")
    p.communicate()
    POETRY = p.returncode == 0
    env_setup_cmd = "poetry install" if POETRY else "pip install -r requirements.txt"
    popen(env_setup_cmd).communicate()

    args = [
        "pyinstaller -F -c --clean",
        "--distpath .",
        f"--name {name}",
        "-i src/shell32_172.ico",
        "--hidden-import src.backend.local",
        "--hidden-import src.backend.server",
        "--hidden-import src.backend.baidu",
        "--noupx",
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
