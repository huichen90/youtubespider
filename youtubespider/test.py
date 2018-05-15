from youtubespider.langconv import Converter


def Traditional2Simplified(s):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''

    print(s)

    s = Converter('zh-hans').convert(s)
item = {}

item['tags'] =''      #视频的标签
list2 = ','.join(item['tags'])
simplified_sentence = Traditional2Simplified(list2)
tags = simplified_sentence.split(',')
if tags==['']:
    item['tags'] = []
item['tags'] = tags

print(item['tags'])