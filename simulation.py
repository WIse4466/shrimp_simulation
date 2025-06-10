import simpy
import pandas as pd
import random

SEED = 9527
random.seed(SEED)

# 模擬參數設定
SIM_TIME = 480               # 模擬 480 分鐘
STOP_ACCEPTING_CUSTOMERS_TIME = 420  # 結束營業前 60 分鐘停止收客
THRESHOLD_WAIT_GIVE_ROD = 10 # 發桿等待超過 10 分鐘會離開
THRESHOLD_WAIT_FISHING = 30  # 釣魚等待超過 30 分鐘會離開
P_EAT_SHRIMP = 0.3          # 顧客烤蝦機率

# 各流程服務時間（分鐘、固定或分布）
T_GIVE_ROD =  1            # 發桿固定 1.2 分鐘
T_GRILL = 7               # 烤蝦固定 7.8 分鐘
T_CHECKOUT = 1            # 收銀固定 1.2 分鐘

# 吃蝦時間分布參數
EAT_MEAN  = 20               # 吃蝦平均 20 分鐘
EAT_SD    = 5                # 標準差 5
EAT_MIN   = 10               # 最少 10 分鐘

# 資源設定
NUM_FISHING_SPOTS = 28       # 釣蝦座位 28 席
NUM_EATING_SPOTS = 14        # 吃蝦座位 14 席

# 紀錄事件
event_log = []

def customer(env, cid, clerk, fish_spots, eat_spots):
    arrival = env.now
    event_log.append({'id': cid, 'event': 'arrival',       'time': arrival})

    # 1. 發桿 (含耐心等待)
    #with clerk.request(priority=0) as req:
    with clerk.request() as req:
        wait_start = env.now
        res = yield req | env.timeout(THRESHOLD_WAIT_GIVE_ROD)
        if req not in res:
            event_log.append({'id': cid, 'event': 'leave_on_rod', 'time': env.now,
                              'waiting_time_rod': env.now - wait_start})
            return
        wait_rod = env.now - wait_start
        yield env.timeout(T_GIVE_ROD)
        event_log.append({'id': cid, 'event': 'give_rod',      'time': env.now,
                          'waiting_time_rod': wait_rod})

    # 2. 釣蝦 (要佔用釣蝦座位)
    with fish_spots.request() as req:
        wait_start = env.now
        res = yield req | env.timeout(THRESHOLD_WAIT_FISHING)
        if req not in res:
            event_log.append({'id': cid, 'event': 'leave_on_fishing', 'time': env.now,
                              'waiting_time_fish': env.now - wait_start})
            return
        wait_fish = env.now - wait_start
        # 決定釣蝦時間
        # 抽樣離散釣蝦時間
        fishing_time = random.choices(
            [60, 120, 180, 240, 300],
            weights=[0.1, 0.45, 0.3, 0.1, 0.05],
            k=1
        )[0]
        # 把 fishing_time 調整為剩餘營業時間的整數
        '''remaining_time = SIM_TIME - env.now
        if fishing_time > remaining_time:
            fishing_time = remaining_time // 60
            fishing_time *= 60'''
        remaining_time = max(SIM_TIME - env.now, 0)

        if fishing_time > remaining_time:
            #fishing_time = (remaining_time // 60) * 60
            fishing_time = remaining_time

        event_log.append({'id': cid, 'event': 'start_fishing',  'time': env.now,
                          'waiting_time_fish': wait_fish,
                          'duration_fish': fishing_time})
        yield env.timeout(fishing_time)
        event_log.append({'id': cid, 'event': 'finish_fishing', 'time': env.now})

    # 3. 決定是否烤蝦
    if random.random() < P_EAT_SHRIMP:
        # 烤蝦 (佔用 clerk)
        #with clerk.request(priority=2) as req:
        with clerk.request() as req:
            wait_start = env.now
            yield req
            wait_grill = env.now - wait_start
            yield env.timeout(T_GRILL)
            event_log.append({'id': cid, 'event': 'grill',      'time': env.now,
                              'waiting_time_grill': wait_grill})

    # 吃蝦 (佔用吃蝦座位)
    eating_time = max(random.normalvariate(EAT_MEAN, EAT_SD), EAT_MIN)
    with eat_spots.request() as req:
        wait_start = env.now
        yield req
        wait_eat = env.now - wait_start
        event_log.append({'id': cid, 'event': 'start_eating','time': env.now,
                          'waiting_time_eat': wait_eat,
                          'duration_eat': eating_time})
        yield env.timeout(eating_time)
        event_log.append({'id': cid, 'event': 'finish_eating','time': env.now})

    # 4. 收銀
    #with clerk.request(priority=1) as req:
    with clerk.request() as req:
        wait_start = env.now
        yield req
        wait_co = env.now - wait_start
        yield env.timeout(T_CHECKOUT)
        event_log.append({'id': cid, 'event': 'checkout',     'time': env.now,
                          'waiting_time_checkout': wait_co})

def get_interarrival(env_now):
    # 假設 0–180 分鐘是離峰 (平均 8 分鐘一人)，
    # 180–300 分鐘是尖峰 (平均 3 分鐘一人)，
    # 300–480 分鐘再回到離峰
    if env_now < 180:
        return 6    # 離峰：8 分鐘來一位
    elif env_now < 300:
        return 4.6    # 尖峰：3 分鐘來一位
    else:
        return 8

def setup(env):
    #clerk = simpy.PriorityResource(env, capacity=1)
    clerk = simpy.Resource(env, capacity=1)
    fish_spots = simpy.Resource(env, capacity=NUM_FISHING_SPOTS)
    eat_spots = simpy.Resource(env, capacity=NUM_EATING_SPOTS)
    cid = 0
    while True:
        mean_interval = get_interarrival(env.now)
        inter = random.expovariate(1.0 / mean_interval)
        if env.now >= STOP_ACCEPTING_CUSTOMERS_TIME:  # 修改判斷條件
            break
        yield env.timeout(inter)
        cid += 1
        env.process(customer(env, cid, clerk, fish_spots, eat_spots))

# 執行模擬
env = simpy.Environment()
env.process(setup(env))
#env.run(until=SIM_TIME)

# 執行到停止收客時間
env.run(until=STOP_ACCEPTING_CUSTOMERS_TIME)
# 繼續執行直到所有事件完成
env.run()

# 整理輸出為 DataFrame
df = pd.DataFrame(event_log)
df['time'] = df['time'].round(2)

# 【關鍵步驟】將 DataFrame 存為 JSON 檔案
# orient='records' 會讓每一列都變成一個 JSON 物件，方便前端處理
df.to_json('simulation_log.json', orient='records', indent=4)

print("模擬完成！已成功產生 simulation_log.json。")
# 可以在這裡印出 df 來預覽結果
print(df.head())