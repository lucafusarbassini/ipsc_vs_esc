"""
A disordered script for extracting Affymetrix data from different GEO datasets 
and create a unified dataset, given the urls of the gene expression tables
"""

import urllib2
from bs4 import BeautifulSoup
import re
from openpyxl import Workbook
import string
import pandas as pd

df = pd.ExcelFile('urls_complete.xlsx').parse('samples_with_urls')
urls = [str(df['URL'][i]) for i in range(len(df)) if str(df['URL'][i])!='nan']
print(urls)

list_dics = []
set_id = set()

book = Workbook()
sheet = book.active

x = string.ascii_uppercase
col_indexes = list(x) + list([x[i]+x[j] for i in range(len(x)) for j in range(len(x))])
col_indexes = col_indexes[1:len(urls)+1]
print(col_indexes)

type_of_measure = []
for url in urls:
    print(url)
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html)
    for script in soup(["script", "style"]):
        script.decompose()
        script.extract() 
        strips = str(list(soup.stripped_strings)[-1])
        dictionary = {}
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)[:80]
    tm = text[text.find("#VALUE")+8: text.find("#VALUE")+18].replace(" ", "").lower()
    fund = re.match(r"(\w+)\t(-?\d+.\d+)", strips.splitlines( )[0].replace("-", "_"))
    if fund != None:
        lol = fund.group(1)
    else:
        lol = '675'
    if ('log2' in tm or 'rma' in tm) and '78' in lol:
        for j in strips.splitlines( ):
            result = re.match(r"(\w+)\t(-?\d+.\d+)", j.replace("-", "_"))
            if result != None:
                gene = result.group(1)
                value = result.group(2)
                dictionary[gene] = value
    list_dics.append(dictionary)
    id_now = list(dictionary.keys())
    for k in id_now:
        set_id.add(k)
   
l_set_id = list(set_id)
sheet['A1'] = 'Gene ID'
for k, col in enumerate(col_indexes):
    sheet[col+'1'] = 'Sample' + str(k+1) #+ "..." + str(type_of_measure[k])

for i in range(2, len(l_set_id)+2):
    sheet['A'+str(i)] = str(l_set_id[i-2])
    # sheet['B'+str(i)] = list_dics[0][l_set_id[i-2]]
    for j, colind in enumerate(col_indexes):
        print(colind+str(i))
        #if l_set_id[i-2] in list_dics[j].keys():
        sheet[colind+str(i)] = list_dics[j].get(l_set_id[i-2], 'N/A')
        #else:
         #   sheet[colind+str(i)] = 'N/A'


book.save("dataset_ipsc3.xlsx")


