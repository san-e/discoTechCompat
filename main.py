from json import dump, dumps
import urllib.request
import zlib
import argparse
from time import time
from pprint import pprint
from bs4 import BeautifulSoup
from html_table_parser.parser import HTMLTableParser
import pandas as pd
import flint as fl
from json import dump

parser = argparse.ArgumentParser(description='Parse DiscoveryGC\'s techcompat table.')
parser.add_argument('--enable-compression', help='Enable file compression when writing to disk', action="store_true")
args = parser.parse_args()

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

def get_nicknames(path_to_freelancer):
    fl.set_install_path(path_to_freelancer)

    nicknames = {}

    for ship in fl.ships:
        nicknames[ship.nickname] = ship.name()
    for equipment in fl.equipment:
        nicknames[equipment.nickname] = equipment.name()
    for commoditie in fl.commodities:
        nicknames[commoditie.nickname] = commoditie.name()
    for good in fl.goods:
        try:
            nicknames[good.nickname] = good.name()
        except TypeError:
            pass

    return nicknames

def writeData():
    to_dump = {"techcells" : get_techcells(), "definitions" : get_definitions(), "nicknames" : get_nicknames("A:/Spiele/Freelancer/Discovery Freelancer")}

    if not args.enable_compression:
        with open(f"./saves/data{int(time())}.json", "w") as f:
            dump(to_dump, f, indent=1)
    else:
        compressed = zlib.compress(dumps(to_dump).encode(), level = 9)
        with open(f"./saves/data{int(time())}.zlib", "wb") as f:
            f.write(compressed)

if __name__ == "__main__":
    writeData()