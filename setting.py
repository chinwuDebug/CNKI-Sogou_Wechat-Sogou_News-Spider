######################### 抓取参数配置 #########################
# 指定抓取的时间范围
# 必须同时指定或者同时不指定
# e.g. START = "20140101"  END = "20180101"
# default START = ""  END = ""
START = ""
END = ""

# 抓取源选择
# ["sogou_news", "sogou_wechat", "cnki_journal", "cnki_from"]
DATA_FROM = "cnki_from"

# 抓取关键词
# ["keyword1", "keyword2",]
KEYWORDS = ["高分八号", "高分九号"]

# 知网期刊
# ["测绘学报", "测绘通报",]
JOURNAL = ["测绘科学"]

# 指定知网来源
# ["武汉大学",]
FROMS = ["武汉测绘院"]

# 知网的账号
CNKI_USER = ''
CNKI_PASSWD = ''


######################### IP代理/打码 #########################
### ip代理功能
# ip隧道信息
# 这里用的是阿布云做代理
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"
# 代理隧道验证信息
proxyUser = ""
proxyPass = ""


### 打码平台信息
# 如果抓取知网数据，识别验证码识别的出来，请不要改
# 云打码平台
username = ''
password = ''
appid = 0
appkey = ''