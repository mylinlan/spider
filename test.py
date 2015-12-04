# -*- coding:utf-8 -*-
import requests
import re
import json

response = requests.get('http://interface.sina.cn/dfz/jx/news/index.d.html?callback=jsonp1449208211944&page=50&ch=zhengwen&cid=73350')
# s= "\u8d35\u9633\u9910\u9986\u5f15\u8fdb\u201c\u5965\u7279\u66fc\u201d \u4e13\u4e3a\u987e\u5ba2\u524a\u9762\u6761"
# s = s.decode("unicode_escape")
print type(response)
s = response.text
if not s:
    print '没有字符串'

s = s.decode("unicode_escape")
# s = s.encode('utf-8').replace('\\', '').strip()
s = s.strip().replace('\r', '').replace('\n', '')
print s
s = s[19:-1]
print '\n'
dict_json = json.loads(s)
print dict_json
result_list = dict_json["result"]["data"]["list"]
for each in result_list:
    print each['title']
    print each['URL']
    print each['fpTime']
    print '\n'

# me = re.findall(u'\((.*?)\)', s)
