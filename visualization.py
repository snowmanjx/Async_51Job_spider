import matplotlib.pyplot as plt
from salary_average import gen_job_salary_average

'''从数据库中获取数据，利用matplotlib制作可视化图表'''


#获取mysql中的职位薪酬数据
job_average = gen_job_salary_average()
job_name = [job_name.split('_')[0] for job_name in job_average.keys()]
job_salary = [int(salary) for salary in job_average.values()]

#载入中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
#设置autolayout为True，在小图里也能将图表显示完整
plt.rcParams.update({'figure.autolayout': True})
#选择style
plt.style.use('fivethirtyeight')
#创建画布，获取fig和ax
fig, ax = plt.subplots()
#获取barh对象,用于后续标记注解用
rects = ax.barh(job_name, job_salary)
#定义autolabel函数，用来标记图形柱的宽度
def autolabel(rects):
    for rect in rects:
        width = rect.get_width()
        ax.annotate(str(width)+'元',
                    #xy代表标记的坐标，下面代码的效果是居中显示
                    xy=(width, rect.get_y()+rect.get_height()/2),
                    xytext=(3,0),
                    textcoords='offset points', 
                    va='center'
                    )
                    
autolabel(rects)
#设置坐标轴上的一些参数，因本人居住在杭州，故图表的title设置为“杭州互联网***”
#其他使用者可以按需自行更改地点
ax.set(xlabel='税前月薪(元)', 
       title='杭州互联网职位薪酬统计')
ax.set_ylabel('职位分类', labelpad=50, rotation=0)
plt.show()

