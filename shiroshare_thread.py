from PyQt5.QtCore import QThread

class Main_Thread(QThread):
    """
    主要用来初始化局域网内的信息与开始监控文件
    """
    def __init__(self):
        super(Main_Thread,self).__init__()