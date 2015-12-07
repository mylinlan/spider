# -*- coding:utf-8 -*-
import MySQLdb
import time


class Mysql(object):
    def __get_time(self):
        return self.time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    def __log(self, log_str, *args, **kw):
        current_time = self.__get_time()
        print current_time + ' : ' + log_str,
        for each in args:
            print each,
        print '\n',
        for each in kw.keys():
            print current_time + ' : ' + each + ' is ' + kw[each]

    # 数据库初始化
    def __init__(self):
        self.time = time
        try:
            self.db = MySQLdb.connect(host='localhost', port=3306, user='lin', passwd='lin', db='tianya')
            self.cur = self.db.cursor()
        except MySQLdb.Error, e:
            self.__log("链接数据库失败，原因:", e.args[0], e.args[1])
	    exit()

    # 插入数据
    def insert_data(self, table, my_dict):
        try:
            self.db.set_character_set('utf8')
            cols = ', '.join(my_dict.keys())
            values = '"," '.join(my_dict.values())
            # print cols
            # print values
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, '"'+values+'"')
            try:
                result = self.cur.execute(sql)
                insert_id = self.db.insert_id()
                self.db.commit()
                # 判断是否执行成功
                if result:
                    return insert_id
                else:
                    return 0
            except MySQLdb.Error, e:
                # 发生错误时回滚
                self.db.rollback()
                # 主键唯一，无法插入
                if "key 'PRIMARY'" in e.args[1]:
                    self.__log("数据已存在，未插入数据")
                else:
                    self.__log("插入数据失败，原因:", e.args[0], e.args[1])
        except MySQLdb.Error, e:
            self.__log("数据库错误，原因:", e.args[0], e.args[1])

    def clean_table(self, table):
        try:
            sql = "truncate %s" % (table,)
            self.__log(sql)
            self.cur.execute(sql)
            self.db.commit()
        except MySQLdb.Error, e:
            self.__log("清空表错误，原因", e.args[0], e.args[1])

if __name__ == '__main__':
    m = Mysql()
    m.clean_table('titleswe')
