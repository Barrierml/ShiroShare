import random,string
import os_cope as oc
import os,copy,gc,time
class Abstract_File:
    """来储存还未实体化的文件"""
    def __int__(self,id):
        self.parent = None
        self.name= None
        self.suffix= None
        self._size= None
        self.md5= None
        self._identifier = id
        self.AttrCode = None
        self._end_time = None
    @property
    def id(self):
        return self._identifier
    @property
    def Name(self):
        return self.name + self.suffix
    def __str__(self):
        return "目录：{} 文件名：{} 后缀：{} 大小：{} MD5:{} 唯一ID：{}".format(self.parent,self.name,self.suffix,self._size,self.md5,self.id)
    def init_id(self):
        self._identifier = "".join([random.choice(string.ascii_letters+string.digits+"1234567890") for i in range(20)])
    @property
    def Dict(self):
        # 返回自己的信息
        return {"identifier":self.id,"name":self.name,"suffix":self.suffix,"md5":self.md5}
class Entity_File(Abstract_File):
    def __init__(self,url=None,Config=None,parent=None):
        super(Entity_File,self).__init__()
        if url == None and Config==None:
            raise KeyError("至少输入一个值")
        if Config != None:
            self.parent = parent.Abs_url
            self._identifier = Config.get("identifier")
            self.name = Config.get("name")
            self.suffix = Config.get("suffix")
            self.md5 = Config.get("md5")
            self.AttrCode = oc.GetAttrCode(self.Abs_url)
            self._size = oc.get_size(self.Abs_url)
            self._end_time = os.stat(self.Abs_url).st_mtime
        else:
            self.AttrCode = oc.GetAttrCode(url)
            self.parent,self.name,self.suffix = oc.get_file_all(url)
            self._size = oc.get_size(url)
            self.md5 = oc.Md5Get(url)
            self.init_id()
            self._end_time = os.stat(url).st_mtime
    @property
    def Abs_url(self):
        return os.path.join(self.parent, self.name + self.suffix)
    @property
    def size(self):
        return oc.Size(self._size)
    @property
    def time(self):
        return oc.chuo_time(self._end_time)
class Abstract_Dir:
    """储存文件夹信息"""
    def __init__(self):
        self.parent = None
        self.name = None
        self.url = None
        self.main_dir = False
        self._identifier = None
        self._File_list = []
        self._child_dir = []
        self.AttrCode = None
        self._end_time = None
    @property
    def id(self) -> str:
        return self._identifier
    @property
    def Dir(self) -> list:
        return self._child_dir
    @property
    def File(self) -> list:
        return self._File_list
    @property
    def File_Dict(self)-> list:
        return [i.Dict for i in self.File]
    @property
    def Dir_Dict(self)-> list:
        return [i.Abs_url for i in self.Dir]
    @property
    def Abs_url(self) -> str:
        if self.main_dir:
            return self.url
        return os.path.join(self.url,self.name)
    def File_url(self,url):
        return os.path.join(self.Abs_url,url)
    @property
    def time(self) -> str:
        return oc.chuo_time(self._end_time)
    @property
    def Dict(self) -> dict:
        # 返回自己的信息
        return {"parent":self.Abs_url,"identifier":self.id,"name":self.name,"files":self.File_Dict,"dirs":self.Dir_Dict}
    def __iter__(self):
        # 先迭代目录再迭代文件
        for i in self.Dir:
            yield i
        for i in self.File:
            yield i
    def init_id(self) -> None:
        self._identifier = "".join([random.choice(string.ascii_letters+string.digits+"1234567890") for i in range(20)])
    def __str__(self):
        return "文件夹：{} 文件：{}个 子文件夹{}个".format(self.Abs_url,len(self.File),len(self.Dir))
    def __getitem__(self,key):
        for i in self.Dir:
            if i.name == key:
                return i
        for i in self.File:
            if i.name == key:
                return i
        raise KeyError("找不到{}".format(key))
