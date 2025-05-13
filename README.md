# mca Reader
读取并遍历所有.mca文件，统计特定高度范围的各个方块的类型及其对应的数量，并导出Excel表格。
# mca Mover
与mca Reader配套的工具（可选），其作用是将已经处理好的.mca移动到同目录下processed_mca文件夹以便区分，不常用。

# 注意事项：
要在新电脑上成功运行这段代码，需要准备以下 Python 环境和依赖：
1. 安装 Python 环境
Python 3.7+（推荐 3.9 或更高版本）
从 Python 官网 下载并安装，安装时勾选 “Add Python to PATH”。
2. 安装依赖包
代码依赖以下第三方库，需使用 pip 安装：

bash
pip install mca openpyxl psutil

mca：用于解析 Minecraft 的 .mca 区域文件。
openpyxl：用于生成和操作 Excel 文件（.xlsx）。
psutil：用于监控系统内存和进程。
3. 检查系统依赖
Windows 系统：
代码中的高 DPI 支持需要 Windows API，确保运行环境为 Windows。
Minecraft 世界路径：
确保 MCA_DIRECTORY 路径指向有效 Minecraft 世界的 region 文件夹，否则会找不到 .mca 文件。
4. 验证环境配置
安装完成后，通过以下命令验证依赖是否正确安装：

bash
python -c "import mca; import openpyxl; import psutil; print('依赖安装成功')"
5. 可选优化
调整配置参数：
根据电脑性能修改代码开头的配置参数：
python
运行
# 建议降低内存限制（默认100%可能导致系统卡顿）
MAX_MEMORY_USAGE_PERCENT = 70  # 根据内存大小调整（60-80%为宜）

# 限制最大进程数（避免过多进程导致系统过载）
MAX_WORKERS = 8  # 根据CPU核心数调整



常见问题及解决方法
缺少依赖错误：
若提示 ModuleNotFoundError，检查是否正确安装所有依赖包。
权限问题：
确保 Python 有读写 progress.json 和输出 Excel 文件的权限。
高 DPI 支持失效：
若 Windows 上 UI 仍模糊，尝试以管理员身份运行程序。
内存溢出：
降低 MAX_MEMORY_USAGE_PERCENT 值（如 60%），并减少 MAX_WORKERS。
