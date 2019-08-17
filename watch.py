import time,shutil,datetime,os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os_cope as oc
from PyQt5.QtCore import QThread,pyqtSignal
from queue import Queue
from D_C import Entity_Dir
import threading
# 设计思路是把监控和文件管理分开，防止文件处理时的卡顿
# 子进程打开watchdog，子进程自己处理关于文件处理，复制，备份等需要阻塞的动作
# 来防止watchdog在监控上的不及时，当文件发生改变再发给子进程处理
# 通过子进程再与主进程通信,进行显示和发送的工作
# 由于watchdog只能监控监控目录的文件，无法监控子目录里的文件，所以只能递归，文件管理也要改。。。
#
class Watch_Dir(threading):
    loaded = pyqtSignal(str)
    freshUi = pyqtSignal(object)
    def __init__(self,dir_url,Model=None,Parent=None) -> None:
        super(Watch_Dir,self).__init__()
        self.ChildTread = []
        self.q = Queue()
        self.url = dir_url
        self.is_watching = False
        self.Model = Model
        self.Parent = Parent
        # 备份的文件夹
        self.backup_url = os.path.join(self.url,"shiro_backup")
    def run(self) -> None:
        # 先检测是否有配置文件夹
        if not os.path.exists(self.backup_url):
            self.New_Init()
        else:
            # 加载配置文件夹
            self.Load_Init()
        # 开启watchdog
        self.freshUi.emit(self.Model)
        while True:
            # 一直循环会卡，加个时间
            self.msleep(100)
            while not self.q.empty():
                print(self.q.get())
    def AddNewWatch(self,url):
        event_handler = MyHandler(self.q)
        observer = Observer()
        observer.schedule(event_handler, path=url, recursive=False)
        observer.start()
        self.ChildTread.append(observer)
    def New_Init(self):
        # 更新全新的文件夹
        try:
            os.mkdir(self.backup_url)
            oc.SetAttrCode(self.backup_url, 18)
            # 建立文件模型,受watchdog的限制,每一个子文件都要建立自己的监控。。
            self.Model = Entity_Dir(name=self.url, load_all=False)
            self.Model.Init_directory()
            # 把所有文件信息保存到配置文件内
            oc.SetJsonToFile(os.path.join(self.backup_url, self.Model.id + ".json"), self.Model.Dict)
            # 新建文件备份文件夹
            for i in self.Model.File:
                try:
                    os.mkdir(os.path.join(self.backup_url,i.id))
                except Exception as e:
                    print(e)
            # 建立子文件夹的监控
            for a in self.Model.Dir:
                self.AddNewWatch(a.Abs_url)
        except Exception as e:
            print(e)
            pass
    def Load_Init(self):
        # 读取本地配置
        Setting = oc.GetSettingFile(self.backup_url)
        # 防止有文件夹没有文件
        if Setting:
            # 实例化自己
            self.Model = Entity_Dir(Config=Setting)
class MyHandler(FileSystemEventHandler):
    def __init__(self,Queue:Queue):
        self.q = Queue
    def on_any_event(self, event):
        time.sleep(1)
        if os.path.exists(event.src_path):
            self.q.put([event.src_path,event.event_type])
if __name__ == "__main__":
    w = Watch_Dir("D:\\英雄时刻")
    w.start()