class Entity_Dir(Abstract_Dir):
    """实体文件夹，把所有文件信息载入到内存
        递归层数太多的话，会花费很长时间
        递归10层左右共16g的文件夹会花费25秒左右
        不过这个可能跟cpu有关
        所以选择只加载用户看的那一层比较好,也可以选择只加载前三层
    """
    def __init__(self,name=None,parent=None,Config=None,load_all=True):
        super(Entity_Dir,self).__init__()
        self.Config = Config
        if Config != None:
            if parent == None:
                self.parent = self
                self.main_dir = True
            else:
                self.parent = parent
            self.url = Config.get("parent")
            self.name = Config.get("name")
            self._identifier = Config.get("identifier")
            for i in Config["files"]:
                self.File.append(Entity_File(Config=i,parent=self))
            return
        if parent != None:
            self.url = parent.Abs_url
            self.name = name
        else:
            self.main_dir = True
            self.url = name
            _,self.name = oc.get_dir_all(self.url)
            self.parent = self
        self.AttrCode = oc.GetAttrCode(self.Abs_url)
        self._end_time = os.stat(self.Abs_url).st_mtime
        self.load_all = load_all
        if load_all:
            self.Init_directory()
    def Init_directory(self):
        # 初始化文件夹下的文件与子文件
        self.init_id()
        All = os.listdir(self.Abs_url)
        for i in All:
            # 如果是目录
            if i == "shiro_backup":
                # 不把备份文件夹放到模型里面
                continue
            if os.path.isdir(self.File_url(i)):
                self.Dir.append(Entity_Dir(i,parent=self,load_all=self.load_all))
            else:
                self.File.append(Entity_File(self.File_url(url=i)))
        self.CallBack()
    def clear(self):
        self.Dir.clear()
        self.File.clear()
    def CallBack(self):
        """继承这个方法来回调"""
        pass
    def copy(self):
        return copy.deepcopy(self)
    @property
    def size(self):
        n = 0
        for i in self.File:
            n += i._size
        for i in self.Dir:
            n += i.size
        return n
    def Is_Empty(self):
        if len(self.File) == 0 and len(self.Dir) == 0:
            return True
        return False
