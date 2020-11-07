from TODO_db import TODO_db

tdb = TODO_db()
print('''n:当前时间
n+,n-:与当前时间加减
+,-:与上次输入的时间加减''')
op = input('''请输入要进行的操作
1. 添加任务
2. 列出任务
3. 删除任务
4. 修改任务''')
if op == 1:
    start_str = input('开始时间:')
    
