Campus Wi-Fi Coding Lab 修订版

一 启动
建议使用Python 3.10或以上，需包含Tkinter。项目仅使用Python标准库，无需pip安装依赖。
请先解压整个文件夹，不要直接在压缩包内双击单个文件。

Windows：双击根目录Start_WiFi_Lab.bat；也可在该目录运行 py -3 main.py。
Mac：在终端进入解压后的目录，运行 python3 main.py。
Mac也提供Start_WiFi_Lab.command；若系统阻止双击或丢失执行权限，使用上面的终端命令即可。

启动菜单：
• Basic lab：原有TODO 1–2，距离平方与覆盖判定。
• Optimization lab：修订后的TODO 3–6，评分、分步搜索、调试与实验记录。

直接启动第三阶段：python3 main.py --advanced
直接启动基础阶段：python3 main.py --basic
若出现“没有tkinter”，先确认本机Python带有Tkinter；python3 -m tkinter可检查。
根目录原gui.py仍是旧参考展示界面，本次课堂应从main.py进入学生版本。

二 第三阶段课堂操作
1. Expressions：学生填写TODO 3、4、5，点击Run 49 expression tests。
2. Algorithm：选择Guided blocks，分别完成A合并覆盖、B计算得分、C更新最优；逐块测试。
   A和B各35个案例，C为6个案例。测试某一块时，其他输入由程序提供，不要求先完成所有块。
3. 三块通过后，点击Run & record my algorithm。程序将三块嵌入组合循环，调用学生自己的表达式。
   Preview assembled algorithm可查看拼接结果。Free coding保留独立草稿，允许完整编写函数体。
4. 顶部切换100/0、70/30、30/70。保留代码及历史记录，重新测试分块并运行算法。
5. Debug：先写预测、运行预置错误，修改代码后再测，填写修改原因并保存说明。
6. Evidence：比较不同方案，填写推荐理由，导出TXT。复制表格可粘贴到Word或电子表格。

运行记录只在当前会话内保留；关闭前导出。关闭时会提醒，但不自动保存草稿。
编辑器内写Python代码，说明与讨论可以用中文。为延续原版，程序界面保留英文。

三 学生代码与教师答案
学生编辑区默认保留空白任务或未完成框架，这不是程序故障。
teacher/reference_answers.py为教师参考，不由学生界面自动载入。
调试时可以用其中EXPRESSIONS、BLOCKS、FREE_ALGORITHM和DEBUG_REPAIRS核对结果。
不要将含参考答案和自动化测试的完整开发包直接当作无答案学生作业包。

GUI内的算法是“函数体”：不要粘贴def或import。
GUI提供MAX_COST、coverage_weight、cost_weight和数据字典；名称区分大小写。
student_cost、student_score、student_better使用学生在TODO 3–5中填写的表达式。
独立文件练习stage3/student_algorithm.py与GUI编辑器不自动同步；两种练习方式任选其一。

四 模型规则
固定7个候选点、12个教室代表检测点、恰好3台路由器、半径3。
每个教室检测点被任一所选路由器覆盖即计入，重叠部分只计一次。
不同候选点的安装成本不同；不涉及不同型号或容量。
综合分 = 覆盖权重 × 覆盖率 + 成本权重 × (1 − 总成本 / MAX_COST)。
MAX_COST=1100是当前三点组合的最大成本，用于归一化，不是预算约束。
权重之和为1；比例内部用0至1，界面再显示百分比。
达到最高综合分的所有同分合法方案均判为最优。不同权重的综合分不能直接用于跨情境排名。
人数、墙体、强弱信号、三维空间本轮未增加。

五 验证
在根目录运行 python3 run_tests.py；Windows也可用 py -3 run_tests.py。
54项自动化测试覆盖原模型、表达式、分块、算法、权重、调试、进程和界面状态控制。
完整输出在teacher/TEST_RESULTS.txt。
本次环境没有图形显示服务，未完成真实桌面上的窗口排版与鼠标点击实测。
首次上课前请按第六部分在实际展示电脑运行一遍。

六 上课前验收
□ 从main.py分别打开基础阶段与第三阶段。
□ 教师参考表达式通过基础阶段测试和第三阶段49项测试。
□ 分块A/B/C分别通过，完整算法返回合法方案。
□ 在100/0、70/30、30/70下重新运行，记录各方案及遗漏教室。
□ 调试练习先失败、修改后通过，导出含预测与修改原因的记录。
□ 修改代码与权重后，旧认证失效、原历史权重不被改写。
□ 在实际投影分辨率下确认所有标签页、滚动条和结果区可见。

七 整合包新增选做
从本目录运行python3 demand_extension.py --budget 750，使用当前成本与同学410人数据，固定3台；--csv results.csv可导出35方案。
主线run_tests.py仍运行54项；另运行python3 -m unittest -v test_demand_extension验证7项选做测试。此模块为命令行，不修改GUI。
