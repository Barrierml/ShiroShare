import sqlite3,time


class mysql:
    def __init__(self,sqlname):
        # 链接服务器
        self._con = sqlite3.connect(sqlname,check_same_thread=False)
        self.cc = self._con.cursor()
    def commit(self):
        # 提交更改
        self._con.commit()
    def table_is_in(self,table_name:str):
        # 判断表格是否在数据库内
        command = "select * from sqlite_master where type = 'table' and name = '{}' ".format(table_name)
        self.cc.execute(command)
        if len(self.cc.fetchall()) == 0:
            return False
        else:
            return True
    def create_table(self,table_name:str,lie:dict):
        # 创建表
        # 例子: create_table("table_name",{"hahah":"TEXT"})
        if self.table_is_in(table_name):
            return False
        ll = ""
        for k,v in lie.items():
            ll += str(k) +' '+  str(v) + ","
        ll = ll[:-1]
        command = '''CREATE TABLE {} ({})'''.format(table_name,ll)
        try:
            self.cc.execute(command)
        except Exception as e:
            raise Exception(e)
        else:
            self.commit()
            return True
    def del_table(self,table_name):
        if not self.table_is_in(table_name):
            return False
        command = "DROP TABLE {}".format(table_name)
        try:
            self.cc.execute(command)
        except Exception as e:
            raise Exception(e)
        else:
            self.commit()
            return True
    def insert(self,table_name,ll):
        # 添加到表格内，ll为列表或字典，列表支持多个导入
        # 例子 列表加入insert("User",[(id,name,ip)])
        # 例子 字典添加insert("User",{"name":"123","12321":"213"})
        # 标准添加语句 INSERT INTO COMPANY VALUES (7, 'James', 24, 'Houston', 10000.00 );
        if isinstance(ll,dict):
            sql_len = len(self.table_key(table_name))
            se_len = len(ll)
            if sql_len != se_len:
                raise KeyError("插入数目 {} 与输入数目 {} 不相同".format(se_len, sql_len))
            keys = ','.join(ll.keys())
            pp =[]
            for i in ll.values():
                pp.append('"'+ str(i)+'"')
            values = ','.join(pp)
            sql = 'INSERT INTO {table}({keys}) VALUES({values})'.format(table=table_name, keys=keys, values=values)
            self._con.execute(sql)
            self.commit()
        else:
            """"executemany(templet,args)
            　　templet : sql模板字符串,
                例如     'insert into table(id,name) values(%s,%s)'
　　              args: 模板字符串的参数，是一个列表，列表中的每一个元素必须是元组！！！ 
                例如：  [(1,'小明'),(2,'zeke'),(3,'琦琦'),(4,'韩梅梅')] """
            sql_len = len(self.table_key(table_name))
            se_len = len(ll[0])
            if  sql_len != se_len:
                raise KeyError("插入数目 {} 与输入数目 {} 不相同".format(se_len,sql_len))
            q_num = ",?" * (sql_len-1)
            command = "INSERT INTO {} values (?{})".format(table_name,q_num)
            self._con.executemany(command,ll)
            self.commit()
    def table_key(self,table_name):
        """PRAGMA table_info({}) 的返回值
                下标	名称	描述
                0	cid	    序号
                1	name	名字
                2	type	数据类型
                3	notnull	能否null值，0不能，1 能
                4	dflt_value	缺省值
                5	pk	是否主键primary key,0否，1是
        """
        self.cc.execute("PRAGMA table_info({})".format(table_name))
        re = []
        for i in self.cc.fetchall():
            re.append(i[1])
        return re
