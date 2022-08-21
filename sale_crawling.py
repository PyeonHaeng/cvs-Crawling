from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pickle


class SaleCrawler:
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.implicitly_wait(3)

    def crawl_gs(self):
        #gs25 할인 페이지 로드
        self.driver.get('http://gs25.gsretail.com/gscvs/ko/products/event-goods#;')
        # self.driver.implicitly_wait(2)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul')))

        sale_info = []
        #우선 1+1 행사 부터 처리
        while True:
            html = self.driver.page_source
            soup = BeautifulSoup(html,"html.parser")

            #각 상품들은 prod_box 에 정보가 들어있다. 그러나 그냥 prod_box 를 가져오면 상당의 MD 추천도 가져옴, 1+1,2+1 위치가 다름
            goods = soup.select('#contents > div.cnt > div.cnt_section.mt50 > div > div > div:nth-child(3) > ul')

            goods = goods[0]

            goods.find_all('div',class_ = 'prod_box')

            for g in goods:
                data = {'tag' : '1+1'}
                try:
                    data['name'] = g.find('p',class_ = 'tit').text
                except:
                    data['name'] = 'error'
                    print(f'이름 찾기 에러 : {g}')


                try:
                    data['img'] = g.find('p', class_ ='img').find('img').get('src')
                except:
                    data['img'] = 'error'
                    print(f'그림찾기 에러 : {data["name"]} - {g}')


                try:
                    data['price'] = g.find('span', class_ = 'cost').text
                except:
                    data['price'] = 'error'
                    print(f'가격찾기 에러 : {data["name"]} - {g}')


                sale_info.append(data)

            try:
                self.driver.find_element_by_xpath('//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/div/a[3]').click()


                #implicitly_wait 는 기본 로딩이라 js 등에 의한 로딩은 무시?
                #다른 대기 방법 사용해보았지만 사이트에서 로딩창이 뜨면 에러 발생 -> 무식하게 time.sleep하면 괜찮은듯?
                #self.driver.implicitly_wait(3)
                #WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul/li[1]/div/p[1]')))
                #WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul/li[1]/div/p[1]')))
                time.sleep(5)

            except:
                #다음버튼 눌러서 반응없이 에러나면 1+1 정보 끝난거
                # 에러 안나고 마지막 페이지 재로드. 다른 방법 필요
                break
        return sale_info

    def test(self):
        self.driver.get('http://gs25.gsretail.com/gscvs/ko/products/event-goods#;')
        self.driver.implicitly_wait(2)
        self.driver.find_element_by_xpath('//*[@id="GIFT"]').click()
        self.driver.implicitly_wait(2)
        self.driver.find_element_by_xpath('//*[@id="contents"]/div[2]/div[3]/div/div/div[3]/div/a[4]').click()
        self.driver.implicitly_wait(2)
        
        
        html = self.driver.page_source
        soup = BeautifulSoup(html,"html.parser")
        num_bar = soup.find_all('span',class_ = 'num')
        test = num_bar[2].find_all('a')
        print(test[-1].text)
        

c = SaleCrawler()
data = c.crawl_gs()
print(data)
print(len(data))
with open("data.pickle","wb") as fw:
    pickle.dump(data,fw)