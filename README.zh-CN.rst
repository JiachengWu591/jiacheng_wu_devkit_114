
.. image:: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/_static/jiacheng_wu_devkit_114-logo.png
    :target: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/

``jiacheng_wu_devkit_114`` 中文文档
==============================================================================

``devkit`` 是一个小巧的命令行工具箱,提供数据格式转换(JSON/YAML/CSV/PDF)、批量文件重命名与整理、
日志过滤与汇总三类功能。本文档是从零开始的完整用户指南:安装、一分钟快速上手,以及完整的命令参考。

English version: `README.rst <https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/blob/main/README.rst>`_


devkit 是什么
--------------------------------------------------------------

devkit 是一个小巧的通用命令行工具箱,并不是一套大而全的框架,而是把日常开发中经常用得到的三类实用功能打包进同一个命令里:数据格式转换(``convert``)、批量文件重命名与整理(``batch``),以及日志过滤与汇总(``log``)。不管你是想把一份 JSON 导出成 CSV,把杂乱的下载文件按类型或日期分类归档,还是想从几万行日志里迅速揪出报错和异常堆栈,devkit 都能帮你省去现场写脚本的功夫。它更像是一位开发者写给自己(以及愿意直接拿来用的其他人)的工具集——追求"装上就能用、命令好记、一分钟内看到效果",而不是覆盖所有边缘场景,因此特别适合日常运维、数据整理这类轻量场景下的个人或小团队使用。

安装
--------------------------------------------------------------

使用 pip 直接安装即可:

.. code-block:: console

    $ pip install jiacheng-wu-devkit-114

devkit 要求 Python 版本 ``>=3.10,<4.0`` (官方在 3.10 到 3.14 上都做过测试),安装前请确认本机 Python 版本落在这个区间内。

安装完成后,跑一下帮助命令,确认 CLI 已经可以正常调用:

.. code-block:: console

    $ devkit --help

如果一切正常,终端会打印出 devkit 的帮助文本,里面能看到 ``convert``、``batch``、``log`` 这三个子命令组的名字。只要看到这三个名字,就说明安装成功,可以继续往下走了。

上面这个基础安装已经覆盖了 ``convert data``、``batch``、``log`` 的全部功能,但**不包括** ``convert pdf2md``——PDF 转换依赖的一整套东西(``markitdown``、``pypdf`` 以及它们各自拉进来的依赖)相当重,所以把它做成了可选项,不是每个人都必须装。如果你需要用到它,装的时候加上 ``pdf`` 这个 extra:

.. code-block:: console

    $ pip install "jiacheng-wu-devkit-114[pdf]"

没装这个 extra 就跑 ``devkit convert pdf2md`` 会得到一条清楚的报错,提示你去装,不会甩出一堆看不懂的 Python 报错堆栈。

快速上手
--------------------------------------------------------------

下面用两个虚构的小例子,带你在安装完成后的一分钟内看到 devkit 的实际输出。

假设当前目录下有一个 ``users.json``,内容类似这样:

.. code-block:: json

    [
        {"name": "Alice", "address": {"city": "NY"}},
        {"name": "Bob", "address": {"city": "SF"}}
    ]

把它转换成 CSV 看看。因为里面有嵌套的 ``address`` 字段,需要额外加上 ``--flatten``:

.. code-block:: console

    $ devkit convert data users.json --to csv --flatten

结果会直接打印到终端,大致是这样:

.. code-block:: text

    name,address.city
    Alice,NY
    Bob,SF

再假设你手头还有一堆命名很乱的截图,比如 ``IMG_0001.jpg``、``IMG_0002.jpg`` 这种,想统一改成带序号的新文件名。先用 ``--dry-run`` 预览一下,这一步不会真正改动任何文件:

.. code-block:: console

    $ devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --dry-run

devkit 会把"重命名前 -> 重命名后"的完整清单打印出来(注意:devkit 打印的是每个文件的完整绝对路径,不是仅有文件名)。确认没问题之后,把 ``--dry-run`` 换成 ``--yes`` 就会真正执行。到这里,你已经用到了 devkit 两个不同的命令组,下面的"命令参考"会把每个子命令的全部选项讲清楚。

命令参考
--------------------------------------------------------------

devkit 的所有功能都挂在三个子命令组下面:``convert``、``batch``、``log``。下面按组逐一介绍每个子命令的作用、参数和示例。另外还有一个独立的第四个命令 ``devkit help``,可以跨这三个组一起搜索。

