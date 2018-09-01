import requests
import json
import re
import time
import csv
from requests.cookies import RequestsCookieJar
from cnki.CnkiSpider import verify
from selenium import webdriver
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import quote
import setting as st


class CnkiJournal:

    def __init__(self):
        self.now_time = time.strftime("%m%d_%H%M", time.localtime(time.time()))
        self.csv_file_name = self.now_time + "_journal.csv"

    def get_data(self, keyword):
        '''
        通过关键词搜索拿到列表数据
        '''
        all_data = []
        search = keyword
        driver = webdriver.Chrome()
        # 使用selenium打开知网网页进行搜索
        driver.get("http://kns.cnki.net/kns/brief/default_result.aspx")
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="Ecp_top_login"]/a/i').click()
        driver.find_element_by_id('Ecp_TextBoxUserName').send_keys(st.CNKI_USER)
        driver.find_element_by_id('Ecp_TextBoxPwd').send_keys(st.CNKI_PASSWD)
        driver.find_element_by_id('Ecp_Button1').click()

        # 大量js python无法执行大量js  所以获取浏览器的cookies 用于requests
        # 记得给每个请求加上cookies
        dcookies = driver.get_cookies()
        cookies = RequestsCookieJar()
        for cookie in dcookies:
            cookies.set(cookie['name'], cookie['value'])

        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="txt_1_sel"]/option[10]').click()
        driver.find_element_by_xpath('//*[@id="txt_1_value1"]').send_keys(search)
        driver.find_element_by_xpath('//*[@id="btnSearch"]').click()
        time.sleep(3)
        s = quote(search)
        # 请求头信息
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Host': 'kns.cnki.net',
            'Referer': 'http://kns.cnki.net/kns/brief/default_result.aspx',
        }
        self.data = {
            'pagename': 'ASP.brief_default_result_aspx',
            'dbPrefix': 'SCDB',
            'dbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'research': 'off',
            't': '1532051820667',
            'keyValue': '{}'.format(search),
            'S': '1'
        }
        proxyHost = st.proxyHost
        proxyPort = st.proxyPort

        # 代理隧道验证信息
        proxyUser = st.proxyUser
        proxyPass = st.proxyPass

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        self.contentUrl = 'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode={}&dbname={}&filename={}' \
                          '&uid=WEEvREcwSlJHSldTTEYzU3EycEhmbWZBTkJwa0xJQ3dMWkdpWndMWWdDRT0=$9A4hF_YAuvQ5' \
                          'obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&v=MTk1OTJUM3FUcldNMUZyQ1VSTEtmWU9kbU' \
                          'Z5cm5VNzNNSmlYVGJMRzRIOVhOclk5RlpvUjhlWDFMdXhZUzdEaDE='
        page_url = 'http://kns.cnki.net/kns/brief/brief.aspx?curpage={}&RecordsPerPage=20&QueryID=1&ID=&turn' \
                   'page=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&' \
                   'PageName=ASP.brief_default_result_aspx'
        api_url = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&dbPrefix=' \
                  'SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%' \
                  '87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1532051820667&' \
                  'keyValue={}&S=1'
        start_urls = api_url.format(s)
        req = requests.get(start_urls, headers = self.header, data = self.data, cookies = cookies,
                           allow_redirects = False).text
        soup = BeautifulSoup(req, 'lxml')
        MaxPage = soup.select('.countPageMark')[0].get_text().split('/')[1]  # 获取最大页数
        count = 0
        for i in range(1, int(MaxPage) + 1):
            print("正在抓取第%d页内容..." % i)
            time.sleep(2)
            page_data = {
                'curpage': '{}'.format(i),
                'RecordsPerPage': '20',
                'QueryID': '1',
                'ID': '',
                'turnpage': '1',
                'tpagemode': 'L',
                'dbPrefix': 'SCDB',
                'Fields': '',
                'DisplayMode': 'listmode',
                'PageName': 'ASP.brief_default_result_aspx'
            }
            try:
                Get = requests.get(page_url.format(i), headers = self.header, data = page_data, cookies = cookies,
                                   proxies = proxies)  # 请求翻页数据

                if Get.status_code in [400, 402, 404]:
                    print("请检查ip隧道是否到期....")

                # 破解验证码
                # 如果需要打开注释
                # 请确认打码策略
                # if '请输入验证码' in Get.text:
                #     print("正在识别验证码....")
                #     verify.getCkCode(self.header, cookies)
                #     vc = verify.ydmInit()
                #     if len(vc) is 5:
                #         if count == 5:
                #             time.sleep(10)
                #         if count == 10:
                #             print("知网已经爬虫封禁，将已下载内容保存，请检查ip隧道和打码平台是否都到期，然后重新尝试下载...")
                #             break
                #         verify.botCheck(page_url.format(i)[19:], vc, self.header, cookies, i)
                #         Get = requests.get(page_url.format(int(i)), headers = self.header, data = page_data,
                #                            cookies = cookies, proxies = proxies)
            except Exception as e:
                print(e)
                continue
            soup = BeautifulSoup(Get.text, 'lxml')
            table = soup.select('.GridTableContent tr')[1:21]
            if len(table) == 0:
                count += 1
            else:
                count = 0
            for i in table:
                try:
                    filename = i.select('.fz14')[0]['href'].split('=')[4].replace('&DbName', '')  # 文章页面所需要的三个参数
                    dbname = i.select('.fz14')[0]['href'].split('=')[5].replace('&DbCode', '')
                    dbcode = i.select('.fz14')[0]['href'].split('=')[6].replace('&yx', '')
                    ContTitle = i.select('.fz14')[0].get_text()  # 标题
                    author = re.compile('<a class="KnowledgeNetLink" href=.*?>(.*?)</a>').findall(str(i))  # 作者
                    datetime = i.select('td')[4].get_text().strip()  # 时间
                    datetime = self.time_exchange(datetime)
                    contUrl = self.contentUrl.format(dbcode, dbname, filename)  # 论文url
                    dicts = self.getCont(contUrl, ContTitle, author, datetime, cookies)
                    all_data.append(dicts)
                except Exception as e:
                    print(e)
                    continue

        print("%s关键词内容抓取完成..." % keyword)
        driver.quit()

        self.save_journal_data(keyword, all_data)
        file_name = self.now_time + "_journal_%s" % keyword + ".txt"
        with open("cnki/output/" + file_name, "w") as f:
            f.write(json.dumps(all_data))

    # 抓取论文摘要数据
    def getCont(self, contUrl, ContTitle, author, datetime, cookies):
        reqs = requests.get(contUrl, headers = self.header, allow_redirects = False, cookies = cookies)
        soup = BeautifulSoup(reqs.text, 'lxml')
        try:
            abstract = soup.select('#ChDivSummary')[0].get_text()  # 摘要
        except IndexError:
            abstract = None
        company = etree.HTML(reqs.text).xpath('//*[@id="mainArea"]/div[3]/div[1]/div[2]/span/a/text()')  # 单位
        mark = etree.HTML(reqs.text).xpath('//*[@id="mainArea"]/div[3]/div[3]/div[2]/div[2]/p[1]/a/text()')  # 来源
        dicts = {
            'ContTitle': ContTitle,
            'ContUrl': contUrl,
            'author': ",".join(author),
            'mark': ",".join(mark),
            'datetime': datetime,
            'abstract': abstract,
            'company': ",".join(company),
        }
        print(dicts)
        return dicts

    def time_exchange(self, t):
        try:
            if ":" in t:
                time_ = time.strptime(t, "%Y-%m-%d %H:%M")
            else:
                time_ = time.strptime(t, "%Y-%m-%d")
            time_ = time.strftime("%Y%m%d", time_)
        except:
            time_ = time.strftime("%Y%m%d", time.localtime(time.time()))
        return time_

    def time_in(self, time_):
        start = st.START
        end = st.END
        if start == "" or end == "":
            return True
        start_time = time.strptime(start, "%Y%m%d")
        end_time = time.strptime(end, "%Y%m%d")
        c_time = time.strptime(time_, "%Y%m%d")
        return start_time <= c_time and end_time >= c_time

    def save_journal_data(self, keyword, all_data):
        with open("cnki/output/by_journal/" + self.csv_file_name, "a", encoding = 'utf-8', newline = '') as csv_file:
            csv_writer = csv.writer(csv_file)
            print("%s有%d篇文献" % (keyword, len(all_data)))
            for dicts in all_data:
                journal = dicts["mark"]
                from_ = dicts["company"]
                title = dicts["ContTitle"]
                author = dicts["author"]
                time_ = dicts["datetime"]
                article_abstract = dicts["abstract"]
                if not self.time_in(time_):
                    continue
                content_link = dicts["ContUrl"]
                row = [keyword, journal, author, from_, time_, title, article_abstract, content_link]
                csv_writer.writerow(row)

    def crawl_cnki_by_journal(self):
        journals = st.JOURNAL
        with open("cnki/output/by_journal/" + self.csv_file_name, "w", encoding = 'utf-8', newline = '') as csv_file:
            csv_writer = csv.writer(csv_file)
            header_row = ["keyword", "journal", "author", "from", "time", "title", "article_abstract", "content_link"]
            csv_writer.writerow(header_row)

        for j in journals:
            self.get_data(j)
