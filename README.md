# ShiroShare

预想的功能是把分享的文件夹同步到其他电脑上，其他电脑上的人要是修改的话还可以同步到本地，有点类似于微软的脱机文件吧，不过我想实现的的功能主要是往局域网网盘的方向靠近，局域网内大家都是主机，可以保证数据不会丢失，但是也会出现安全和储存问题，考虑到使用的环境，是在办公室内的局域网，分享的文件也多是文档类的文件，这些问题也可以暂时忽略了，

# main_ui.py main_window.py
ui文件就是主界面的ui啦，main_window继承ui文件来构建的主界面，

# D_C.py
这个是自己写的文件管理模型，监控文件的模型，ui文件的模型，都写在里面

# os_cope.py
这个是自己包装的一些关于系统处理方面的函数

# watch.py
这个当然就是监控文件的主程序啦，详细的监控进程我都写进去了

# 其他
剩下的大部分都是测试文件了，因为现在还没写完。。。。
说实话现在遇到了障碍，就是文件系统问题。。我是先写的文件模型，预想的是通过watchdog监控文件改变，然后改变模型内的文件，并备份到备份文件内