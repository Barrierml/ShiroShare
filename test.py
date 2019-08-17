from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,\
    QTextEdit,QHBoxLayout,QLabel,QGridLayout
from PyQt5.QtGui import QIcon,QColor
from Lib.FramelessWindow import FramelessWindow
from Lib.top_bar import top_bar
from Lib.body import control_bar,Body
class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        tb = top_bar()
        cb = control_bar()
        body = Body()
        layout_main = QVBoxLayout()
        layout_main.addWidget(tb)
        layout_main.addWidget(cb)
        layout_main.addWidget(body)
        self.setLayout(layout_main)
class App(FramelessWindow):
    def __init__(self,mode=None,_set=False):
        # mode是一个列表 [显示最小化，显示最大化（去除最大化会禁止控制大小）]
        if mode == None:
            self.mode = [1,1]
        else:
            self.mode = mode
        super().__init__(mode = self.mode,_set=_set)
        SS = """
        /*标题栏*/
        TitleBar {
            background-color:	rgb(100,149,237);
        }

        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color: 	rgb(100,149,237);
        }

        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            background-color: #d9d9d9;
        }
        #buttonClose:hover {
            color: white;
            background-color: rgb(232, 17, 35);
        }

        /*鼠标按下不放*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: #cccccc;
        }
        #buttonClose:pressed {
            color: white;
            background-color: rgb(161, 73, 92);
        }
        """
        self.setStyleSheet(SS)
        w = MainWindow(self)
        self.setWindowTitle('ShiroShare-赛维专用')
        self.setWindowIcon(QIcon('pic/MY.ico'))
        self.setWidget(w)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = App([1,1],_set=True)
    w.show()
    sys.exit(app.exec_())