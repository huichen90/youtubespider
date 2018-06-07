import json
import requests
import hashlib

class Translate(object):
    def __init__(self,q):
        self.url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

        self.q = q
        self.from1 = 'auto'
        self.to='zh'
        self.appid=20180607000173223
        self.salt = 123

        '''生成秘钥sign'''
        self.pwd = 'Gy4Mzn0ILDyD9fS3iuzf'
        str1 = str(self.appid)+self.q+str(self.salt)+self.pwd
        m = hashlib.md5()
        str1 = str1.encode(encoding='UTF-8',errors='strict')
        m.update(str1)
        self.sign = m.hexdigest()

    def translate(self):
        params = {'q':self.q,'from':self.from1,'to':self.to,'appid':self.appid,'salt':self.salt,'sign':self.sign}

        response = requests.get(url=self.url, params=params)
        result = response.text
        result = json.loads(result)

        return result['trans_result'][0]['dst']

if __name__ == '__main__':
    t = Translate(q='hello world!')
    rsl = t.translate()
    print(rsl)