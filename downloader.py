#! python3

import os, bs4, requests, re, time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def scroll_down(driver, times):
    print('Loading',end='')
    for i in range(times):
        print('.',end='')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
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
amount = str(soup.find('p',{'class':'_1u88E _1iWCF _27Bp2'}))
rr = re.compile(r'.*>(.*?)free.*')
amount = rr.findall(amount)[0].strip()
amount = int(amount.replace(',',''))
print('Total: '+ str(amount))
print('Captured: '+ str(len(link)))

count = 0
for piece in link:
    deepLk = 'https://unsplash.com' + str(piece.get('href'))
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'https://unsplash.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    deepRes = requests.get((deepLk), headers=headers)
    deepSoup = bs4.BeautifulSoup(deepRes.text, "html.parser")
    pic = deepSoup.find('img',{'class':'_2zEKz'})
    try:
        picLk = str(pic.get('src'))
    except:
        print('download failed')
    rr = re.compile(r'(.* ?)\?')
    filename = str(pic.get('alt')) + '.png'
    if picLk != 'None':
        count += 1
        picLk = rr.findall(picLk)[0]
        print('Download from ' + deepLk + ': ' + filename )
        picRes = requests.get(picLk)
        if filename == 'None.png':
            imageFile = open(os.path.join('pics', os.path.basename(picLk)+'.png'),'wb')
        else:
            imageFile = open(os.path.join('pics', filename),'wb')
        for chunk in picRes.iter_content(100000):
                imageFile.write(chunk)
        imageFile.close()
