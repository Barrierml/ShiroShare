import random,string
import os_cope as oc
import os,pprint,copy
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
    def id(self):
        return self._identifier
    @property
    def Dir(self):
        return self._child_dir
    @property
    def File(self) -> list:
        return self._File_list
    @property
    def File_Dict(self):
        return [i.Dict for i in self.File]
    @property
    def Dir_Dict(self):
        return [i.Abs_url for i in self.Dir]
    @property
    def Abs_url(self):
        if self.main_dir:
            return self.url
        return os.path.join(self.url,self.name)
    def File_url(self,url):
        return os.path.join(self.Abs_url,url)
    @property
    def time(self):
        return oc.chuo_time(self._end_time)
    @property
    def Dict(self):
        # 返回自己的信息
        return {"parent":self.Abs_url,"identifier":self.id,"name":self.name,"files":self.File_Dict,"dirs":self.Dir_Dict}
    def __iter__(self):
        # 先迭代目录再迭代文件
        for i in self.Dir:
            yield i
        for i in self.File:
            yield i
    def init_id(self):
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
if __name__ == '__main__':
    w = Entity_Dir("D:\英雄时刻")
    print(w["新建文件夹"].Abs_url)