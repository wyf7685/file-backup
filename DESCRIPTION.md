# `file-backup` 程序说明

咕咕咕

- `main.py`

  主程序文件，程序入口。

- `src/backend/`

  文件操作实现，将 `local` 、 `server` 等多个不同备份方式抽象为统一的 `Backend` 类对象。

  - `config.py`

    从全局配置中解析 `Backend` 相关的配置。

  - `backend.py`

    `Backend` 抽象类。

  - `local/` `server/` `...`

    `Backend` 类的实现。

- `src/backup/`

  - `backup.py`

    处理备份任务。

  - `backup_host.py`

    在后台定时执行备份任务。

  - `backup_cmd.py`

    注册备份相关的控制台命令。

- `src/config/`

  - `config_model.py`

    继承 `pydantic.BaseModel` 定义 `ConfigModel` 类，实现配置文件的读取写入操作。

    `parse_config` 方法实现动态构造配置类，解析配置文件。

  - `config.py`

    默认的全局配置对象。

- `src/console/`

  - `console.py`

    定义 `Console` 类，注册并处理控制台命令。

    <details>
    <summary>命令注册示例</summary>

    ```py
    from typing import List

    from src.console import Console

    @Console.register("foo", alias=["bar"])
    async def _(args: List[str]):
        Console.check_arg_length(args, 3)
        Console.logger.info(", ".join(args))
    ```

    </details>

  - `input_queue.py`

    定义 `InputQueue` ，在独立线程处理控制台输入。

  - `console_cmd.py`

    注册默认控制台命令。

- `src/const/`

  - `__init__.py`

    定义程序中的常量。

  - `path.py`

    定义程序中使用的路径常量。

    <details>
    <summary>路径常量使用方法</summary>

    ```py
    from src.const import PATH
    # 缓存目录
    cache = PATH.CACHE / "my_cache_key"
    ```

    </details>

  - `exceptions.py`

    继承 `Exception` 创建 `Error` 类，作为程序中所有自定义异常的基类。

    继承 `Error` 类创建多种异常类型，用于程序内部抛出和捕获。

- `src/recover/`

  - `recover.py`

    处理恢复任务。

  - `recover_cmd.py`

    注册恢复相关的控制台命令。

- `src/strategy/`

  - `strategy.py`
    
    定义 `BaseStrategy` 抽象类，处理备份和恢复的具体逻辑。

    继承 `BaseStrategy` 定义 `Strategy` 抽象类，实现备份记录处理逻辑和一些共用代码。

  - `protocol.py`

    定义 `StrategyProtocol` 协议供外部引用，可使用 `isinstance` 检查是否实现 `Strategy` 相关函数。

  - `increment/` `compress/` `...`
    
    备份恢复具体逻辑的实现。

- `src/utils/`

  程序中使用到的各种函数。

  - `utils.py`

    一些常用且方便的函数。

  - `typed_queue.py`

    继承 `queue.Queue` 类实现的同名类，不改变执行逻辑，添加了泛型类型注解支持。

  - `log_style.py`

    定义 `StyleInt` ，用于处理 `loguru` 日志的着色。

    <details>
    <summary>使用示例</summary>

    ```py
    from src.log import get_logger
    from src.utils import Style

    logger = get_logger("Test").opt(colors=True)
    logger.info(f"{Style.YELLOW("Yellow Text")} and {(Style.CYAN | Style.UNDERLINE)("Cyan Underline Text")}")
    ```

    </details>

  - `ansi_html.py`

    [`实验性功能`] 不建议使用

    继承 `colorama` 模块的 `AnsiToWin32` 类，定义 `AnsiToHtml` 类，将其中调用 win32 api 的部分替换为输出 html 标签，实现 ansi控制符 转 html文本。

    附带将日志以html格式输出的功能，可通过修改配置文件开启。

- `src/log.py`

  自定义 `loguru` 模块的日志格式。

- `src/models.py`

  使用 `pydantic` 的 `BaseModel` 创建模型，结构化处理备份记录。

- `src/shell32_172.ico`

  编译后 exe 文件的图标
