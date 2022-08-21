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
    print('Done')


if __name__ == "__main__":

    sched = BlockingScheduler()
    sched.add_job(main,'cron', day='1, 15', hour=7, minute=30, second=0)
    sched.start()

    # main()