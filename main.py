import sale_crawling
import time
#import firebase_store
from sql import SQL
#import firebase_realtime
#from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
#from push_notification import PushNotificationModule

def main():
    crawer=sale_crawling.SaleCrawler()

    conn = SQL("root", "password", "192.168.50.206", "conv_sale")
    
    

    sync_key = datetime.now().strftime('%Y:%m') #양식은 2022:11

    gs_sale_data = crawer.crawl_gs()

    gs_addi = {
        'enable':True,
        'store':'GS25'}
    conn.set_datas(gs_sale_data,gs_addi,sync_key)
    print('Done Gs25')


    time.sleep(10)
    
    cu_sale_data = crawer.crawl_cu()

    cu_addi = {
        'enable':True,
        'store':'CU'}
    conn.set_datas(cu_sale_data,cu_addi,sync_key)
    print('Done CU')

    time.sleep(10)

    seven_eleven_sale_data = crawer.crawl_seven_eleven()

    seven_eleven_addi = {
        'enable':True,
        'store':'7-ELEVEn'}
    conn.set_datas(seven_eleven_sale_data,seven_eleven_addi,sync_key)
    print('Done 7-ELEVEn')
    
    time.sleep(10)

    mini_stop_sale_data = crawer.crawl_mini_stop()

    mini_stop_addi = {
        'enable':True,
        'store':'MINISTOP'}
    conn.set_datas(mini_stop_sale_data,mini_stop_addi,sync_key)
    print('Done ministop')

    time.sleep(10)

    emart24_sale_data = crawer.crawl_emart24()

    emart24_addi = {
        'enable':True,
        'store':'emart24'}
    conn.set_datas(emart24_sale_data,emart24_addi,sync_key)
    print('Done emart24')


    conn.set_sync_key(sync_key)


    print('Done update sync_key')




    month = datetime.now().month
    PushNotificationModule().send_push(title=f'{month}월 제품 업데이트',body=f'{month}월 제품 업데이트가 완료되었습니다!')

    del crawer


if __name__ == "__main__":

    sched = BlockingScheduler()
    #sched.add_job(main,'cron', day='1, 15', hour=7, minute=30, second=0)
    sched.add_job(main,'cron', day='1', hour=0, minute=5, second=0)

    sched.start()

    #main()