import sale_crawling
import firebase_store
from apscheduler.schedulers.blocking import BlockingScheduler
def main():
    crawer=sale_crawling.SaleCrawler()
    firebase_db = firebase_store.FirebaseStore()

    gs_sale_data = crawer.crawl_gs()

    gs_addi = {
        'enable':True,
        'store':'gs'}
    firebase_db.set_datas(gs_sale_data,gs_addi)
    print('Done Gs25')


    cu_sale_data = crawer.crawl_cu()

    cu_addi = {
        'enable':True,
        'store':'cu'}
    firebase_db.set_datas(cu_sale_data,cu_addi)
    print('Done CU')


    seven_eleven_sale_data = crawer.crawl_seven_eleven()

    seven_eleven_addi = {
        'enable':True,
        'store':'7-eleven'}
    firebase_db.set_datas(seven_eleven_sale_data,seven_eleven_addi)
    print('Done 7-ELEVEn')


if __name__ == "__main__":

    # sched = BlockingScheduler()
    # sched.add_job(main,'cron', day='1, 15', hour=7, minute=30, second=0)
    # sched.start()

    main()