import time
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import *

#建立与Mysql的连接
engine = create_engine('mysql+pymysql://root:"输入你自己的密码"@localhost:3306\
/spiderdb?charset=utf8')
#建立操控Mysql的会话
DBsession = sessionmaker(bind=engine)
SQLsession = DBsession()
#创建数据模型父类Base
Base = declarative_base()

#城市名称和搜索关键字由用户输入
city = input('请输入需要搜索的城市名称: ')
keyword = input('请输入需要搜索的关键字: ')

def return_params():
    return city, keyword

#定义数据模型，类的属性对应数据表的字段，添加数据表
class table_info(Base):
    __tablename__ =  keyword + '_' + city + '_job_info'
    id = Column(Integer(), primary_key=True)
    job_id = Column(String(100), comment='职位id')
    job_name = Column(String(3000), comment='职位名称')
    job_salary = Column(String(100), comment='职位薪酬')
    company_name = Column(String(100), comment='公司名称')
    company_type = Column(String(100), comment='公司类型')
    company_people = Column(String(100), comment='公司规模')
    company_trade = Column(String(100), comment='公司经营范围')
    company_welfare = Column(String(1000), comment='企业福利')
    job_loc = Column(String(100), comment='工作区域')
    job_years = Column(String(100), comment='工龄要求')
    job_edu = Column(String(100), comment='学历要求')
    job_count = Column(String(100), comment='招聘人数')
    job_date = Column(String(100), comment='发布日期')
    job_info = Column(Text, comment='职位信息')
    recruit_source = Column(String(100), comment='招聘来源')
    log_date = Column(String(100), comment='记录日期')

#创建数据表
Base.metadata.create_all(engine)

#写入数据库
def insert_db(info_dict):
    temp_id = info_dict['job_id']
    #通过job_id判断记录是否存在
    info = SQLsession.query(table_info).filter_by(job_id=temp_id).first()
    #如果存在该条记录，则更新数据
    if info:
        info.job_name = info_dict.get('job_name', '')
        info.job_salary = info_dict.get('job_salary', '')
        info.company_name = info_dict.get('company_name', '')
        info.company_type = info_dict.get('company_type', '')
        info.company_people = info_dict.get('company_people', '')
        info.company_trade = info_dict.get('company_trade', '')
        info.company_welfare = info_dict.get('company_welfare', '')
        info.job_loc = info_dict.get('job_loc', '')
        info.job_years = info_dict.get('job_years', '')
        info.job_edu = info_dict.get('job_edu', '')
        info.job_count = info_dict.get('job_count', '')
        info.job_date = info_dict.get('job_date', '')
        info.job_info = info_dict.get('job_info', '')
        info.recruit_source = info_dict.get('recruit_source', '')
        info.log_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    #若不存在该条记录，则添加该条数据
    else:
        insert_data = table_info(
            job_id = info_dict.get('job_id', ''),
            job_name = info_dict.get('job_name', ''),
            job_salary = info_dict.get('job_salary', ''),
            company_name = info_dict.get('company_name', ''),
            company_type = info_dict.get('company_type', ''),
            company_people = info_dict.get('company_people', ''),
            company_trade = info_dict.get('company_trade', ''),
            company_welfare = info_dict.get('company_welfare', ''),
            job_loc = info_dict.get('job_loc', ''),
            job_years = info_dict.get('job_years', ''),
            job_edu = info_dict.get('job_edu', ''),
            job_count = info_dict.get('job_count', ''),
            job_date = info_dict.get('job_date', ''),
            job_info = info_dict.get('job_info', ''),
            recruit_source = info_dict.get('recruit_source', ''),
            log_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            )
        SQLsession.add(insert_data)
    SQLsession.commit()
                                         
            
