import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
import csv
import setting as st


class SogouNews:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
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

    now_time = time.strftime("%m%d_%H%M", time.localtime(time.time()))
    all_data = []

    def __init__(self):
        pass

    def get_search_url(self, keyword, max_page):
        news_datas = []
        max_page = max_page < 2 and 2 or max_page
        current_content = ""
        for n in range(1, max_page):
            time.sleep(3)
            try:
                new_url = "http://news.sogou.com/news?mode=1&manual=&query=%s&time=0&sort=0" \
                          "&page=%d&w=03009900&dr=1&_asf=news.sogou.com&_ast=1532749568" % (
                              quote("\"" + keyword + "\""), n)
                r = requests.get(new_url, headers = self.headers, proxies = self.proxies)
                # print("搜狗新闻页面状态：%d" % r.status_code)
                if r.status_code == 503:
                    print("关键词搜索完成...")
                    break
                print("关键词：%s...第%d页" % (keyword, n))

                clean_text = ""
                for t in r.text.split("\n"):
                    if "<a href=" in t and "id=\"uigs_" in t:
                        clean_text += t
                    if "<p class=\"news-from\">" in t:
                        clean_text += t

                if current_content == clean_text:
                    print("关键词搜索完成...")
                    break

                current_content = clean_text
                soup = BeautifulSoup(clean_text, "lxml")
                urls = []
                titles = []
                froms = []
                times = []
                for new in soup.find_all("a"):
                    url = new.attrs["href"]
                    title = new.get_text()
                    urls.append(url)
                    titles.append(title)
                    # print(title, url)
                for new in soup.find_all("p"):
                    from_time = new.get_text()
                    from_ = from_time.split("\xa0")[0]
                    time_ = from_time.split("\xa0")[1]
                    froms.append(from_)
                    times.append(time_)
                    # print(from_time)

                if len(urls) != len(times):
                    print("抓取内容格式....关键词：%s...第%d页..." % (keyword, n))
                    continue

                for i in range(len(urls)):
                    news_data = {}
                    news_data["url"] = urls[i]
                    news_data["title"] = titles[i]
                    news_data["time"] = times[i]
                    news_data["from"] = froms[i]

                    news_datas.append(news_data)
            except:
                print("关键词：%s...第%d页出现问题..." % (keyword, n))
                continue

        file_name = self.now_time + "_sogou_news_%s" % keyword + ".txt"
        with open("sogou_news/output/" + file_name, "w") as f:
            f.write(json.dumps(news_datas))

        return news_datas

    def encode_text(self, req):
        if req.encoding == 'ISO-8859-1':
            encodings = requests.utils.get_encodings_from_content(req.text)
            if encodings:
                encoding = encodings[0]
            else:
                encoding = req.apparent_encoding
        else:
            encoding = "utf-8"
        encode_content = req.content.decode(encoding, 'replace').encode('utf-8', 'replace')
        return encode_content

    def use_driver_content(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        content = ""
        for l in driver.find_elements_by_xpath("//p"):
            content += l.text
        driver.close()
        return content

    def get_news_content(self, news_datas, keyword):
        content_datas = []
        print("%s总共%d条新闻..." % (keyword, len(news_datas)))
        for new in news_datas:
            url = new["url"]
            title = new["title"]
            time_ = new["time"]
            from_ = new["from"]
            new_content = {}
            new_content["keyword"] = keyword
            new_content["url"] = url
            new_content["title"] = title
            new_content["time"] = time_
            new_content["from"] = from_
            content = ""
            print("正在抓取页面内容：%s...%s...页面\t%s..." % (keyword, new["title"], new["url"]))
            try:
                r = requests.get(url, headers = self.headers, proxies = self.proxies)
                soup = BeautifulSoup(self.encode_text(r), "lxml")
                for c in soup.find_all("p"):
                    content += c.get_text()
                if content == "":
                    content = self.use_driver_content(url)
            except:
                pass

            new_content["content"] = content
            content_datas.append(new_content)

        print("%s关键词搜索已完成..." % keyword)
        self.all_data.extend(content_datas)

        file_name = self.now_time + "_sogou_news_all_%s" % keyword + ".txt"
        with open("sogou_news/output/" + file_name, 'w') as f:
            f.write(json.dumps(content_datas))

    def time_in(self, time_):
        start = st.START
        end = st.END
        if start == "" or end == "":
            return True
        start_time = time.strptime(start, "%Y%m%d")
        end_time = time.strptime(end, "%Y%m%d")
        c_time = time.strptime(time_, "%Y%m%d")
        return start_time <= c_time and end_time >= c_time

    def write_csv(self):
        file_name = self.now_time + "_sogou_news.csv"
        with open("sogou_news/output/" + file_name, "w", encoding = 'utf-8', newline = '') as csv_file:
            csv_writer = csv.writer(csv_file)
            header_row = ["keyword", "time", "from", "title", "content", "link"]
            csv_writer.writerow(header_row)

            for new in self.all_data:
                keyword = new["keyword"]
                time_ = new["time"]
                if not self.time_in(time_):
                    continue
                from_ = new["from"]
                title = new["title"]
                new_content = new["content"]
                new_link = new["url"]
                row = [keyword, time_, from_, title, new_content, new_link]

                csv_writer.writerow(row)

    def crawl_sogou_news(self):
        keywords = st.KEYWORDS
        for keyword in keywords:
            try:
                news_datas = self.get_search_url(keyword, 50)
                self.get_news_content(news_datas, keyword)
            except:
                continue
        self.write_csv()