**devkit help —— 跨组搜索命令**

不带任何参数运行 ``devkit help``,会给三个组下面的每个子命令打印一行可以直接复制粘贴的命令格式;加上关键词 ``devkit help 关键词`` 就是搜索。每一行显示的是命令真实的参数签名(有哪些参数、哪些选项、默认值是什么),而不是一句描述——每个命令的文件参数统一显示成占位符 ``input``,``--output``/``-o`` 选项统一显示成 ``output``,这样每一行用的是同一套占位符,不会因为每个命令自己的参数名不一样(``input_file``、``logfile``、``src_dir`` 等)而看起来不统一。匹配的时候不区分大小写,而且不仅比对命令名,还会比对完整的帮助文本,所以即使关键词从没出现在组名里也能找到——比如 ``devkit help csv`` 能找到 ``devkit convert data`` (``csv`` 这个词从没出现在 "convert" 里),``devkit help traceback`` 能找到 ``devkit log filter``。

示例:

.. code-block:: console

    $ devkit help csv
    devkit convert data input --to <json|yaml|csv> [--output/-o output] [--flatten]

.. note::
   全局错误处理行为:如果给的路径本身在磁盘上就不存在(比如路径打错了),这是底层 CLI 框架(Typer/Click)自己的参数校验先挡下来的,devkit 自己的逻辑根本还没跑到——你会看到一个带边框的用法错误提示,进程退出码是 ``2``。而如果路径本身是存在的,但内容或选项让 devkit 自己的逻辑跑不通(比如格式不匹配、``--to csv`` 时有未展开的嵌套对象、``batch`` 计划出现冲突、``--pattern`` 正则不合法等),devkit 会打印一行红色的 ``Error: ...`` 到 stderr,并让进程以状态码 ``1`` 退出。这两种情况下都不会有任何文件被改动;要是遇到意外的程序内部 bug(不是可识别的输入问题),则会打印出完整的 Python 堆栈跟踪,不会被悄悄吞掉。

**devkit convert —— 格式转换**

``devkit convert data`` 用于在 JSON / YAML / CSV 之间互相转换:

.. code-block:: console

    $ devkit convert data INPUT_FILE --to {json|yaml|csv} [--output/-o PATH] [--flatten]

源格式由 ``INPUT_FILE`` 的后缀名自动识别(``.json``、``.yaml``/``.yml``、``.csv``),没有单独的参数可以覆盖这个判断,所以文件后缀一定要写对。

参数说明:

- ``--to``:必填,目标格式,取值为 ``json``、``yaml`` 或 ``csv``。
- ``--output``/``-o``:把转换结果写入指定文件,不给的话直接打印到标准输出。
- ``--flatten``:仅在目标格式是 ``csv`` 且记录里含有嵌套对象(比如 ``{"address": {"city": "NY"}}``)时才有意义——加上它会把嵌套键展开成用点连接的列名,例如 ``address.city``,而不是直接报错;对 ``json``/``yaml`` 目标完全不起作用,加不加都一样。

几点需要留意的行为:

- CSV 的读写全部按"扁平字符串字段"处理,不做任何类型推断——数字、布尔值进出 CSV 都会变成字符串。
- 转成 csv 又没加 ``--flatten`` 时,只要任意一条记录里有嵌套对象字段,就会直接报错,并明确指出是哪些记录、哪些字段出了问题,同时提示你加上 ``--flatten`` 或者换一个非 csv 的目标格式。
- 一个已知的局限:即便加了 ``--flatten``,记录里的列表(list)值也不会被展开成多列,而是整体做 JSON 编码后塞进单个单元格;只有嵌套的字典(dict)才会被点号展开。
- 写 csv 时,表头是所有记录里出现过的键的并集;某条记录缺哪个键,对应单元格就留空。
- JSON 输出统一用 2 个空格缩进,非 ASCII 字符保持原样,不会被转义成 ``\uXXXX``。
- YAML 输出同样允许直接写 Unicode 字符,并且保留源数据里的键顺序,不会按字母重新排序。

示例:

.. code-block:: console

    $ devkit convert data users.json --to csv
    $ devkit convert data users.json --to csv --flatten
    $ devkit convert data config.yaml --to json -o config.json

``devkit convert pdf2md`` 用于把 PDF 转成 Markdown 文本。需要先装 ``pdf`` 这个 extra——``pip install "jiacheng-wu-devkit-114[pdf]"``,见前面的"安装"一节:

