import time,shutil,datetime,os,math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os_cope as oc
from PyQt5.QtCore import QThread,pyqtSignal
from queue import Queue
from D_C import *
import threading
# 设计思路是把监控和文件管理分开，防止文件处理时的卡顿
# 子进程打开watchdog，子进程自己处理关于文件处理，复制，备份等需要阻塞的动作
# 来防止watchdog在监控上的不及时，当文件发生改变再发给子进程处理
# 通过子进程再与主进程通信,进行显示和发送的工作
# 由于watchdog只能监控监控目录的文件，无法监控子目录里的文件，所以只能递归，文件管理也要改。。。
#
EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'
class Watch(QThread):
    """目前先只实现监控子文件的功能"""
    # 各个信号
    created = pyqtSignal(dict)
    deleted = pyqtSignal(dict)
    modified = pyqtSignal(dict)
    moved = pyqtSignal(dict)
    All = pyqtSignal(dict)
    def __init__(self,url,data) -> None:
        super(Watch,self).__init__()
        # 自己的基本信息
        self.data = data
        # 创建通讯queue
        self.q = Queue()
        # 初始化模型
        self.model = Dir_Watch()
        self.model.INIT(url)
        # 创建看门狗
        event_handler = MyHandler(self.q)
        self.observer = Observer()
        # 创建监控子线程，关闭递归
        self.observer.schedule(event_handler, path=url, recursive=False)
    def run(self) -> None:
        # 发送所有文件
        self.All_list_Send()
        # 开启看门狗
        self.observer.start()
        #开启监控循环
        while True:
            self.msleep(100)
            if not self.q.empty():
                event = self.q.get()
                # 直接抄的watchdog的源码
                _method_map = {
                    EVENT_TYPE_MODIFIED: self.on_modified,
                    EVENT_TYPE_MOVED: self.on_moved,
                    EVENT_TYPE_CREATED: self.on_created,
                    EVENT_TYPE_DELETED: self.on_deleted,
                }
                event_type = event.event_type
                if event.is_directory:
                    continue
                _method_map[event_type](event)
    def on_modified(self,event):
        # 先获取改变的文件名
        _,name,suffix = oc.get_file_all(event.src_path)
        file = self.model.FindFile(name+suffix)
        # 如果不为空就备份
        if file != None:
            print("{}备份一次".format(name+suffix))
            file.Backup()
    def on_moved(self,event):
        # 改名，移动，还是有很多种的
        _,name,suffix = oc.get_file_all(event.src_path)
        file = self.model.FindFile(name+suffix)
        if file != None:
            _, new_name, new_suffix = oc.get_file_all(event.dest_path)
            time.sleep(0.5)
            if os.path.exists(event.dest_path):
                print("修改文件名")
                file.name = new_name
                file.suffix = new_suffix
                file.Backup()
            else:
                print("啊啊啊啊啊")
                file.Backup()
    def on_created(self,event):
        # 添加一个文件
        time.sleep(0.5)
        if os.path.exists(event.src_path):
            print("添加一个文件{}".format(event.src_path))
            self.model.AddFile(event.src_path)
    def on_deleted(self,event):
        _, name, suffix = oc.get_file_all(event.src_path)
        if self.model.DelFile(name+suffix):
            print("删除一个文件{}".format(event.src_path))
    def All_list_Send(self):
        # 整理自己所有文件，打包成dict,分块发送
        dd = {
            "DirId":self.model.id,
            "DirName":self.model.name,
            "files":[]
        }
        n = len(self.model.files)
        pp = math.ceil(n/20)
        part = []
        for i in range(1,pp):
            part.append(self.model.files[(i-1)*20:i*20])
        part.append(self.model.files[(pp-1)*20:])
        for w in part:
            p = []
            for i in w:
                b = {
                "_id": i.id,
                "FileName": i.name,
                "suffix": i.suffix,
                "md5": i.md5,
                "belong_dir": self.model.id,
                "owner": self.data.get("id"),
                "end_time": i.EndBackupTime,
                }
                p.append(b)
            dd["files"] = p
            # 因为不知道python的变量管理机制，被坑惨了
            # 我无论怎么传递参数都不变，才发现是python的指针问题，喷血。。。不过也算是解决了
            self.All.emit(dd.copy())
        del dd
class MyHandler(FileSystemEventHandler):
    def __init__(self,queue:Queue):
        self.q = queue
    def on_any_event(self, event):
        self.q.put(event)
if __name__ == "__main__":
    w = Watch("C:\\Users\\Administrator\\Desktop")
    w.start()
    w.join()