class File_Watch:
    # 具象化监控文件,实现自动备份功能
    @property
    def Abs_Url(self):
        # 绝对路径
        return os.path.join(self.url,self.name+self.suffix)
    @property
    def Size(self):
        # 大小 Byte单位
        return os.path.getsize(self.Abs_Url)
    def __str__(self):
        return str(self.name+self.suffix)
    def __init__(self):
        # 初始化属性
        # 文件名
        self.name = None
        # 文件后缀
        self.suffix = None
        # 唯一id
        self.id = None
        # 文件夹的父路径,并不包含自己
        self.url = None
        # md5
        self.md5 = None
        # 备份文件夹路径
        self.BackupUrl = None
        # 备份详情文件
        self.BackupList = []
        # 限制备份次数
        self.Limit_times = 5
        # 最后备份时间
        self.EndBackupTime = 0
    def Drestory(self):
        # 删除自己的配置文件
        oc.rmdirs(self.BackupUrl)
    def Load_Config(self,Config_Dir):
        # 读取备份配置,文件属性，和备份文件记录,合并改动
        self.BackupUrl = Config_Dir
        self.BackupJson = os.path.join(self.BackupUrl,"backup.json")
        # 两层之外就是文件存在目录
        self.url = os.path.dirname(os.path.dirname(self.BackupUrl))
        # 读取配置文件
        Config = oc.GetFileToJson(self.BackupJson)
        if not Config:
            # 配置文件损坏,删除所有文件
            print("{}找不到配置文件，删除".format(Config_Dir))
            self.Drestory()
            return False
        self.id = Config["id"]
        self.name = Config["name"]
        self.suffix = Config["suffix"]
        self.md5 = Config["md5"]
        self.BackupList = Config["backup"]
        # 读取出来的文件如果存在
        if os.path.exists(self.Abs_Url):
            # 获取属性，判断是否相同
            md5 = oc.Md5Get(self.Abs_Url)
            # 不相同就把当前文件备份
            if self.md5 != md5:
                self.Backup()
        else:
            # 此文件已经不存在了，删除所有记录
            self.Drestory()
            return False
        return True
    def Frist_Init(self,url,backupurl):
        #参数：url 文件完整的路径
        # 初始化属性
        self.url,self.name,self.suffix = oc.get_file_all(url)
        self.id = oc.Random_ID()
        try:
            self.md5 = oc.Md5Get(self.Abs_Url)
        except PermissionError:
            return False
        # 备份文件夹目录
        self.BackupUrl = os.path.join(backupurl,self.id)
        self.BackupJson = os.path.join(self.BackupUrl,"backup.json")
        # 创建备份文件夹
        os.mkdir(self.BackupUrl)
        # 隐藏文件夹
        # oc.SetAttrCode(self.BackupUrl, 18)
        # 先备份一下
        self.Backup()
        # 保存配置
        self.Updata_BackupJson()
        return True
    def Backup(self):
        if time.time() - self.EndBackupTime < 1:
            return
        # 获取改变的属性
        self.md5 = oc.Md5Get(self.Abs_Url)
        ttt = oc.GetFileEndTime(self.Abs_Url)
        # 备份的文件名是根据备份次数来递增的
        if len(self.BackupList) == 0:
            backup_name = 0
        else:
            backup_name = int(self.BackupList[-1].get("backup_name")) + 1
        # 列表要是超过限制次数就删除第一个再加入
        if len(self.BackupList) == self.Limit_times:
            # 取出第一个
            GetOut = self.BackupList.pop(0)
            # 删除存在的文件
            os.remove(os.path.join(self.BackupUrl,str(GetOut.get("backup_name"))))
        # 复制文件到备份文件
        b = os.path.join(self.BackupUrl,str(backup_name))
        oc.CopyFile(self.Abs_Url,b)
        self.EndBackupTime = time.time()
        # 完成以上动作后把数据写到备份记录里
        self.BackupList.append({
            "backup_name":backup_name,
            "name":self.name,
            "suffix":self.suffix,
            "time":ttt,
            "size":self.Size,
            "md5":self.md5,
        })
        # 保存备份记录
        self.Updata_BackupJson()
        # 传递参数到下一步
        self.NetSend(b)
    def Updata_BackupJson(self):
        ll = {
            "id":self.id,
            "name":self.name,
            "suffix":self.suffix,
            "md5":self.md5,
            "backup":self.BackupList
        }
        oc.SetJsonToFile(self.BackupJson,ll)
    def NetSend(self,BackupFileUrl):
        # 完成备份后自动把备份文件路径传进来，后续发送文件使用这个方法
        pass
