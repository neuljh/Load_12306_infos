import itertools

from tqdm import tqdm

from utils.util import get_price, getStationName

date = '2024-08-15'

all_text = getStationName()
all_citys = list(all_text.keys())
all_city_codes = list(all_text.values())

load_citys = [
    '北京', '重庆', '上海', '广州', '深圳', '苏州', '成都', '杭州',
]
combinations = list(itertools.permutations(load_citys, 2))
save_path = f'./data/12306/{date}'
for combo in tqdm(combinations, desc="Stations Loading"):
    get_price(all_text, date, combo[0], combo[1], save_path=save_path)