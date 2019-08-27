import math
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import QThread,pyqtSignal
from queue import Queue
from core.model import *
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
class Watch(threading.Thread):
    """目前先只实现监控子文件的功能"""
    def __init__(self,url,queue) -> None:
        super(Watch,self).__init__()
        # 创建通讯queue
        # 跟父进程通信
        self.Queue = queue
        # 和子进程通信
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
            time.sleep(0.1)
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
            w = file.Backup()
            if w != None:
                self.Queue.put({
                    "type":"MODI_FILE",
                                    "data": {
                    "_id": w.id,
                    "FileName": w.name,
                    "suffix": w.suffix,
                    "md5": w.md5,
                    "belong_dir": self.model.id,
                    "end_time": w.EndBackupTime
                },
                    "DirId": self.model.id,
                })

    def on_moved(self,event):
        # 改名，移动，还是有很多种的
        _,name,suffix = oc.get_file_all(event.src_path)
        file = self.model.FindFile(name+suffix)
        if file != None:
            _, new_name, new_suffix = oc.get_file_all(event.dest_path)
            time.sleep(0.5)
            if os.path.exists(event.dest_path):
                # word类文件的自动保存
                file.name = new_name
                file.suffix = new_suffix
                w = file.Backup()
                self.Queue.put({
                    "type":"MODI_FILE",
                                    "data": {
                    "_id": w.id,
                    "FileName": w.name,
                    "suffix": w.suffix,
                    "md5": w.md5,
                    "belong_dir": self.model.id,
                    "end_time": w.EndBackupTime
                },
                    "DirId": self.model.id,
                })
            else:
                # 改名
                w = file.Backup()
                self.Queue.put({
                    "type":"MODI_FILE",
                "data": {
                    "_id": w.id,
                    "FileName": w.name,
                    "suffix": w.suffix,
                    "md5": w.md5,
                    "belong_dir": self.model.id,
                    "end_time": w.EndBackupTime
                },
                    "DirId": self.model.id,
                })
    def on_created(self,event):
        # 添加一个文件
        time.sleep(0.5)
        if os.path.exists(event.src_path):
            w = self.model.AddFile(event.src_path)
            self.Queue.put({
                "type": "ADD_FILE",
                "data": {
                    "_id": w.id,
                    "FileName": w.name,
                    "suffix": w.suffix,
                    "md5": w.md5,
                    "belong_dir": self.model.id,
                    "end_time": w.EndBackupTime
                },
                "DirId": self.model.id,
            })
    def on_deleted(self,event):
        _, name, suffix = oc.get_file_all(event.src_path)
        w = self.model.DelFile(name+suffix)
        if w:
            self.Queue.put({
                "type": "DEL_FILE",
                "data": w,
                "DirId":self.model.id,
            })
    def search(self,fileid):
        # 通过id返回备份的文件
        return self.model.search(fileid)
    def All_list_Send(self):
        # 整理自己所有文件，打包成dict,分块发送
        dd = {
            "DirId":self.model.id,
            "DirName":self.model.name,
            "Files":[]
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
                "end_time": i.EndBackupTime
                }
                p.append(b)
            dd["Files"] = p
            # 因为不知道python的变量管理机制，被坑惨了
            # 我无论怎么传递参数都不变，才发现是python的指针问题，喷血。。。不过也算是解决了
            self.Queue.put({
                "type":"All_list",
                "data":dd,
                "DirId":self.model.id,
            })
class MyHandler(FileSystemEventHandler):
    def __init__(self,queue:Queue):
        self.q = queue
    def on_any_event(self, event):
        self.q.put(event)
if __name__ == "__main__":
    print(os.getpid())
    w = Watch("C:\\Users\\Administrator\\Desktop",Queue())
    w.start()
    w.Get("123123")
    w.join()
