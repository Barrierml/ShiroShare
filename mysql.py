import sqlite3
class mysql:
    def __init__(self,sqlname):
        self._con = sqlite3.connect(sqlname)
        self.cc = self._con.cursor()
    def commit(self):
        self._con.commit()
    def table_is_in(self,table_name:str):
        command = "select * from sqlite_master where type = 'table' and name = '{}' ".format(table_name)
        self.cc.execute(command)
        if len(self.cc.fetchall()) == 0:
            return False
        else:
            return True
    def create_table(self,table_name:str,lie:dict):
        if self.table_is_in(table_name):
            return False
        ll = ""
        for k,v in lie.items():
            ll += str(k) +' '+  str(v) + ","
        ll = ll[:-1]
        command = '''CREATE TABLE {} ({})'''.format(table_name,ll)
        print(command)
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
        return self.cc.fetchall()
