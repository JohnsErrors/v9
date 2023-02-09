import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from colorama import init
import pymysql
import random
import gc

init()
import os
import time

import asyncio
import aiohttp

print("Running---------------------")

async def fetch(url, session):
    #print(".",end="")
    try:
        async with session.get(url, headers=headers, timeout=20) as response:
            return await response.text(encoding='utf-8')
    except:
      return False


async def by_aiohttp_concurrency(urlsDivided: list, sitemap: int):

    async with aiohttp.ClientSession() as session:
        tasks = [] 
        for url in urlsDivided:
            tasks.append(asyncio.create_task(fetch(url, session)))

        original_result = await asyncio.gather(*tasks)
        if sitemap == 0:
          global ifSitemap
          ifSitemap = original_result
          return 0
        global globalLinkData
        global siteDomain
        global badsitecount
        for sourceXMLF in original_result:
            cleanLinksArray = []
            if sourceXMLF == False or len(sourceXMLF) < 1500:
              badsitecount += 1
              continue
            sourceXMLF = BeautifulSoup(sourceXMLF, "html.parser")
            if sourceXMLF == False:
              return
            #linkFun = sourceXMLF.findAll("a", attrs={'href': re.compile("^https://")})
            linkFun = []
            for link in sourceXMLF.findAll("a"):
                href = link.get("href")
                if href and href.startswith("https://"):
                    linkFun.append(link)
            global globalLinkData
            for href in linkFun:
              DMN = getDomain(href["href"])
              if DMN != "" and DMN != siteDomain:
                if DMN not in cleanLinksArray and len(DMN.split(".", 1)[0]) > 12 and DMN.count(".") < 2 and DMN not in globalLinkData and DMN.split(".", 1)[0] not in SearchedDomains:
                  cleanLinksArray.append(DMN)

            globalLinkData += cleanLinksArray


user_agent_desktop = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 '\
'Safari/537.36'

headers = {'User-Agent': user_agent_desktop}


def GetSource(website):
  whileVariable = 0
  while True:
    try:
      source = BeautifulSoup(
        requests.get(website, headers=headers, timeout=7).text, "html.parser")
    except:
      whileVariable += 1
      if whileVariable > 1:
        #print("x", end="")
        return False
      continue
    if source is not None:
      break
  return source


def getDomain(href):
  return urlparse(href).netloc.replace("www.", "")


def executeThread(threads, one=0):
  if one != 0:
    threads.start()
    threads.join()
    return 0
  for x in threads:
    x.start()
  for x in threads:
    x.join(timeout=7)



SearchedDomains = [
  "facebook", "youtube", "blogspot", "wordpress", "pinterest", "vote",
  "networkadvertising", "security", "vimeo", "twitter", "instagram",
  "googletagmanager", "reddit", "googlesyndication", "samsung", "amazon",
  "paypal", "doubleclick", "mozilla", "schema", "w3", "apple", "move", "imgix",
  "shopify", "judge", "serif", "google", "github", "youtu", "mailchimp",
  "wordpress"
]


def printStatistics(pages=0):
  os.system('clear')
  print("\n\n Working Program ", arraynumber, " .............")
  print("\n Website waiting to be parsed DataBase [" +
        urlsCount + "]")
  print(" Websites DataBase [" + urlsdownloadCount + "]\n")
  if pages == 0:
    print(" Checking [\033[91m" + siteDomain + "\033[39m]\n\n")
  else:
    print(" Checking [\033[91m" + siteDomain + "\033[39m] - " + str(pages) +
          "\n\n")

def divide_chunks(l, n):  
  for i in range(0, len(l), n):
    yield l[i:i + n]
    
def execute_query(query, args=None, many=False):
    countloop = 0
    while True:
        try:
            if args and many:
                cursor.executemany(query, args)
            elif args:
                cursor.execute(query, args)
            else:
                cursor.execute(query)
            break
        except mysql.connector.Error as e:
            if e.errno == 1213:
                print("Deadlock found, retrying...")
                time.sleep(1)
            else:
                print("Error:", e)
                countloop += 1
                time.sleep(1)
                if countloop > 10:
                    break



