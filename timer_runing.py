import schedule
import time
from datetime import datetime
from BaiduHttpRequest import get_traffic_of_wujiaochang


def time_run():
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


schedule.every(10).minutes.do(get_traffic_of_wujiaochang)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
