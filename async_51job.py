import requests
from requests_html import HTMLSession, AsyncHTMLSession
import re, math, time
from bs4 import BeautifulSoup
from insertsql import *





headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51', 
           'Host': 'jobs.51job.com',
           'Upgrade-Insecure-Requests': '1'
           }

#获取城市的编号
def get_city_code():
    url = 'https://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20200818'
    result = requests.get(url, headers=headers).text
    #用eval函数将字符串转化为字典
    dic_string = eval(result.split('=')[1].split(';')[0])
    #字典的key是城市编号，value是城市名称
    #为了方便后续输入城市名称返回城市编号，将字典中的key和value对换
    dic_code = {}
    for key, value in dic_string.items():
        dic_code[value] = key
    return dic_code

#获取职位的总页数
def get_page_number(city_code, keyword):
    url = 'https://search.51job.com/list/{},000000,0000,00,9,99,{},2,1.html'\
          .format(city_code, keyword)
    session = HTMLSession()
    r = session.get(url, headers=headers)
    r.html.render()
    string = r.html.find('div.rt')[1].text
    total_page = re.findall('.*?(\d+).*', string)[0]
    if total_page:
        page_num = math.ceil(int(total_page)/50)
        #为防止页面太多，电脑资源不够用，设置页面数量不超过250
        if page_num > 250:
            page_num = 250
        return page_num
    else:
        return 0
    session.close()

#异步获取搜索关键字产生的每页信息    
async def get_url(session, url):
    
    r = await session.get(url, headers=headers)
    return r
#异步加载搜索关键字产生的每页信息，运行其中的javascript代码
async def render(r):
    #当加载页数很多时，所需时间较长，默认timeout为8秒，往往不够，在此设置为100秒，
    await r.html.arender(wait=0.2, timeout=999.0)
    return r.html


#遍历每一页的职位信息，异步进入每一条具体信息进行爬取
def get_page(city_code, keyword, page_num):
    session = AsyncHTMLSession()
    urls = []
    n = 0
    for i in range(page_num):
        url = \
            'https://search.51job.com/list/{},000000,0000,00,9,99,{},2,{}.html'\
          .format(city_code, keyword, i+1)
        urls.append(url)
    #异步获取所有的url返回的信息
    responses = session.run(*[get_url(session, url) for url in urls])
    print('所有网页加载完毕，共'+str(page_num)+'页')
    #异步加载responses中的网页，并返回
    results = session.run(*[render(r) for r in responses])
    print('所有网页中的JavaScript加载完毕，共'+str(len(results))+'个')
    
    #获取每一页中职位的url,异步加载后用parser()进行数据清洗,最后添加到Mysql中
    
    for r in results:
        task = []
        job_elements = r.find(
            'div.leftbox > div:nth-child(4) > div.j_joblist > div.e'
            )
        for job in job_elements:
            #获取单条职位信息的网址
            href = job.find('a')[0].attrs['href']
            task.append(get_info(href, session))
        contents = session.run(*task)
        info_dicts = parser(contents)
    
        #入库处理
        if info_dicts:
            for info_dict in info_dicts:
                insert_db(info_dict)
        n += 1
        print('完成第'+str(n)+'页数据的插入')
    session.run(session.close())
            

#爬取职位的详细信息
async def get_info(href, session):
    #当网址不是'jobs.51job.com'时，返回None
    if 'https://jobs.51job.com' in href:
        r = await session.get(href, headers=headers)
        return r

def parser(contents):
    #当相应网址对应的职位取消时，将无法读取网页信息，Exception会提示相关错误信息
    results = []
    for r in contents:
        #解析每条职位信息主页面中的内容，将各项信息存入temp_dict，最终汇总到
        #results，供插入Mysql使用
        try:
            temp_dict = {}
            soup = BeautifulSoup(r.content.decode('gbk'), 'html.parser')
            job_id = soup.find('div', class_='cn').h1.input['value']
            temp_dict['job_id'] = job_id
            job_info = soup.find('div', class_='cn')
            temp_dict['job_name'] = job_info.h1.get_text()
            temp_dict['job_salary'] = job_info.strong.get_text()
            temp_dict['company_name'] = soup.find('a', class_='com_name').\
                                        get_text()
            company_info = soup.find_all('p', class_='at')
            for info in company_info:
                if info.find('span', class_='i_flag'):
                    temp_dict['company_type'] = info.get_text()
                if info.find('span', class_='i_people'):
                    temp_dict['company_people'] = info.get_text()
                if info.find('span', class_='i_trade'):
                    temp_dict['company_trade'] = info.get_text()
            job_msgs = soup.find('p', class_='msg ltype').get_text().split('|')
            edu = ['初中及以下', '中专', '高中', '大专', '本科', '硕士', '博士']
            for i in range(len(job_msgs)):
                if i == 0:
                    temp_dict['job_loc'] = job_msgs[i].strip()
                else:
                    if '经验' in job_msgs[i] or '在校生' in job_msgs[i] \
                       or '应届生' in job_msgs[i]:
                        temp_dict['job_years'] = job_msgs[i].strip()
                    elif job_msgs[i].strip() in edu:
                        temp_dict['job_edu'] = job_msgs[i].strip()
                    elif '招' in job_msgs[i]:
                        temp_dict['job_count'] = job_msgs[i].strip()
                    elif '发布' in job_msgs[i]:
                        temp_dict['job_date'] = job_msgs[i].strip()
            welfare_raw = soup.find_all('span', class_='sp4')
            welfare = [welfare_raw[i].get_text() for i in range(len(welfare_raw))]
            temp_dict['company_welfare'] = '/'.join(welfare)
            job_info = soup.find('div', class_='bmsg job_msg inbox').\
                       find_all('p', recursive=False)
            job_info = [job_info[i].get_text() for i in range(len(job_info))]
            job_info = ' '.join(job_info).replace('  ', '\n')
            temp_dict['job_info'] = job_info
            temp_dict['recruit_source'] = '前程无忧'
            results.append(temp_dict)
        except Exception as e:
            print(e)
        
    return results

        
            
if __name__ == '__main__':
    #city, keyword由模块insertsql中的方法return_params()导入
    city, keyword = return_params()
    start = time.time()
    city_code = get_city_code()[city]
    page_num = get_page_number(city_code, keyword)
    get_page(city_code,keyword,page_num)
    end = time.time()
    #显示本次爬取消耗的时间
    print('爬取完毕,共耗时'+str(round(end-start, 2))+'秒')
    
        
        

