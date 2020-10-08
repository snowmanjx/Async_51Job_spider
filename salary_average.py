import re
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker



#计算折算后的月均收入
def salary_average(salary):
    averages = []
    for i in salary:
        try:
            #因为query.all()获取的是由元组组成的列表，
            #所以需要获取元组中的第一个数据
            i = i[0]
            if '月' in i:
                    sa_range = re.findall('(.*?-.*?)./', i)
                    num = sa_range[0].split('-')
                    if '万' in i:
                            average = (float(num[0]) + float(num[1]))\
                                      / 2 * 10000
                    elif '千' in i:
                            average = (float(num[0]) + float(num[1]))\
                                      / 2 * 1000
            elif '年' in i:
                    sa_range = re.findall('(.*?-.*?)./', i)
                    num = sa_range[0].split('-')
                    average = (float(num[0]) + float(num[1]))\
                              * 10000 / 24
            elif '天' in i:
                    average = float(re.findall('(.*?)./', i)[0]) * 21.75
            averages.append(average)
        except Exception as e:
            pass
    sa_average = round(sum(averages)/len(averages))
    return sa_average

def gen_job_salary_average():
    #创建与mysql的连接
    engine = create_engine('mysql+pymysql://root:"输入你自己的密码"@localhost:3306\
    /spiderdb?charset=utf8')
    #创建会话实例
    session = sessionmaker(bind=engine)()
    #创建元数据实例
    metadata = MetaData()
    #获取数据库中的所有表单名
    tables = engine.table_names()
    job_average = {}
    #遍历每个表单，将数据库中的table建立Table实例，映射到内存中
    for table in tables:
        table_c = Table(table, metadata, autoload=True, autoload_with=engine)
        data = session.query(table_c.c.job_salary).all()
        sa_average = salary_average(data)
        job_average[table] = sa_average
    return job_average                



