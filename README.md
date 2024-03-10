# file-backup

## 简介 / Introduction

一个简单的文件备份程序

## 运行方法 / Usage

> 在使用前，请确保你已经正确安装了 `Python 3.12`，并将其添加到 `PATH`。

<details>
<summary>使用 poetry 创建虚拟环境</summary>

> 在阅读前，请确保你已经安装了 `poetry` 包管理器:
>
> `pip install --upgrade poetry`

1. 下载源代码并解压，或使用 `git` 克隆此仓库。

```sh
git clone https://github.com/wyf7685/file-backup.git
cd file-backup
```

2. 使用 `poetry` 包管理器创建虚拟环境。

```sh
poetry install --no-root
```

3. 在虚拟环境中运行`main.py`。

```sh
poetry run python main.py
```

</details>

<details>
<summary>使用 pip 安装依赖</summary>

1. 下载源代码并解压，或使用 `git` 克隆此仓库。

```sh
git clone https://github.com/wyf7685/file-backup.git
cd file-backup
```

2. 使用 `pip` 安装依赖库。

```sh
pip install -r requirements.txt
```

1. 运行`main.py`。

```sh
python main.py
```

</details>

## 程序说明 / Description

见 [`程序说明`](./DESCRIPTION.md)

## 贡献者 / Contributors

![Contributors](https://contrib.rocks/image?repo=wyf7685/file-backup)
