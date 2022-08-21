from ast import excepthandler
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


    def __crawl_gs_items(self,tag_datas):
        """
        gs 편의점 할인 페이지에서 상품정보 가져오는데 반복되는 부분 재활용용도

        Args:
            tag_datas (lits[dictionary]) : 클릭할 속성값들이 dictionary형태로 묶여 들어있는 리스트

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """

        sale_info = []


        for tags in tag_datas:

            self.driver.find_element_by_xpath(tags['btn_tab']).click()
            time.sleep(3)

            #맨 마지막 페이지로 이동
            self.driver.find_element_by_xpath(tags['btn_last_page']).click()
            time.sleep(3)

            html = self.driver.page_source
            soup = BeautifulSoup(html,"html.parser")
                
            #마지막 페이지에서 가장 마지막에 있는 숫자 페이지 확인 하여 총 페이지 수 가져옴
            num_bar = soup.find_all('span',class_ = 'num')
            num_final = num_bar[0].find_all('a')[-1].text #탭별로 0,1,2,3 인덱스를 가져야하지만 사이트가 그냥 다같이 바껴서 암거나 해도 무관
            try:
                num_final = int(num_final)
            except:
                print('페이지 마지막 번호 가져오기 에러?')
                raise

            #다시 1페이지로 복귀
            self.driver.find_element_by_xpath(tags['btn_first_page']).click()
            time.sleep(3)


            #페이지 수만큼 반복 작업
            for _ in range(num_final):
                html = self.driver.page_source
                soup = BeautifulSoup(html,"html.parser")

                #각 상품들은 prod_box 에 정보가 들어있다. 그러나 그냥 prod_box 를 가져오면 상당의 MD 추천도 가져옴, 1+1,2+1 위치가 다름
                goods = soup.select(tags['prod_box'])

                goods = goods[0]

                goods.find_all('div',class_ = 'prod_box')

                for g in goods:
                    data = {'tag' : tags['tag']}
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
                    self.driver.find_element_by_xpath(tags['btn_next_page']).click()


                    #implicitly_wait 는 기본 로딩이라 js 등에 의한 로딩은 무시?
                    #다른 대기 방법 사용해보았지만 사이트에서 로딩창이 뜨면 에러 발생 -> 무식하게 time.sleep하면 괜찮은듯? 아닌듯 가아끔 못가져오는 경우가있넹....
                    #self.driver.implicitly_wait(3)
                    #WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul/li[1]/div/p[1]')))
                    #WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul/li[1]/div/p[1]')))
                    time.sleep(5)

                except:
                    #다음버튼 눌러서 반응없이 에러나면 1+1 정보 끝난거
                    # 에러 안나고 마지막 페이지 재로드. 다른 방법 필요
                    print('다음 페이지 버튼 에러?')
                    break
        return sale_info

    
    def crawl_gs(self):
        """
        gs 편의점 할인 페이지에서 상품정보 가져옴

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """
        #gs25 할인 페이지 로드
        self.driver.get('http://gs25.gsretail.com/gscvs/ko/products/event-goods#;')
        # self.driver.implicitly_wait(2)
        #WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/ul')))
        time.sleep(5)


        tag_datas = [
            {
                'btn_tab':'//*[@id="ONE_TO_ONE"]',
                'btn_last_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/div/a[4]',
                'btn_first_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/div/a[1]',
                'prod_box':'#contents > div.cnt > div.cnt_section.mt50 > div > div > div:nth-child(3) > ul',
                'tag' : '1+1',
                'btn_next_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[1]/div/a[3]'
            },
            {
                'btn_tab':'//*[@id="TWO_TO_ONE"]',
                'btn_last_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[2]/div/a[4]',
                'btn_first_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[2]/div/a[1]',
                'prod_box':'#contents > div.cnt > div.cnt_section.mt50 > div > div > div:nth-child(5) > ul',
                'tag' : '2+1',
                'btn_next_page':'//*[@id="contents"]/div[2]/div[3]/div/div/div[2]/div/a[3]'
            }
        ]
        sale_info = self.__crawl_gs_items(tag_datas)



        self.driver.quit()
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