MongoDB = ""
WebToPeParsedDB = ""
WebToPeParsed_DATABASE = True

WebsitesDB = ""
Websites_DATABASE = ""
urlsCount = 0
urlsdownloadCount = 0

hostLogin = "allweb.cuy9kz7charw.us-east-1.rds.amazonaws.com"
passwordLogin = "mdkg45jrd3"
connectSql = ""    
cursor = ""


AllLinksParsed = []
globalLinkData = []
ifSitemap = []
siteDomain = ""
domainNow = ""
arraynumber = 0
badsitecount = 0

while WebToPeParsed_DATABASE:

  #Updating Data
  
  #cursor.execute("SELECT * FROM urls")
  #WebToPeParsed_DATABASE = [item[1] for item in cursor.fetchall()]
  connectSql = pymysql.connect( host=hostLogin, user="admin", password=passwordLogin, database="www")      
  cursor = connectSql.cursor()
  
  if globalLinkData != []:
    execute_query("INSERT IGNORE INTO urls (url) VALUES (%s)", globalLinkData, True)
    execute_query("INSERT IGNORE INTO urlsdownload (url) VALUES (%s)", globalLinkData, True)
  
  execute_query("SELECT * FROM urls ORDER BY RAND() LIMIT 1;")
  domainNow = cursor.fetchone()[1]
  execute_query('DELETE FROM urls WHERE url = "' + domainNow + '"')
  connectSql.commit()
  
  execute_query("SELECT COUNT(*) FROM urls")
  urlsCount = str(cursor.fetchone()[0])
  execute_query("SELECT COUNT(*) FROM urlsdownload")
  urlsdownloadCount = str(cursor.fetchone()[0])
  
  cursor.close()
  connectSql.close()
  del connectSql
  del cursor
  #Database finished

  url = "https://" + domainNow + "/sitemap.xml"
  siteDomain = getDomain(url)
  print("Sitemap ", arraynumber, " -- ", domainNow + " .....")

  AllLinksParsed = []
  globalLinkData = []

  sourceXML = GetSource(url)
  if sourceXML == False:
    continue
  sitemap = sourceXML.findAll("loc")

  #First Sitemap
  xlmToContinue = []
  for x in sitemap:
    if ".xml" not in x.text:
      AllLinksParsed.append(x.text)
    else:
      xlmToContinue.append(x.text)
  
  #Second Sitemap
  ifSitemap=[]
  asyncio.run(by_aiohttp_concurrency(xlmToContinue,0))
  gc.collect()
  for sourceXML2 in ifSitemap:
    if sourceXML2 == False:
      continue
    sourceXML2 = BeautifulSoup( sourceXML2, "html.parser")
    if sourceXML2 == False:
      continue
    sitemap2 = sourceXML2.findAll("loc")
    for x2 in sitemap2:
      if ".xml" in x2.text:
        print(x2)
      else:
        AllLinksParsed.append(x2.text)

  printStatistics(len(AllLinksParsed))

  if len(AllLinksParsed) > 10000:
    AllLinksParsed = AllLinksParsed[:10000]
  badsitecount = 0

  if AllLinksParsed != []:
    ThreadsDiveded = list(divide_chunks(AllLinksParsed, 1500))
    for thread in ThreadsDiveded:
      start_time = time.time()
      asyncio.run(by_aiohttp_concurrency(thread, 1))
      gc.collect()
      if badsitecount > 500:
        print("Bad Site")
        break
      print("Sites [",len(globalLinkData), "] Time [",int(time.time() - start_time)/(len(AllLinksParsed)/100),"s/100th ]\n")
      
  print("Number of sites added: ", len(globalLinkData))
