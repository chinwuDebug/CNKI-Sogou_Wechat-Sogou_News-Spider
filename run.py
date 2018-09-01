
import setting as st
from sogou_wechat.sogou_wechat import SogouWechat
from sogou_news.sogou_news import SogouNews
from cnki.CnkiSpider.cnki_journal import CnkiJournal
from cnki.CnkiSpider.cnki_from import CnkiFrom

"""
程序入口
请在setting中输入参数，运行此文件
"""

if st.DATA_FROM == "sogou_news":
    spider = SogouNews()
    spider.crawl_sogou_news()
elif st.DATA_FROM == "sogou_wechat":
    spider = SogouWechat()
    spider.crawl_sogou_wechat()
elif st.DATA_FROM == "cnki_journal":
    spider = CnkiJournal()
    spider.crawl_cnki_by_journal()
elif st.DATA_FROM == "cnki_from":
    spider = CnkiFrom()
    spider.crawl_cnki_by_from()
else:
    print("请指定数据来源...")