class ShiroSQL(mysql):
    """主要管理用户列表,和文件列表"""
    def __init__(self,name="ShiroDB"):
        super(ShiroSQL,self).__init__(name)
        # 如果不在数据库内就重新初始化
        if not self.table_is_in("User"):
            # 创建用户数据库
            self.create_table("User",{
                "_id":"TEXT",
                "Name":"TEXT",
                "ip":"TEXT",
                "end_life_time":"TEXT",
            })
            # 创建文件数据库
            self.create_table("Files",{
                "_id":"TEXT",
                "FileName":"TEXT",
                "suffix":"TEXT",
                "md5":"TEXT",
                "belong_dir": "TEXT",
                # 拥有者用id保存
                "owner":"TEXT",
                "abs_url":"TEXT",
                "end_time":"TEXT"
            })
            # 创建文件夹
            self.create_table("Dirs",{
                "_id":"TEXT",
                "owner":"TEXT",
                "Name":"TEXT",
                "abs_url":"TEXT",
                "end_time":"TEXT",
            })
    def AddUser(self,id,name,ip):
        # 添加用户
        self.insert("User",[(id,name,ip,str(time.time()))])
    def GetAllUser(self):
        # 获取所有用户
        self.cc.execute('select *from User')
        return self.cc.fetchall()
    def ChangeUser(self,id,data):
        m =""
        p = 1
        ll = self.table_key("User")
        data["end_life_time"] = time.time()
        for k,v in data.items():
            if k not in ll:
                continue
            if p == 1:
                m += "{}='{}'".format(k,v)
            else:
                m += ",{}='{}'".format(k, v)
            p += 1
        if p == 1:
            return
        command = "update User set {} where _id ='{}'".format(m,id)
        self.cc.execute(command)
        self.commit()
    def DelUser(self,id):
        # 删除用户
        command = "DELETE from User where _id='{}'".format(id)
        self.cc.execute(command)
        self.commit()
    def AddFile(self,id,name,suffix,md5,belong_dir,owner,abs_url,endtime):
        if not self.InFiles(id):
            self.insert("Files",[(id,name,suffix,md5,belong_dir,owner,abs_url,endtime)])
            return True
        return False
    def GetAllFile(self):
        # 从文件库里面获取文件，数量按照Number
        self.cc.execute('select *from Files')
        return self.cc.fetchall()
    def DelFile(self,id):
        command = "DELETE from Files where _id='{}'".format(id)
        self.cc.execute(command)
        self.commit()
    def InUsers(self,id):
        command = "select * from User where _id = '{}'".format(id)
        self.cc.execute(command)
        if self.cc.fetchone():
           return True
        return False
    def ChangeFile(self,id,data:dict=None):
        # 改变文件属性
        m =""
        p = 1
        ll = self.table_key("Files")
        for k,v in data.items():
            if k not in ll:
                continue
            if p == 1:
                m += "{}='{}'".format(k,v)
            else:
                m += ",{}='{}'".format(k, v)
            p += 1
        if p == 1:
            return
        command = "update Files set {} where _id ='{}'".format(m,id)
        print(command)
        self.cc.execute(command)
        self.commit()
    def InFiles(self,id):
        command = "select * from Files where _id = '{}'".format(id)
        self.cc.execute(command)
        if self.cc.fetchone():
           return True
        return False
    def GetInDirFIles(self,dirid):
        # 获取某文件夹内所有文件
        command = "select * from Files where belong_dir = '{}'".format(dirid)
        self.cc.execute(command)
        p = []
        for i in self.cc.fetchall():
            p.append({
                "_id":i[0],
                "FileName":i[1],
                "suffix":i[2],
                "md5":i[3],
                "belong_dir": i[4],
                "owner":i[5],
                "abs_url":i[6],
                "end_time":i[7]
            })
        return p
    def GetAllDir(self):
        # 从文件库里面获取文件，数量按照Number
        self.cc.execute('select *from Dirs')
        return self.cc.fetchall()
    def InDirs(self,id):
        command = "select * from Dirs where _id = '{}'".format(id)
        self.cc.execute(command)
        if self.cc.fetchone():
           return True
        return False
    def AddDir(self,id,owner,name,absurl):
        self.insert("Dirs", [(id, owner, name, absurl,time.time())])
    def GetDirName(self,id):
        if self.InDirs(id):
            command = "select * from Dirs where _id = '{}'".format(id)
            self.cc.execute(command)
            return self.cc.fetchone()[2]
        return False
if __name__ == '__main__':
    cc = ShiroSQL("D:\\ShiroShare\\222")
    print(cc.InUsers("123"))