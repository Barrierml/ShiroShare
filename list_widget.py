from PyQt5.QtCore import QSequentialAnimationGroup, pyqtProperty,\
    QPauseAnimation, QPropertyAnimation, QParallelAnimationGroup,\
    QObject, QSize, Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor,QPixmap,QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout,QLabel,QDialog
class ll(QWidget):
    def __init__(self,file_name:str,file_suffiux,file_size,file_endtime,parent=None
                 ,model=None):
        super(ll,self).__init__(parent)
        layout_main = QHBoxLayout(self)
        layout_main.setContentsMargins(0, 0, 0, 0)
        self.file_name = file_name
        self.file_size = file_size
        self.file_endtime = file_endtime
        self.model = model
        #图标
        self.label = QLabel(self,pixmap=ll.flie_type(file_suffiux))
        # 文件夹去除尾部
        self.setFont(QFont("Microsoft YaHei",12))
        if file_suffiux != ".dir":
            self.label1 = QLabel(file_name+file_suffiux,self)
        else:
            self.label1 = QLabel(file_name, self)
        self.label2 = QLabel(file_size,self)
        # 设置文字居中
        self.label2.setAlignment(Qt.AlignCenter)
        self.label3 = QLabel(file_endtime,self)
        self.label3.setMargin(10)
        layout_main.addWidget(self.label)
        layout_main.addWidget(self.label1,2)
        layout_main.addWidget(self.label2,1)
        layout_main.addWidget(self.label3,1)
    def set_file_name(self,name):
        self.file_name = name
        self.label1.setText(name)
    def set_file_size(self,size):
        self.file_size = size
        self.label1.setText(size)
    def set_file_endtime(self,endtime):
        self.file_endtime = endtime
        self.label1.setText(endtime)
    @staticmethod
    def flie_type(name:str):
        def re_p(url):
            return QPixmap(url).scaled(49,49,aspectRatioMode=Qt.IgnoreAspectRatio)
        t = name.replace(".","")
        if not t:return re_p(":/file/unknown-ext.png")
        else:
            if t == "xlsx" or t == "xls"or t == "XLSX"or t == "XLS":return re_p(":/file/excel-ext.png")
            elif t == "gif" or t == "GIF":return re_p(":/file/gif-ext.png")
            elif t == "html" or t == "HTML":return re_p(":/file/htm-ext.png")
            elif t == "JPG" or t == "jpg":return re_p(":/file/jpg-ext.png")
            elif t == "NOTE" or t == "note":return re_p(":/file/note-ext.png")
            elif t == "PDF" or t == "pdf":return re_p(":/file/pdf-ext.png")
            elif t == "PNG" or t == "png":return re_p(":/file/png-ext.png")
            elif t == "PPT" or t == "ppt":return re_p(":/file/ppt-ext.png")
            elif t == "RAR" or t == "rar":return re_p(":/file/rar-ext.png")
            elif t == "swf" or t == "SWF":return re_p(":/file/swf-ext.png")
            elif t == "PNG" or t == "png":return re_p(":/file/png-ext.png")
            elif t == "AVI" or t == "avi" or t == "mov" or t =="MOV" or t=="rmvb"\
            or t == "RMVB" or t == "FLV" or t == "flv" or t == "mp4" or t == "MP4"\
            or t == "3GP" or t == "3gp":
                return re_p(":/file/vidoe-ext.png")
            elif t == "WAV" or t == "wav" or t == "mp3" or t == "MP3" or t == "WMA" \
            or t == "wma" or t == "OGG" or t == "ogg" or t == "FLAC" or t == "flac" \
            or t == "doc" or t == "DOC" or t == "DOCX" or t == "docx":return re_p(":/file/voice-ext.png")
            elif t == "ZIP" or t == "zip":return re_p(":/file/zip-ext.png")
            elif t == "dir":return re_p(":/file/dir.png")
            else:return re_p(":/file/unknown-ext.png")
class CircleItem(QObject):

    X = 0  # x坐标
    Opacity = 1  # 透明度0~1
    valueChanged = pyqtSignal()

    @pyqtProperty(float)
    def x(self) -> float:
        return self.X

    @x.setter
    def x(self, x: float):
        self.X = x
        self.valueChanged.emit()

    @pyqtProperty(float)
    def opacity(self) -> float:
        return self.Opacity

    @opacity.setter
    def opacity(self, opacity: float):
        self.Opacity = opacity


