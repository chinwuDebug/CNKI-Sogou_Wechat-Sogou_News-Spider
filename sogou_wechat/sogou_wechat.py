from selenium import webdriver
import time
import random
import json
import requests
from bs4 import BeautifulSoup
import csv
import setting as st

class SogouWechat:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"}

        self.sogou_data = []
        self.all_data = []
        self.now_time = time.strftime("%m%d_%H%M", time.localtime(time.time()))

    def log_in(self):
        self.driver.get("http://weixin.sogou.com/")
        time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="loginBtn"]').click()

        # 请及时扫码
        time.sleep(10)

        # 判断是否登录成功
        log_in_link = self.driver.find_element_by_xpath('//*[@id="login_no"]')
        log_in_tag = log_in_link.get_attribute("style")

        if log_in_tag == "":
            count = 0
            while log_in_tag == "":
                if count > 3:
                    print("没有登录，程序自动退出")
                    return False
                log_in_link = self.driver.find_element_by_xpath('//*[@id="login_no"]')
                log_in_tag = log_in_link.get_attribute("style")
                time.sleep(10)
                count += 1
                print("请扫描二维码登录.....")

        return True

    def accuracy_keyword(self, keyword):
        return "\"" + keyword + "\""

    def get_search_web(self, keywords):
        self.driver.find_element_by_id("query").send_keys(self.accuracy_keyword(keywords[0]))
        time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="searchForm"]/div/input[3]').click()
        try:
            self.get_information(keywords[0])
        except:
            print("关键词没有内容...")
        self.next_page(keywords[0])

        if len(keywords) > 1:
            for key in keywords[1:]:
                self.driver.find_element_by_id("query").clear()
                key = self.accuracy_keyword(key)
                self.driver.find_element_by_id("query").send_keys(key)
                time.sleep(3)
                self.driver.find_element_by_xpath('//*[@id="scroll-header"]/form/div/input[1]').click()
                time.sleep(3)
                try:
                    self.get_information(key)
                except:
                    print("关键词没有内容...")
                self.next_page(key)
        self.driver.quit()

    def next_page(self, key):
        print("keyword：%s 第1页..." % key)
        count = 1
        while True:
            try:
                js = "var action=document.documentElement.scrollTop=%d" % (random.randint(1, 3) * 100)
                self.driver.execute_script(js)
                time.sleep(2)
                self.driver.find_element_by_xpath('//*[@id="sogou_next"]').click()
            except:
                print("keyword：%s 抓取结束..." % key)
                break
            time.sleep(3)
            self.get_information(key)
            count += 1
            print("keyword：%s 第%d页..." % (key, count))

    def get_information(self, key):
        items = self.driver.find_elements_by_class_name("news-list")[0].find_elements_by_class_name("txt-box")

        for item in items:
            data = {}
            try:
                link = item.find_element_by_xpath('.//*[@target="_blank"]').get_attribute("data-share")
                title = item.find_element_by_tag_name('h3').text
                from_ = item.find_elements_by_class_name("account")[0].text
                time_raw = item.find_elements_by_class_name("s2")[0].text
                if "-" not in time_raw:
                    time_ = time.strftime("%Y%m%d", time.localtime(time.time()))
                else:
                    time_ = time.strptime(time_raw, "%Y-%m-%d")
                    time_ = time.strftime("%Y%m%d", time_)

                data["keyword"] = key
                data["url"] = link
                data["title"] = title
                data["from"] = from_
                data["time"] = time_

                self.sogou_data.append(data)
            except:
                continue

    def download_data(self):
        count = 1
        print("总共抓取%d篇文章..." % len(self.sogou_data))
        for item in self.sogou_data:
            data = {}
            url = item["url"]
            try:
                r = requests.get(url, headers = self.headers)
                if r.encoding == 'ISO-8859-1':
                    encodings = requests.utils.get_encodings_from_content(r.text)
                    if encodings:
                        encoding = encodings[0]
                    else:
                        encoding = r.apparent_encoding
                else:
                    encoding = "utf-8"
                encode_content = r.content.decode(encoding, 'replace').encode('utf-8', 'replace')

                start_soup = BeautifulSoup(encode_content, "lxml")
                content = ""
                for i in start_soup.find_all("p"):
                    content += i.text
                if content == "":
                    driver = webdriver.Chrome()
                    driver.get(url)
                    content = ""
                    for l in driver.find_elements_by_xpath("//p"):
                        content += l.text
                    driver.close()
                data["content"] = content
                data["url"] = url
                data["keyword"] = item["keyword"]
                data["time"] = item["time"]
                data["title"] = item["title"]
                data["from"] = item["from"]
                print("第 %d 篇文章内容已抓取" % count)
                count += 1
                self.all_data.append(data)
            except:
                print("url:%s" % url)

    def sava_data(self, save_type):
        file_name = save_type == "all" and self.now_time + "_all.txt" or self.now_time + "_sogou_wechat.txt"
        data = save_type == "all" and self.all_data or self.sogou_data
        with open("sogou_wechat/output/" + file_name, "w") as f:
            f.write(json.dumps(data))

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
        csv_name = self.now_time + "_sogou_news.csv"
        with open("sogou_wechat/output/" + csv_name, "w", encoding = 'utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            header_row = ["keyword", "time", "from", "title", "content", "link"]
            csv_writer.writerow(header_row)

            for item in self.all_data:
                keyword = item["keyword"].replace("\"", "")
                time_ = item["time"]
                if not self.time_in(time_):
                    continue
                from_ = item["from"]
                title = item["title"]
                content = item["content"]
                link = item["url"]
                row = [keyword, time_, from_, title, content, link]

                csv_writer.writerow(row)

    def crawl_sogou_wechat(self):
        keywords = st.KEYWORDS
        log_status = self.log_in()
        if log_status:
            self.get_search_web(keywords)
            self.sava_data("sogou_wechat")
            self.download_data()
            self.sava_data("all")
            self.write_csv()
            print("全部关键词已抓取完成...")
        else:
            print("请及时用微信扫码登陆搜狗页面...重新开始...")
