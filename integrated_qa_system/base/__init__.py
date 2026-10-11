# 解决文件跨目录模块导入的问题

# 导包
import os
import sys

# 1. 获取当前文件所在目录的绝对路径
module_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 获取当前文件根目录的绝对路径
project_root = os.path.dirname(module_dir)

# 3. 将模块目录加入系统路径
# 解释：若模块目录不在sys.path中，插入到列表首位，确保优先加载当前模块目录下的文件，避免：同名模块冲突
if module_dir not in sys.path:
    sys.path.insert(0, module_dir)

# 4. 将项目根目录加入系统路径
# 解释：若项目根目录不在sys.path中，插入到列表首位，确保优先加载当前模块目录下的文件，避免：同名模块冲突
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 5. 扩展：调用并打印
# print(sys.path)

# 6. 导入自定义模块
from config import Config
from logger import logger
'''
在 Python 中，__init__.py 是一个特殊的模块文件，主要用于将一个普通目录标识为 Python 包（Package）。当导入该包时，这个文件中的代码会被自动执行。
它的核心作用与常见写法可以归纳为以下几个方面：
1. 标识 Python 包
作用：它的存在告诉 Python 解释器，当前目录应该被当作一个包来处理，而不是普通的文件夹。
写法：即使是一个完全空的文件，也能起到标识包的作用。
补充说明：从 Python 3.3 开始，引入了“命名空间包”的概念，即使没有 __init__.py，Python 也能识别包。
但为了兼容性以及让 pytest、mypy 等工具更好地识别项目结构，显式创建 __init__.py 依然是业界推荐的最佳实践。

. 执行包的初始化代码
作用：当包被首次导入时，__init__.py 中的代码会自动运行，适合用于包级别的初始化配置。
常见写法：
设置版本或全局常量：定义包的版本号或配置信息，方便外部访问。
__version__ = "1.0.0"
config = {"timeout": 30}
配置日志系统：统一设置包内模块的日志记录。
import logging
logging.basicConfig(level=logging.INFO)
执行必要的初始化逻辑：例如注册插件、检查运行环境等。

3. 控制导入行为与简化路径
作用：通过预先导入子模块或函数，可以简化外部的导入路径，让用户无需了解包的内部层级结构即可直接使用核心功能。
常见写法:
    # 将子模块中的核心函数提升到包级别
    from .module1 import func1
    from .module2 import func2
    
这样外部使用时只需 import mypackage，然后直接调用 mypackage.func1()，
而不需要写冗长的 mypackage.module1.func1()。


4. 定义包的公共接口（控制 import * 行为）
作用：通过定义 __all__ 变量，可以精确控制当外部使用 from package import * 时，哪些模块、类或函数会被暴露出去，从而隐藏内部实现细节，提升封装性。
常见写法：
    __all__ = ['func1', 'func2', 'MyClass']
    
如果不定义 __all__，import * 默认只会导入 __init__.py 中直接定义的名称。 
'''