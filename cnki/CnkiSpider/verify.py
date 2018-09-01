import http.client, mimetypes, urllib, json, time, requests
import setting as st
import random
from urllib.parse import quote


######################################################################

class YDMHttp:
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files = []):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if (response):
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files = []):
        for key in files:
            files[key] = open(files[key], 'rb')
        res = requests.post(url, files = files, data = fields)
        return res.text


######################################################################
username = st.username
password = st.password
appid = st.appid
appkey = st.appkey


def ydmInit(fn = 'ckcode.gif', ct = 1006, timeout = 60):
    yundama = YDMHttp(username, password, appid, appkey)
    yundama.login()
    cid, result = yundama.decode(fn, ct, timeout)
    return result


def getCkCode(headers, cookies):
    url = 'http://kns.cnki.net' + '/kns/checkcode.aspx?t=' + str(random.random())
    r = requests.get(url, headers = headers, cookies = cookies)
    with open('ckcode.gif', 'wb') as f:
        f.write(r.content)
        f.close()


def botCheck(url, vc, headers, cookies, i):
    params = {
        'rurl': url,
        'vericode': vc
    }

    if i >= 60:
        params = {
            'rurl': url,
            'vericode': vc,
            'skey': "CheckMaxTurnPageCount"
        }
        time.sleep(random.randint(5, 10))

    r = requests.get('http://kns.cnki.net/kns/brief/vericode.aspx', headers = headers, params = params,
                     cookies = cookies)

    count = 0
    while '验证码错误' in r.text:
        print("验证码错误，正在重新识别...")
        count += 1
        if count > 6:
            return 0
        getCkCode(headers, cookies)
        vc = ydmInit()
        params = {
            'rurl': url,
            'vericode': vc
        }

        if i >= 60:
            params = {
                'rurl': url,
                'vericode': vc,
                'skey': "CheckMaxTurnPageCount"
            }
            time.sleep(random.randint(5, 10))
        r = requests.get('http://kns.cnki.net/kns/brief/vericode.aspx', headers = headers, params = params,
                     cookies = cookies)


if __name__ == '__main__':
    pass
    url = 'http://kns.cnki.net' + '/kns/checkcode.aspx?t=' + str(random.random())
    r = requests.get(url)
