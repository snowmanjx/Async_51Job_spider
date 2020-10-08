# Async_51job_spider
异步爬取前程无忧的职位信息，其中insertdb.py中的建模及添加数据到mysql的代码借鉴了黄永祥著的《实战 python网络爬虫》。

使用前需要将requests-html的源码做以下两处修改：
1. 将HTML类中的方法render()和arender()中的html = HTML(url=self.url, html=content.encode(DEFAULT_ENCODING), default_encoding=DEFAULT_ENCODING)改为html = HTML(url=self.url, html=content.encode(self.encoding), default_encoding=DEFAULT_ENCODING)，这样就能正常显示"gbk"编码的网页。
2. 将AsyncHTMLSession类中的run()方法中的tasks = [asyncio.ensure_future(coro()) for coro in coros]改为tasks = [asyncio.ensure_future(coro) for coro in coros]。

使用者需要输入所要搜索的城市名及职位关键字，例如“python”， “java”， “互联网运营”等等。

visualization.py可以生成职位薪资的可视化分析图表。
