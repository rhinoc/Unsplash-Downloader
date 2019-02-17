#! python3

import os, bs4, requests, re, time, threading
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def scroll_down(driver, times):
    print('Loading',end='')
    for i in range(times):
        print('.',end='')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
    print('')

os.makedirs('pics',exist_ok=True)

keyword = input()
url = 'https://unsplash.com/search/photos/' + keyword

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
print('Setting up the driver')
driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/local/bin/chromedriver')
driver.get(url)
print('Driver prepared')

scroll_down(driver,3)
soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
link = soup.find_all('a',{'class':'_2Mc8_'})
amount = len(link)
total = str(soup.find('p',{'class':'_1u88E _1iWCF _27Bp2'}))
rr = re.compile(r'.*>(.*?)free.*')
total = rr.findall(total)[0].strip()
total = int(total.replace(',',''))
print('Total: '+ str(total))
print('Captured: '+ str(amount))


def singleDownloader(startNum, endNum):
    for piece in link[startNum:endNum]:
        deepLk = 'https://unsplash.com' + str(piece.get('href'))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://unsplash.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        deepRes = requests.get((deepLk), headers=headers)
        deepSoup = bs4.BeautifulSoup(deepRes.text, "html.parser")
        pic = deepSoup.find('img', {'class': '_2zEKz'})
        try:
            picLk = str(pic.get('src'))
            rr = re.compile(r'(.* ?)\?')
            filename = str(pic.get('alt')) + '.png'
            picLk = rr.findall(picLk)[0]
            print('Downloading from ' + deepLk + ': ' + filename)
            picRes = requests.get(picLk)
            if filename == 'None.png':
                imageFile = open(os.path.join('pics', os.path.basename(picLk) + '.png'), 'wb')
            else:
                imageFile = open(os.path.join('pics', filename), 'wb')
            for chunk in picRes.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
        except:
            print('Download failed: Can not get the download link.')

downloadThreads = []
delta = round(amount/8)
for i in range(0, amount, delta):
    endNum = min(amount - 1, i + delta - 1)
    downloadThread = threading.Thread(target=singleDownloader, args=(i, endNum))
    downloadThreads.append(downloadThread)
    downloadThread.start()

for downloadThread in downloadThreads:
    downloadThread.join()
print('Download Finished.')