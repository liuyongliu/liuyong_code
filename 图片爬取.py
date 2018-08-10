# coding:utf-8
import requests
from lxml import html
import os
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing 
import re
from multiprocessing import Pool

def header(referer):
    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/59.0.3071.115 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }
    return headers

# 获取主页列表
def getPage(pageNum):
    baseUrl = 'http://www.mzitu.com/page/{}'.format(pageNum)
    try:
        selector = html.fromstring(requests.get(baseUrl,timeout=(3.09,20)).content)
    except:
        return []
    urls = []
    for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
        urls.append(i)
    return urls


# 图片链接列表， 标题
# url是详情页链接
def getPiclink(url):
    try:
        sel = html.fromstring(requests.get(url,timeout=(3.09,20)).content)
    except:
        return None
    # 图片总数
    total = sel.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
    # 标题
    title = sel.xpath('//h2[@class="main-title"]/text()')[0]
    # 文件夹格式
    dirName = u"[第{}页].[共{}张].{}".format(pag_2,total,title)
    dirName = dirName.replace(":","")
    dirName = dirName.replace("?","")
    dirName = dirName.replace("\\","")
    dirName = dirName.replace("*","")
    dirName = dirName.replace("/","")
    ll = []
    lll = []
    for parent,dirnames,filenames in os.walk(os.path.abspath('.')):
        ll.append(parent)
    for k in ll:
        s = re.findall(r'.+张]\.(.*)',k)
        if s == [] :
            ll.remove(k)
        else:
            lll.append(s[0])

    s = re.findall(r'.+张]\.(.*)',dirName)[0]
    if s not in lll:
        os.mkdir(dirName)
    else:
        print('目录名重复')
        return None
    try:
        total = int(total)
    except:
        total = 1
    n = 1
    for i in range(total):
        try:
            link = '{}/{}'.format(url, i+1)
            try:
                s = html.fromstring(requests.get(link,timeout=(3.09,20)).content)
            except:
                continue
            jpgLink = s.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
            try:
                img = requests.get(jpgLink, headers=header(jpgLink),timeout=(3.09,20)).content
            except:
                continue
            filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirName, n)
            print(u'正在下载:第%s页-第%s张-共%s张-%s' % (pag_2, n,total,title))          
            with open(filename, "wb+") as jpg:
                jpg.write(img)
            n += 1
        except:
            pass

def start_heiheihei(pageNum):
    global pag_2
    pag_2 = pageNum
    p = getPage(pageNum)
    if p == []:
        return None
    with ThreadPool(5) as pool:
        pool.map(getPiclink, p)
    pool.close()
    pool.join()
    

if __name__ == '__main__':
    multiprocessing.freeze_support()
    start = datetime.datetime.now()
    result = [x for x in range(1,188)]
    p = Pool(4)
    r = p.map(start_heiheihei,result)
    p.close()
    p.join()
    end = datetime.datetime.now()
    runtime = str((end-start).seconds)
    print(runtime)



