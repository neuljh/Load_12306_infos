import os
import re
import time
import pandas as pd
import requests


def getStationName():
    # 爬取12306网站所有车站名称信息 https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9315
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9315'  # 车站信息控件
    r = requests.get(url)
    # 北京北|VAP|beijingbei|bjb|0|0357|北京 ([\u4e00-\u9fa5]+)\|([A-Z]+)\|([a-z]+)\|([a-z]+)\|([0-9]+)\|([0-9]+)\|([\u4e00-\u9fa5]+)
    pattern = '([\u4e00-\u9fa5]+)\|([A-Z]+)\|([a-z]+)\|([a-z]+)\|([0-9]+)\|([0-9]+)\|([\u4e00-\u9fa5]+)'  # 正则匹配规则
    results = re.findall(pattern, r.text)
    stationName = dict()  # 所有车站信息，转换为字典
    for result in results:
        station_name = result[0]
        station_code = result[1]
        city_name = result[-1]
        station_dict = dict(
            code=station_code,
            city=city_name,
        )
        stationName[station_name] = station_dict
    # print(stationName)
    return stationName

def get_station_info_by_station_code(text, search_station_code):
    for station_name, station_dict in text.items():
        if station_dict['code'] == search_station_code:
            station_info = list()
            station_info.append((station_name, search_station_code))
            return station_info
    return '404 Not Found'

def get_station_info_by_station_name(text, search_station_name):
    for station_name, station_dict in text.items():
        if search_station_name in station_name:
            station_info = list()
            station_info.append((search_station_name, station_dict['code']))
            return station_info
    return '404 Not Found'

def get_station_infos_by_city_name(text, city_name):
    station_infos = list()
    for station_name, station_dict in text.items():
        station_code = station_dict['code']
        station_city = station_dict['city']
        if city_name in station_city:
            station_infos.append((station_name, station_code))
    return station_infos

def get_station_name_by_station_code(text, search_station_code):
    for station_name, station_dict in text.items():
        if station_dict['code'] == search_station_code:
            return station_name
    return '404 Not Found'

def get_visit_url(text, date, from_station, to_station):
    # 构建用于查询列车车次信息的url
    # 参数：日期，出发地，到达地
    # key为车站名称， value为车站代号
    # https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E5%8C%97%E4%BA%AC,BJP&ts=%E4%B8%8A%E6%B5%B7,SHH&date=2024-08-06&flag=N,N,Y

    date = date
    from_station = from_station + "," + text[from_station]['code']
    to_station = to_station + "," + text[to_station]['code']  # 新的url
    url = ("https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&"
           "fs={}"
           "&ts={}"
           "&date={}"
           "&flag=N,N,Y"
           ).format(from_station, to_station, date)
    return url

def get_query_url(text, date, from_station, to_station):
    # 构建用于查询列车车次信息的url
    # 参数：日期，出发地，到达地
    # key为车站名称， value为车站代号

    date = date
    from_station = text[from_station]['code']
    to_station = text[to_station]['code']    # 新的url
    url = ("https://kyfw.12306.cn/otn/leftTicket/queryE?leftTicketDTO.train_date={}"
           "&leftTicketDTO.from_station={}"
           "&leftTicketDTO.to_station={}"
           "&purpose_codes=ADULT"
           ).format(date, from_station, to_station)
    return url


def get_price_url(text, date, from_station, to_station):
    # 构建用于查询列车车次信息的url
    # 参数：日期，出发地，到达地
    # key为车站名称， value为车站代号

    date = date
    from_station = text[from_station]['code']
    to_station = text[to_station]['code']  # 新的url

    url = ("https://kyfw.12306.cn/otn/leftTicketPrice/query?leftTicketDTO.train_date={}"
           "&leftTicketDTO.from_station={}"
           "&leftTicketDTO.to_station={}"
           ).format(date, from_station, to_station)
    return url

def get_price(text, date, from_station, to_station, save_path):
    try:
        time.sleep(1)
        url = get_price_url(text, date, from_station, to_station)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': '_uab_collina=172278338146569329543907; JSESSIONID=311C0BF81C626DE378087B1BA852FABA; BIGipServerpassport=1005060362.50215.0000; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_wfdc_flag=dc; route=c5c62a339e7744272a54643b3be5bf64; _jc_save_fromDate=2024-08-06; BIGipServerportal=3067347210.16671.0000; BIGipServerotn=1173357066.50210.0000; _jc_save_fromStation=%u4E0A%u6D77%2CSHH; _jc_save_toStation=%u5317%u4EAC%2CBJP; _jc_save_toDate=2024-08-05',
            'Host': 'kyfw.12306.cn',
            'Sec-CH-UA': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
        }
        r = requests.get(url=url, headers=headers)
        results = r.json()['data']
        r.close()

        data_dicts = dict(
            日期=[],
            车次=[],
            起点站=[],
            起点站代号=[],
            终点站=[],
            终点站代号=[],
            开始时=[],
            结束时=[],
            持续时间=[],
            商务座=[],
            一等座=[],
            二等座=[],
            高级软卧=[],
            软卧=[],
            硬卧=[],
            软座=[],
            硬座=[],
            无座=[],
        )
        table_headers = [
            '日期', '车次', '起点站', '起点站代号', '终点站', '终点站代号',
            '开始时', '结束时', '持续时间', '商务座', '一等座', '二等座',
            '高级软卧', '软卧', '硬卧', '软座', '硬座', '无座',
        ]
        for i in results:
            traindata = i["queryLeftNewDTO"]
            data_dicts['日期'].append(date)
            data_dicts['车次'].append(traindata["station_train_code"])
            data_dicts['起点站'].append(traindata["start_station_name"])
            data_dicts['起点站代号'].append(traindata["start_station_telecode"])
            data_dicts['终点站'].append(traindata["end_station_name"])
            data_dicts['终点站代号'].append(traindata["end_station_telecode"])
            data_dicts['开始时'].append(traindata["start_time"])
            data_dicts['结束时'].append(traindata["arrive_time"])
            data_dicts['持续时间'].append(traindata["lishi"])
            data_dicts['商务座'].append(traindata["swz_price"])
            data_dicts['一等座'].append(traindata["zy_price"])
            data_dicts['二等座'].append(traindata["ze_price"])

            data_dicts['高级软卧'].append(traindata["gr_price"])
            data_dicts['软卧'].append(traindata["rw_price"])
            data_dicts['硬卧'].append(traindata["yw_price"])
            data_dicts['软座'].append(traindata["rz_price"])
            data_dicts['硬座'].append(traindata["yz_price"])
            data_dicts['无座'].append(traindata["wz_price"])
        os.makedirs(save_path, exist_ok=True)
        df = pd.DataFrame(data_dicts)
        df.to_csv(os.path.join(save_path, f'{from_station}_{to_station}.csv'), index=False)

    except Exception as e:
        print(e)
        return e