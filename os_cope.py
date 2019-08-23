import os
from hashlib import md5
import win32con, win32api,time,json,random,string,shutil
"""
这个主要是自己写的关于文件操作的工具
"""
def open_file(url:str):
    if os.path.isfile(url):
        return os.system(url)
    else:
        return False
def open_dir(url):
    if os.path.isdir(url):
        return os.system("explorer "+ url)
    else:
        return False
def is_admin():
    if os.access("C:\\", os.R_OK | os.W_OK | os.X_OK):
        return True
    return False
def get_file_all(filename):
    # 获取文件名，路径，扩展名
    a,b = os.path.split(filename)
    s,e = os.path.splitext(b)
    return a,s,e
def get_dir_all(filename):
    # 获取主路径，名称
    a,b = os.path.split(filename)
    return a,b
def get_size(filename):
    if os.path.exists(filename):
        return os.path.getsize(filename)
    return False
def _get_md5(file_raw):
    md5obj = md5()
    md5obj.update(file_raw)
    hash = md5obj.hexdigest()
    return hash
def Md5Get(url):
    # 大文件就分割查看，小文件就整体查看，把时间压缩到0.01秒内
    if os.path.isfile(url):
        size = int(os.path.getsize(url)/1024/1024)
        if size>5:
            with open(url,"rb") as f:
                q1 = f.read(10000)
                f.seek(-10000,2)
                q2 = f.read(10000)
                return _get_md5(q1+q2)
        else:
            with open(url, "rb") as f:
                q1 = f.read()
                return _get_md5(q1)
    return False
def FullMd5Get(url):
    # 完整计算MD5
    if os.path.isfile(url):
        with open(url,"rb") as f:
            q1 = f.read()
            return _get_md5(q1)
    return False
def GetAllFile(_dir):
    if os.path.isdir(_dir):
        root = os.walk(_dir)
        for i in root:
            print(i)
def GetAttrCode(_dir):
    """
     获取文件属性返回码
     返回码   意义
      1      只读
      2      隐藏
      4      系统
      16     目录
      32     存档
      64     保留
      128    正常
      256    临时
      512    稀疏文件
      1024   超链接或者快捷方式
      2048   压缩文件
      4096   脱机文件
      8192   索引文件
      16384  加密
      65536  虚拟文件
    """
    if os.path.exists(_dir):
        attr = win32api.GetFileAttributes(_dir)
        return attr
    return False
def SetAttrCode(_dir,code):
    if os.path.exists(_dir):
        attr = win32api.SetFileAttributes(_dir,code)
        return attr
    return False
def Size(size:int):
    # 转换大小
    kb = round(size/1024,1)
    if kb < 1:
        return str(size) + "Byte"
    elif kb <1024:
        return str(kb) + "KB"
    MB = round(size/1024/1024,1)
    if MB <1024:
        return str(MB) + "MB"
    GB = round(size/1024/1024/1024,1)
    return str(GB) + "GB"
def chuo_time(shijiancuo):
    return time.strftime("%Y-%m-%d %H:%M",time.localtime(shijiancuo))
def GetFileEndTime(url):
    if os.path.exists(url):
        t = os.path.getmtime(url)
        return t
    return False
def GetFileToJson(url):
    # 开始打算用eval但是考虑安全性还是用json来导入
    if os.path.exists(url):
        try:
            with open(url,"rb") as f:
                r = f.read()
            return json.loads(r)
        except Exception as e:
            #未来加到日志中
            pass
    return False
def SetJsonToFile(url,data):
    try:
        with open(url,"w") as f:
            w = f.write(json.dumps(data))
            return w
    except Exception as e:
        print(e)
        #未来加到日志中
        pass
    return False
def GetSettingFile(dir,suffix=".json"):
    # 找到第一个为特定后缀的文件
    if os.path.isdir(dir):
        All = os.listdir(dir)
        for i in All:
            _,__,_suffix = get_file_all(i)
            if _suffix == suffix:
                return GetFileToJson(os.path.join(dir,i))
    return False
def Random_ID(length=20):
    #生成一个随机的id
    return "".join([random.choice(string.ascii_letters+string.digits+"1234567890") for i in range(length)])
def CopyFile(url1,url2):
    # 复制文件，这个只是不想再导一次包了
    shutil.copyfile(url1,url2)
def ListFiles(url):
    a = []
    All = os.listdir(url)
    for i in All:
        if os.path.isfile(os.path.join(url,i)):
            a.append(i)
    return a
def rmdirs(url):
    # 删除文件夹
    shutil.rmtree(url)
def MessageId():
    # 返回一个数字id
    return random.randint(0,10000)
def mkdir(url):
    # 创建文件夹
    if not os.path.exists(url):
        os.mkdir(url)
        return True
    return False
def path_join(a,b):
    return os.path.join(a,b)
if __name__ == '__main__':
    print(MessageId())
    pass