.. code-block:: console

    $ devkit convert pdf2md INPUT_FILE [--output/-o PATH] [--pages "1-5" 或 "1,3,7-9"]

底层使用 MIT 协议的 ``markitdown`` 库做转换,全程只用 CPU 计算。对于多栏排版或复杂表格,转换结果只是"尽力而为",不保证排版完全还原。

参数说明:

- ``--output``/``-o``:把转换结果写入指定文件,不给的话直接打印到标准输出。
- ``--pages``:可选,按 1 起始的页码选择要转换的页面,支持单个区间如 ``"1-5"``、逗号分隔的列表如 ``"1,3,7"``,也支持两者混用如 ``"1,3,7-9"``;不传则转换整份文档。

以下情况会报错:找不到输入文件、输入文件不是以 ``.pdf`` 结尾,或者 ``--pages`` 里指定的页码超出了文档实际页数。

示例:

.. code-block:: console

    $ devkit convert pdf2md report.pdf -o report.md
    $ devkit convert pdf2md report.pdf --pages 1-3

**devkit batch —— 批量重命名与整理**

``batch`` 下的两个子命令(``rename`` 和 ``organize``)共享同一套安全机制——先打印完整的迁移计划,再检查冲突,最后才会询问确认。这套机制的完整细节(以及一个关于 ``--dry-run`` 的重要提醒)放在下面的"安全提示与建议"一节详细讲,这里先看两个子命令本身怎么用。

``devkit batch rename`` 按模板批量重命名匹配到的文件:

.. code-block:: console

    $ devkit batch rename PATTERN --template TEMPLATE [--dry-run] [--yes/-y]

参数说明:

- ``PATTERN``:glob 匹配模式,支持 ``**`` 递归匹配,例如 ``"*.jpg"`` 或 ``"reports/**/*.pdf"``。务必给它加上引号,原因见"安全提示与建议"一节。
- ``--template``:必填,重命名的目标文件名模板,使用 Python 的 ``str.format`` 语法,可用字段有:

  - ``{seq}``:文件在匹配结果中的序号(从 1 开始),支持格式说明符,比如 ``{seq:03d}`` 会补零成 3 位(001、002……)。
  - ``{stem}``:不含扩展名的文件名。
  - ``{ext}``:带前导点的扩展名(例如 ``.jpg``),文件没有扩展名时为空字符串。
  - ``{name}``:原始文件名(含扩展名)。
  - ``{parent}``:文件所在父目录的目录名本身,而不是完整路径。

  模板里如果用了不认识的字段名,或者格式说明符写错了,命令会在真正重命名任何文件之前就直接报错。
- ``--dry-run``:只打印重命名计划就退出,不会改动任何文件。这一步依然会跑下面说的完整冲突检查,所以 ``--dry-run`` 下看起来没问题的计划,真正执行时也一定没问题。
- ``--yes``/``-y``:跳过交互式确认,直接执行(冲突检查依然会先跑一遍,不受这个选项影响)。

匹配到的文件会先按路径排序,以保证编号是确定、可重复的,然后才从 1 开始编号。重命名是"原地"进行的——文件仍留在原来的目录里,只是文件名变了。

示例:

.. code-block:: console

    $ devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --dry-run
    $ devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --yes

``devkit batch organize`` 把 ``SRC_DIR`` 下的文件按扩展名或修改时间归类到子文件夹里:

.. code-block:: console

    $ devkit batch organize SRC_DIR [--by ext|mtime] [--dest PATH] [--date-format "%Y-%m"] [--recursive] [--dry-run] [--yes/-y]

``SRC_DIR`` 必须是已经存在的目录。参数说明:

- ``--by``:归类方式,``ext`` (默认)或 ``mtime``。

  - ``ext``:按扩展名归类,子文件夹名是小写、去掉点号的扩展名(比如 ``.JPG`` 和 ``.jpg`` 都会归到名为 ``jpg`` 的文件夹);没有扩展名的文件归到 ``no_ext`` 文件夹。
  - ``mtime``:按文件最后修改时间归类,子文件夹名由 ``--date-format`` 指定的 strftime 格式生成。
