from ast import excepthandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import enum
import pickle

class ConvName(enum.Enum):
    GS25=0
    CU=1
    SevenEleven = 2
    MiniStop = 3
    EMart24 = 4



class SaleCrawler:
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.implicitly_wait(3)



    def __check_img_link(self,link,conv_name = 0):
        """
        이미지 링크의 무결성 확인
        이미지 링크 에러시 null 반환

        Args:
            link (string) :  확인할 링크
            cov_name : 편의 점 이름

        Return:
            고친 링크 반환, 문제 있는 링크시 null값 반환
        """
        if conv_name == ConvName.CU.value:
            link = 'http' + link
        elif conv_name == ConvName.SevenEleven.value:
            link = 'https://www.7-eleven.co.kr' + link


        if requests.get(link).status_code != 200:
            return None
        
        return link



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
                        data['name'] = None
                        print(f'이름 찾기 에러 : {g}')

                    try:
                        data['img'] = self.__check_img_link(g.find('p', class_ ='img').find('img').get('src'))
                    except:
                        data['img'] = None
                        print(f'그림찾기 에러 : {data["name"]} - {g}')

                    try:
                        data['price'] = g.find('span', class_ = 'cost').text
                    except:
                        data['price'] = None
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

    

    def crawl_gs(self) -> dict:
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



    def __crawl_cu_items(self,tag_datas):
        """
        cu 편의점 할인 페이지에서 상품정보 가져오는데 반복되는 부분 재활용용도

        Args:
            tag_datas (lits[dictionary]) : 클릭할 속성값들이 dictionary형태로 묶여 들어있는 리스트

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """

        sale_info = []


        for tags in tag_datas:
            
            self.driver.find_element_by_xpath(tags['btn_tab']).click()
            time.sleep(3)

            #하단의 더보기를 한계까지 누르기
            while True:
                try:
                    self.driver.find_element_by_xpath(tags['btn_next_page']).click()
                    time.sleep(3)
                except:
                    break

            html = self.driver.page_source
            soup = BeautifulSoup(html,"html.parser")

            #각 상품들은 div 하단의 ul들 안에 li 안에 들어있다.
            goods_list = soup.select(tags['prod_list_wrap'])[0].find_all('ul')

            for goods in goods_list:
                goods_boxes = goods.find_all('li',class_ ='prod_list')
                for g in goods_boxes:
                    data = {'tag' : tags['tag']}
                    try:
                        data['name'] = g.find('div',class_ = 'name').find('p').text
                    except:
                        data['name'] = None
                        print(f'이름 찾기 에러 : {g}')

                    try:
                        data['img'] = self.__check_img_link(g.find('img', class_ ='prod_img').get('src'),ConvName.CU.value)
                    except:
                        data['img'] = None
                        print(f'그림찾기 에러 : {data["name"]} - {g}')

                    try:
                        data['price'] = g.find('div', class_ = 'price').find('strong').text
                    except:
                        data['price'] = None
                        print(f'가격찾기 에러 : {data["name"]} - {g}')


                    sale_info.append(data)
            time.sleep(3)

            #새로고침 , 안하면 왜인지 2+1 탭 버튼 누를때 에러 발생
            self.driver.refresh()
            time.sleep(3)
        return sale_info



    def crawl_cu(self) -> dict:
        """
        cu 편의점 할인 페이지에서 상품정보 가져옴

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """
        #cu 할인 페이지 로드
        self.driver.get('https://cu.bgfretail.com/event/plus.do?category=event&depth2=1&sf=N')
    
        time.sleep(5)


        tag_datas = [
            {
                'btn_tab':'//*[@id="contents"]/div[1]/ul/li[2]/a',
                'btn_next_page':'//*[@id="contents"]/div[2]/div/div/div[1]/a',
                'prod_list_wrap':'#contents > div.relCon > div',
                'tag' : '1+1'
            },
            {
                'btn_tab':'//*[@id="contents"]/div[1]/ul/li[3]/a',
                'btn_next_page':'//*[@id="contents"]/div[2]/div/div/div[1]/a',
                'prod_list_wrap':'#contents > div.relCon > div',
                'tag' : '2+1'
            }
        ]
        sale_info = self.__crawl_cu_items(tag_datas)

        self.driver.quit()
        return sale_info



    def __crawl_seven_eleven_items(self,tag_datas):
        """
        7-ELEVEn 편의점 할인 페이지에서 상품정보 가져오는데 반복되는 부분 재활용용도

        Args:
            tag_datas (lits[dictionary]) : 클릭할 속성값들이 dictionary형태로 묶여 들어있는 리스트

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """

        sale_info = []


        for tags in tag_datas:
            
            self.driver.find_element_by_xpath(tags['btn_tab']).click()
            time.sleep(3)

            first_flag = True

            #하단의 더보기를 한계까지 누르기
            while True:
                try:
                    if first_flag:
                        self.driver.find_element_by_xpath(tags['btn_first_next_page']).click()
                        first_flag = False
                        time.sleep(3)
                    else:
                        self.driver.find_element_by_xpath(tags['btn_next_page']).click()
                        time.sleep(3)
                except:
                    break

            html = self.driver.page_source
            soup = BeautifulSoup(html,"html.parser")

            #각 상품들은 div 하단의 li 안에 들어있다. , 만 앞의 1+1 등 표시하는 건 제외
            goods_list = soup.select(tags['prod_list_wrap'])[0].find_all('li',class_ = False)[1:]
            
            for g in goods_list:
                data = {'tag' : tags['tag']}
                try:
                    data['name'] = g.find('div',class_ = 'name').text
                except:
                    data['name'] = None
                    print(f'이름 찾기 에러 : {g}')

                try:
                    data['img'] = self.__check_img_link(g.find('div', class_ ='pic_product').find('img').get('src'),ConvName.SevenEleven.value)
                except:
                    data['img'] = None
                    print(f'그림찾기 에러 : {data["name"]} - {g}')

                try:
                    data['price'] = g.find('div', class_ = 'price').text.strip()
                except:
                    data['price'] = None
                    print(f'가격찾기 에러 : {data["name"]} - {g}')


                sale_info.append(data)
            time.sleep(3)
        return sale_info

    def crawl_seven_eleven(self) -> dict:
        """
        7-ELEVEn 편의점 할인 페이지에서 상품정보 가져옴

        Return:
            list 안에 dictionary로 상품정보들이 들어있음
        """
        #cu 할인 페이지 로드
        self.driver.get('https://www.7-eleven.co.kr/product/presentList.asp')
    
        time.sleep(5)


        tag_datas = [
            {
                'btn_tab':'//*[@id="actFrm"]/div[3]/div[1]/ul/li[1]/a',
                'btn_first_next_page':'//*[@id="listUl"]/li[15]/a',
                'btn_next_page' : '//*[@id="moreImg"]/a',
                'prod_list_wrap':'#listDiv > div',
                'tag' : '1+1'
            },
            {
                'btn_tab':'//*[@id="actFrm"]/div[3]/div[1]/ul/li[2]/a',
                'btn_first_next_page':'//*[@id="listUl"]/li[15]/a',
                'btn_next_page' : '//*[@id="moreImg"]/a',
                'prod_list_wrap':'#listDiv > div',
                'tag' : '2+1'
            }
        ]
        sale_info = self.__crawl_seven_eleven_items(tag_datas)

        self.driver.quit()
        return sale_info