def qBound(miv, cv, mxv):
    return max(min(cv, mxv), miv)


class MetroCircleProgress(QWidget):

    Radius = 5  # 半径
    Color = QColor(24, 189, 155)  # 圆圈颜色
    BackgroundColor = QColor(Qt.transparent)  # 背景颜色

    def __init__(self, *args, radius=5, color=QColor(170, 0, 255),
                 backgroundColor=QColor(Qt.transparent), **kwargs):
        super(MetroCircleProgress, self).__init__(*args, **kwargs)
        self.Radius = radius
        self.Color = color
        self.BackgroundColor = backgroundColor
        self._items = []
        self.is_animation = False
    @pyqtProperty(int)
    def radius(self) -> int:
        return self.Radius

    @radius.setter
    def radius(self, radius: int):
        if self.Radius != radius:
            self.Radius = radius
            self.update()

    @pyqtProperty(QColor)
    def color(self) -> QColor:
        return self.Color

    @color.setter
    def color(self, color: QColor):
        if self.Color != color:
            self.Color = color
            self.update()

    @pyqtProperty(QColor)
    def backgroundColor(self) -> QColor:
        return self.BackgroundColor

    @backgroundColor.setter
    def backgroundColor(self, backgroundColor: QColor):
        if self.BackgroundColor != backgroundColor:
            self.BackgroundColor = backgroundColor
            self.update()

    def paintEvent(self, event):
        super(MetroCircleProgress, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.BackgroundColor)
        painter.setPen(Qt.NoPen)

        for item, _ in self._items:
            painter.save()
            color = self.Color.toRgb()
            color.setAlphaF(item.opacity)
            painter.setBrush(color)
            # 5<= radius <=10
            radius = qBound(self.Radius, self.Radius / 200 *
                            self.height(), 2 * self.Radius)
            diameter = 2 * radius
            painter.drawRoundedRect(
                QRectF(
                    item.x / 100 * self.width() - diameter,
                    (self.height() - radius) / 2,
                    diameter, diameter
                ), radius, radius)
            painter.restore()

    def start_animation(self):
        self.is_animation = True
        for index in range(5):  # 5个小圆
            item = CircleItem(self)
            item.valueChanged.connect(self.update)
            # 串行动画组
            seqAnimation = QSequentialAnimationGroup(self)
            seqAnimation.setLoopCount(-1)
            self._items.append((item, seqAnimation))

            # 暂停延迟动画
            seqAnimation.addAnimation(QPauseAnimation(150 * index, self))

            # 加速,并行动画组1
            parAnimation1 = QParallelAnimationGroup(self)
            # 透明度
            parAnimation1.addAnimation(QPropertyAnimation(
                item, b'opacity', self, duration=400, startValue=0, endValue=1.0))
            # x坐标
            parAnimation1.addAnimation(QPropertyAnimation(
                item, b'x', self, duration=400, startValue=0, endValue=25.0))
            seqAnimation.addAnimation(parAnimation1)
            ##

            # 匀速
            seqAnimation.addAnimation(QPropertyAnimation(
                item, b'x', self, duration=2000, startValue=25.0, endValue=75.0))

            # 加速,并行动画组2
            parAnimation2 = QParallelAnimationGroup(self)
            # 透明度
            parAnimation2.addAnimation(QPropertyAnimation(
                item, b'opacity', self, duration=400, startValue=1.0, endValue=0))
            # x坐标
            parAnimation2.addAnimation(QPropertyAnimation(
                item, b'x', self, duration=400, startValue=75.0, endValue=100.0))
            seqAnimation.addAnimation(parAnimation2)
            ##

            # 暂停延迟动画
            seqAnimation.addAnimation(
                QPauseAnimation((5 - index - 1) * 150, self))

        for _, animation in self._items:
            animation.start()
    def stop_animation(self):
        self.is_animation = False
        for _, animation in self._items:
            animation.stop()
        self._items.clear()
        self.update()
    def sizeHint(self):
        return QSize(100, self.Radius * 2)