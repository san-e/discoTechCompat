import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd

def url_get_contents(url):
    request = urllib.request.Request(url=url)
    open = urllib.request.urlopen(request)
    return open.read()

xhtml = url_get_contents('https://discoverygc.com/techcompat/techcompat_table.php').decode('utf-8')

parser = HTMLTableParser()
parser.feed(xhtml)

df = pd.DataFrame(parser.tables[0])

delete = []
for x in df.index:
    if x != 0:
        if x % 11 == 0:
            delete.append(x)
df = df.drop(index=delete)
delete = []
for x in df.columns:
    if x != 0:
        if x % 11 == 0:
            delete.append(x)
for x in delete:
    del df[x]
df = df.reset_index(drop=True)
df.columns = range(df.columns.size)
dict = {}
for x in range(0, len(df[0])):
    dict[x] = df[0][x]
del dict[0]