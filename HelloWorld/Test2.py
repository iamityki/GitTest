#fiter out live ids from a url
from urllib.request import urlopen

def filterLiveIds(url):
    html = urlopen(url)
    liveids = set()
    bsObj = BeautifulSoup(html,"html.parser")
    for link in bsObj.findAll("a",href=re.compile("^(/l/)")):
        if "href" in link.attrs:
            newPage = link.attrs['href']
            liveId = re.findall("[0-9]+",newPage)
            liveIds.add(liveId[0])
    return liveIds

def getUserId(liveId):
    html = urlopen("http://www.huajiao.com/" + "l/" + str(liveId))
    bsObj = BeautifulSoup(html,"html.parser")
    text = bsObj.title.get_text()
    res = re.findall("[0-9]+",text)
    return res[0]