class Dir_Watch:
    """
    具象化监控文件夹,只监视目录下的文件，子文件夹除外
    """
    @property
    def Abs_Url(self):
        # 返回自己的绝对路径
        return os.path.join(self.url,self.name)
    def FileAddUrl(self,ChildName):
        # 返回合并的绝对文件路径
        return os.path.join(self.Abs_Url,ChildName)
    def GetAllFiles(self):
        # 返回所有文件的配置位置
        return [i.BackupUrl for i in self.files]
    def files_name(self):
        # 返回备份的文件
        return [i.name+i.suffix for i in self.files]
    def Drestory(self):
        # 删除自己所有的文件
        oc.rmdirs(self.BackupUrl)
    def __init__(self):
        # 文件夹的名称
        self.name = None
        # 文件夹唯一id
        self.id = None
        # 文件夹的父路径,并不包含自己
        self.url = None
        # 子文件夹
        self.dirs = []
        # 子文件
        self.files = []
        # 上层目录
        self.parent = None
        # 备份目录
        self.BackupUrl = None

    def INIT(self, url):
        # 判断是否存在备份文件夹，然后确定调用新建还是加入
        if os.path.exists(os.path.join(url, "ShiroBackup")):
            try:
                self.Load_Config(url)
            except Exception as e:
                print(e)
                # 配置文件损坏，删除重建
                self.Drestory()
                self.Frist_Init(url)
        else:
            self.Frist_Init(url)
    def Frist_Init(self,url,parent=None):
        # 首次加载初始化
        # 分析url
        self.url,self.name = oc.get_dir_all(url)
        # 生成自己的id
        self.id = oc.Random_ID()
        # 生成备份文件夹
        self.BackupUrl = os.path.join(self.Abs_Url,"ShiroBackup")
        self.BackupJson = os.path.join(self.BackupUrl,"backup.json")
        os.mkdir(self.BackupUrl)
        # 隐藏文件夹
        oc.SetAttrCode(self.BackupUrl, 18)
        #添加提醒文件
        oc.SetJsonToFile(os.path.join(self.BackupUrl,"此文件夹是备份文件夹，请不要删除和修改任何文件.txt"),"")
        # 获取当前目录下所有文件
        All = os.listdir(self.Abs_Url)
        for i in All:
            if os.path.isdir(self.FileAddUrl(i)):
                q = Dir_Watch()
                self.dirs.append(q)
            else:
                q = File_Watch()
                try:
                    q.Frist_Init(self.FileAddUrl(i),self.BackupUrl)
                except PermissionError:
                    # 如果是权限错误就不管他
                    continue
                self.files.append(q)
        self.Updata_BackupJson()
    def Load_Config(self,url):
        self.url, self.name = oc.get_dir_all(url)
        self.BackupUrl = os.path.join(self.Abs_Url,"ShiroBackup")
        self.BackupJson = os.path.join(self.BackupUrl, "backup.json")
        Config = oc.GetFileToJson(self.BackupJson)
        self.id = Config["id"]
        # 判断多出来的文件，新建文件
        old_file_ll = Config["Files"]
        new_file_ll = oc.ListFiles(self.Abs_Url)
        overage = [y for y in new_file_ll if y not in old_file_ll]
        # 新建多出来的文件
        for i in overage:
            q = File_Watch()
            q.Frist_Init(self.FileAddUrl(i), self.BackupUrl)
            self.files.append(q)
        # 加载已存在文件
        for i in Config["FilesBackup"]:
            q = File_Watch()
            if q.Load_Config(i):
                self.files.append(q)
        # 保存一下更改的数据
        self.Updata_BackupJson()
        # 清除不存在文件
        self.ClearBackupDir()
    def Updata_BackupJson(self):
        ll = {
            "id":self.id,
            "Files":self.files_name(),
            "FilesBackup":self.GetAllFiles()
        }
        oc.SetJsonToFile(self.BackupJson,ll)
    def FindFile(self,filename) -> File_Watch:
        # 根据文件名添加
        for i in self.files:
            if filename == i.name+i.suffix:
                return i
    def AddFile(self,fileurl):
        # 添加文件到备份中
        q = File_Watch()
        if q.Frist_Init(fileurl,self.BackupUrl):
            self.files.append(q)
            self.Updata_BackupJson()
    def DelFile(self,filename):
        # 删除文件
        f = self.FindFile(filename)
        if f != None:
            f.Drestory()
            self.files.remove(f)
            self.Updata_BackupJson()
            return True
        return False
    def ClearBackupDir(self):
        # 清理不存在文件夹
        for i in os.listdir(self.BackupUrl):
            # 如果是文件夹就检查
            if os.path.isdir(os.path.join(self.BackupUrl,i)):
                p = File_Watch()
                p.Load_Config(os.path.join(self.BackupUrl,i))
                del p
        gc.collect()
    def search(self,id):
        # 通过id查找,返回最新的备份文件目录
        for i in self.files:
            if i.id == id:
                return i.Abs_url
if __name__ == '__main__':
    w = Dir_Watch()
    w.INIT("D:\英雄时刻")
    print(w.ClearBackupDir())