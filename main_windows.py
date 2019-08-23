import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QListWidgetItem\
    ,QPushButton,QWidget,QHBoxLayout,QLabel,QMenu,QSpacerItem,QSizePolicy
from PyQt5.QtCore import QSize,Qt,QPoint
from PyQt5.QtGui import QCursor,QFont
from main_ui import Ui_MWin
import os_cope as oc
from list_widget import ll,MetroCircleProgress
from functools import partial
import D_C,os,time,sip
from watch import Watch
import Net as CA


class ShiroShare_windows(QMainWindow, Ui_MWin):
    def __init__(self, parent=None):
        super(ShiroShare_windows, self).__init__(parent)
        # 初始化ui
        self.setupUi(self)
        self.INIT_UI()
        # 读取设置
        self.load_config()
        # 客户端属性
    def _show(self):
        self.show()
        self.Watch_List = [Watch("D:\英雄时刻",self.data)]
        self.NET = CA.ShiroNet(self.data)
        self.connectSlots()
        self.NET.start()
    def INIT_UI(self):
        # 进度条
        self.p = MetroCircleProgress()
        self.horizontalLayout_13.addWidget(self.p)
        self.p.setVisible(False)
    def load_config(self):
        # 软件设置
        self.data = {
            "name": "shiroshibe",
            "id": oc.Random_ID(length=10),
            "dir_url":"D:\备份"
        }
    def connectSlots(self):
        # 刷新
        self.pushButton_5.clicked.connect(self.hhh)
        # 搜索
        # self.pushButton_6.clicked.connect()
        # 菜单右键绑定
        self.listWidget.setContextMenuPolicy(3)
        self.listWidget.customContextMenuRequested[QPoint].connect(self.dianji_list)
        self.NET.InitFinsh.connect(self.navigation_bar_init)
        self.NET.LoadBar.connect(self.load_bar)
        self.Watch.All.connect(self.NET.Send_LIST)
    def progress_bar(self):
        if not self.p.is_animation:
            self.p.start_animation()
            self.p.setVisible(True)
        else:
            self.p.stop_animation()
            self.p.setVisible(False)

    def hhh(self):
        p = self.Model
        if isinstance(p, D_C.Entity_Dir):
            self.Load_Model(p.parent)

    def dianji_list(self, Qpiont):
        item = self.listWidget.itemAt(Qpiont)
        if item == None:
            return
        kongjian = self.listWidget.itemWidget(item)
        self.contextMenu = QMenu()
        # 菜单显示位置
        self.contextMenu.popup(QCursor.pos())
        self.actionopen = self.contextMenu.addAction('打开')
        self.actionopendir = self.contextMenu.addAction('打开所在文件夹')
        self.actionsharephone = self.contextMenu.addAction('分享到手机')
        self.actionAshuxing = self.contextMenu.addAction('属性')
        self.actionopen.triggered.connect(partial(self.actionHandler, kongjian))
        self.actionAshuxing.triggered.connect(partial(self.shuxing, kongjian))
        self.contextMenu.show()

    def actionHandler(self, kongjian: ll):
        self.Load_Model(kongjian.model)

    def shuxing(self, kongjian: ll):
        print(kongjian.model.AttrCode)

    def Load_Model(self, Model: D_C.Entity_Dir):
        self.listWidget.clear()
        self.Model = Model
        Model.clear()
        Model.Init_directory()
        if Model.Is_Empty():
            ww = QListWidgetItem(self.listWidget)
            ww.setSizeHint(QSize(200, self.listWidget.height()))
            pp = QPushButton("来到了没有任何东西的荒原")
            font = QFont()
            font.setFamily("Microsoft YaHei")
            font.setPointSize(20)
            pp.setFont(font)
            self.listWidget.setItemWidget(ww, pp)
            return
        for i in Model:
            ww = QListWidgetItem(self.listWidget)
            ww.setSizeHint(QSize(200, 50))
            if isinstance(i, D_C.Entity_Dir):
                self.listWidget.setItemWidget(ww, ll(i.name, ".dir", "——", i.time, model=i))
            elif isinstance(i, D_C.Entity_File):
                self.listWidget.setItemWidget(ww, ll(i.name, i.suffix, i.size, i.time, model=i))

    def load_bar(self, zhuangtaizhi):
        if not self.p.is_animation:
            self.progress_bar()
            self.state_bar = QPushButton(zhuangtaizhi)
            self.state_bar.setObjectName("state_bar")
            font = QFont()
            font.setFamily("Microsoft YaHei")
            font.setPointSize(12)
            self.state_bar.setStyleSheet("""#state_bar{border:0}""")
            self.state_bar.setFont(font)
            self.horizontalLayout_7.addWidget(self.state_bar)
            self.spacerItem = QSpacerItem(0, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
            self.horizontalLayout_7.addItem(self.spacerItem)
        else:
            self.state_bar.setText(zhuangtaizhi)
        # self.pushButton_7.setCursor(QCursor(Qt.PointingHandCursor))
        # self.pushButton_8.setCursor(QCursor(Qt.PointingHandCursor))

    def navigation_bar_init(self):
        # 清除加载栏
        self.progress_bar()
        self.state_bar.setVisible(False)
        sip.delete(self.state_bar)
        self.horizontalLayout_7.removeItem(self.spacerItem)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(ll.flie_type("实打实.123"))
    w = ShiroShare_windows()
    w._show()
    sys.exit(app.exec_())