- ``--dest``:文件最终被移动到的根目录;不指定时默认就是 ``SRC_DIR`` 本身,效果相当于 ``SRC_DIR/<分类文件夹>/<原文件名>``。
- ``--date-format``:仅在 ``--by mtime`` 时生效的 strftime 格式,默认是 ``"%Y-%m"`` (比如 ``"2026-08"``)。
- ``--recursive``:默认只处理 ``SRC_DIR`` 直属的文件——已经被上一次运行归类进子文件夹的文件不会被再次处理,所以重复运行是安全的。加上这个选项后,``SRC_DIR`` 子目录里的文件也会被一并处理。
- ``--dry-run``:只打印移动计划就退出,不会改动任何文件。跟 ``rename`` 一样,这一步依然会跑完整冲突检查,所以 ``--dry-run`` 下没问题的话真正执行也一定没问题。
- ``--yes``/``-y``:跳过交互式确认,直接执行。

示例:

.. code-block:: console

    $ devkit batch organize ./Downloads --by ext --dry-run
    $ devkit batch organize ./Downloads --by mtime --date-format "%Y-%m" --yes

**devkit log —— 日志过滤与统计**

devkit 默认按下面的规则解析日志行:一行以形如 ``YYYY-MM-DD`` (日期和时间之间用空格或 ``T`` 分隔) ``HH:MM:SS`` (可以带 ``.###`` 或 ``,###`` 形式的毫秒)开头的时间戳,后面跟一段空白,然后是**大写**的日志级别 ``DEBUG``/``INFO``/``WARNING``/``WARN``/``ERROR``/``CRITICAL``,再跟一段空白,剩下部分作为消息正文。比如下面这一行就能被正确识别:

.. code-block:: text

    2026-08-07 10:01:12 ERROR Database connection timeout

.. note::
   默认的解析规则只认**大写**的级别单词。像 ``2026-08-07 10:01:12 error Database connection timeout`` 这种小写 ``error`` 的行是**不会**被识别成一条记录的——它会被悄悄当成前一条记录的续行吞掉(如果它是文件里第一行,就会被归进开头那个 ``UNKNOWN`` 合成记录里)。如果你的日志级别是小写或大小写混用的,请用 ``--pattern`` 传一个带大小写不敏感标记的自定义正则(比如在正则前面加上 ``(?i)``)。

不符合这个格式的行不会被丢弃,也不会报错,而是被当作上一条已识别记录的续行追加进去——这正是多行堆栈跟踪(traceback)能够正确附着在触发它的那条日志上的原因。如果文件最开头就出现了不符合格式的行(此时还没有任何已识别记录),这些行会被合并成一条级别为 ``UNKNOWN`` 的合成记录。日志文件按 UTF-8 读取,如果开头带有 BOM(常见于 Windows 编辑器保存的文件),也会被自动兼容处理。

``filter`` 和 ``stats`` 两个子命令都支持通过 ``--pattern`` 传入自定义正则表达式来替代默认解析规则,但这个正则必须包含三个命名捕获组:``timestamp``、``level``、``message``。如果正则本身写错了,或者缺了这三个命名组中的任何一个,命令会立刻报错。

``devkit log filter`` 按条件筛选日志条目:

.. code-block:: console

    $ devkit log filter LOGFILE [--level LEVEL]... [--keyword TEXT] [--since "YYYY-MM-DD[ HH:MM:SS]"] [--until 同上格式] [--pattern REGEX] [--output/-o PATH]

参数说明:

- ``--level``:可重复传入(比如 ``--level ERROR --level CRITICAL``),保留匹配其中任意一个级别的条目(多个级别之间是"或"关系);这个比较本身是大小写不敏感的——但请注意,这跟上面提到的"默认解析规则只认大写"是两件不同的事:``--level`` 只能筛选那些已经被成功识别成一条记录的条目,如果一行日志因为级别是小写而没被识别(变成了续行或 ``UNKNOWN``),``--level`` 也救不回它。不传 ``--level`` 则保留所有级别。
- ``--keyword``:大小写不敏感的子串匹配,匹配范围是整条记录的完整文本,包括后面追加的多行续行(比如 traceback),不只是第一行。
- ``--since``/``--until``:时间范围的两端(都是闭区间),格式是 ``YYYY-MM-DD`` 或 ``YYYY-MM-DD HH:MM:SS``。只要传了 ``--since`` 或 ``--until`` 中的任意一个,所有时间戳解析失败的条目(包括开头那条 ``UNKNOWN`` 级别的合成记录)都会被自动排除,因为它们没法参与范围比较。
- ``--pattern``:自定义解析正则,见上面的说明。
- ``--output``/``-o``:把筛选结果写入指定文件,不给的话直接打印到标准输出。

以上筛选条件如果同时给出多个,是"与"(AND)关系——一条记录必须同时满足你传入的每一个条件才会被保留。

示例:

.. code-block:: console

    $ devkit log filter app.log --level ERROR --level CRITICAL
    $ devkit log filter app.log --keyword timeout --since "2026-08-07 10:00:00"

``devkit log stats`` 对日志做汇总统计:

.. code-block:: console

    $ devkit log stats LOGFILE [--group-by level] [--top-n 10] [--pattern REGEX] [--json]

参数说明:

- ``--group-by``:目前只支持 ``level`` (也是默认值),按日志级别分组统计。
- ``--top-n``:每个级别里展示出现频率最高的前几条"首行消息",默认 10。
- ``--pattern``:自定义解析正则,见上面的说明。
- ``--json``:输出单个机器可读的 JSON 对象,结构形如 ``{"level_counts": {LEVEL: count, ...}, "top_messages": {LEVEL: [[message, count], ...], ...}}``,取代人类可读的文字摘要;需要写脚本处理结果,或者要把结果接给下游工具/AI agent 时,推荐加上这个选项。

不加 ``--json`` 时,输出是人类可读的文字摘要:先是每个级别一行的 ``LEVEL: count`` (按级别名字母顺序排列),然后每个级别各附一段"Top messages for LEVEL:",列出该级别里最常见的消息及出现次数。

示例:

.. code-block:: console

    $ devkit log stats app.log
    $ devkit log stats app.log --top-n 5 --json

安全提示与建议
--------------------------------------------------------------

- **batch 的安全机制分三步,``--dry-run`` 只跳过第三步。** ``batch`` 的两个子命令(``rename``、``organize``)在改动任何文件之前会依次做三件事:第一步,把完整的"旧路径 -> 新路径"迁移计划打印出来(用的是每个文件的完整绝对路径),这一步哪怕加了 ``--dry-run`` 也照常执行;第二步,对这份计划做冲突检查——如果发现两个文件会被移到同一个目标位置,或者某个目标路径已经存在于磁盘上且并非本次计划自己要移动的源文件,命令会直接拒绝执行,不做任何改动(哪怕只有一处冲突,也不会部分执行),**这一步同样在 ``--dry-run`` 下也会执行**,所以 ``--dry-run`` 下看起来"干净"的计划,就是真的没问题,正式执行也一定会成功;第三步,只要没有加 ``--dry-run`` 或 ``--yes``/``-y``,命令会用交互式提示(类似 "Rename N file(s)?" / "Move N file(s)?")等你确认,只有回答"是"才会真正动手——这是三步里唯一一个 ``--dry-run`` 会跳过的步骤。
- **在脚本、CI、AI agent 里跑批处理命令,一定要带 ``--yes``。** 在这些非交互式环境里,如果不加 ``--yes`` (或 ``-y``),上面第三步的交互式确认提示会一直卡在等待标准输入,永远不会返回。
- **给 glob 模式加引号。** 命令行里用到 glob 模式的地方(比如 ``devkit batch rename`` 的 ``PATTERN``),记得给它加上引号,写成 ``"*.jpg"`` 而不是裸的 ``*.jpg``。devkit 在 Windows 上特意关掉了 Click 自带的 glob 自动展开(内部设置 ``windows_expand_args=False``),就是为了让 ``*.jpg`` 这类模式原样传给 devkit 自己的递归 glob 逻辑去处理,而不是先被终端展开成一堆具体文件名。所以不管在哪个操作系统上用,统一加引号才能保证 shell 把模式原样传进去,不会自己抢先展开。
- **退出码可以用来判断脚本里的成败。** 如果给的路径本身就不存在,是 Typer/Click 框架自己的参数校验挡下来的,退出码是 ``2``,不会走 devkit 自己的红色错误提示;路径存在但内容/选项有问题(格式不匹配、冲突、正则不合法等)时,devkit 才会打印红色的 ``Error: ...`` 并以状态码 ``1`` 退出。这两种情况都不会改动任何文件。

贡献者指南
--------------------------------------------------------------

如果你想参与 devkit 本身的开发,本地开发流程基于 ``mise`` + ``uv``:``mise run inst`` 安装依赖,``mise run test`` 跑单元测试,``mise run cov`` 生成带 HTML 覆盖率报告的测试结果,``mise run build-doc`` 构建 Sphinx 文档。更多任务细节可以直接查看仓库里的 ``mise.toml``。
