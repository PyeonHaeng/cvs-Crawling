import sale_crawling
import time
import firebase_store
import firebase_realtime
from apscheduler.schedulers.blocking import BlockingScheduler
def main():
    crawer=sale_crawling.SaleCrawler()
    #firebase_db = firebase_store.FirebaseStore()
    firebase_db = firebase_realtime.FirebaseRealtime()
    
    gs_sale_data = crawer.crawl_gs()

    gs_addi = {
        'enable':True,
        'store':'gs'}
    firebase_db.set_datas(gs_sale_data,gs_addi)
    print('Done Gs25')


    time.sleep(10)
    
    cu_sale_data = crawer.crawl_cu()

    cu_addi = {
        'enable':True,
        'store':'cu'}
    firebase_db.set_datas(cu_sale_data,cu_addi)
    print('Done CU')

    time.sleep(10)

    seven_eleven_sale_data = crawer.crawl_seven_eleven()

    seven_eleven_addi = {
        'enable':True,
        'store':'7-eleven'}
    firebase_db.set_datas(seven_eleven_sale_data,seven_eleven_addi)
    print('Done 7-ELEVEn')
    
    time.sleep(10)

    mini_stop_sale_data = crawer.crawl_mini_stop()

    mini_stop_addi = {
        'enable':True,
        'store':'ministop'}
    firebase_db.set_datas(mini_stop_sale_data,mini_stop_addi)
    print('Done ministop')

    time.sleep(10)

    emart24_sale_data = crawer.crawl_emart24()

    emart24_addi = {
        'enable':True,
        'store':'emart24'}
    firebase_db.set_datas(emart24_sale_data,emart24_addi)
    print('Done emart24')

    del crawer


if __name__ == "__main__":

    sched = BlockingScheduler()
    sched.add_job(main,'cron', day='1, 15', hour=7, minute=30, second=0)
    sched.start()

    # main()