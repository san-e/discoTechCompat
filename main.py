from json import dump, dumps
import urllib.request
import zlib
from pprint import pprint
from bs4 import BeautifulSoup
from html_table_parser.parser import HTMLTableParser
import pandas as pd
from json import dump

def url_get_contents(url):
    request = urllib.request.Request(url=url)
    open = urllib.request.urlopen(request)
    return open.read()

html = url_get_contents('https://discoverygc.com/techcompat/techcompat_table.php').decode('utf-8')

def get_techcells():
    parser = HTMLTableParser()
    parser.feed(html)

    df = pd.DataFrame(parser.tables[0])

    delete = [len(df)-1]
    for x in range(len(df)):
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
    faction_names = {}
    for x in range(1, len(df)):
        faction_names[x] = df[0][x]

    tech_categories = {}
    for x in range(1, len(df.columns)):
        tech_categories[x] = df[x][0]

    final = {}
    ae = {}

    for row in range(1, len(df)):
        for column in range(1, len(df.columns)):
            ae[tech_categories[column]] = int(df[column][row].strip('%')) if df[column][row] != '' else 0
        final[faction_names[row]] = ae
        ae = {}
    return final

def get_definitions():
    data = BeautifulSoup(html, 'html.parser')
    data = data.find('ul', {"id": "techcompat_techs"})
    names_are_hard = {}
    for li in data.find_all("li"):
        temp = str(li).split("br/>")[1]
        temp = temp.split("</li>")[0]
        temp = temp.split(", ")
        names_are_hard[li.find('strong').text] = temp
        temp = ""
    return names_are_hard

with open("data.json", "w") as f:
    dump({"Techcells" : get_techcells(), "Definitions" : get_definitions()}, f, indent=1)

#compressed = zlib.compress(dumps({"Techcells" : get_techcells(), "Definitions" : get_definitions()}, indent=1).encode(), level = 9)
# with open("data.json", "wb") as f:
#     f.write(compressed)
