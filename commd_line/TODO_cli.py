from time_input import Time_input

import sys
sys.path.append("..")
from sqlite_api.TODO_db import TODO_db

tdb = TODO_db()
ti = Time_input()
ti.print_help()
op = input('''请输入要进行的操作:
1. 添加任务
2. 列出任务
3. 删除任务
4. 修改任务
''')
if op == 1:
    start_str = input('开始时间:')
    
