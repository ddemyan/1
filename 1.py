import gui, key, math, threading
from datetime import datetime
import pandas as pd
import PySimpleGUI as sg
from binance.client import Client
from binance import ThreadedWebsocketManager
pd.options.mode.copy_on_write = True
client = Client(key.api_key, key.api_secret, testnet=True)
df,d = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume', 'num']), []
def Run():
    twm = ThreadedWebsocketManager(api_key=key.api_key, api_secret=key.api_secret)
    twm.start()
    twm.start_kline_socket(symbol=f"{values['-lc-']}USDT", callback=Di)
    twm.join()
def Di(msg, hours=3):
    #print(msg)  # вывод сообщения для отладки
    condition=values['-ld-']
    ma=int(values['-AVR-'])
    delta_ma=float(values['-AVR1-'])
    delta_num=float(values['-AVR2-'])
    d.append(msg)
    if len(d) == 6:
        del d[0]
    if len(d) >= 5:
        for y in range(-5, -1):
            event_time = pd.to_datetime(d[y]['E'], unit='ms') + pd.Timedelta(hours=hours)
            formatted_time = event_time.strftime('%H:%M:%S.%f')[:-4] + '/' + event_time.strftime('%d.%м.%y')
            df.loc[y] = [event_time, float(d[y]['k']['o']), float(d[y]['k']['h']),
                         float(d[y]['k']['l']), float(d[y]['k']['c']),
                         float(d[y]['k']['v']), int(d[y]['k']['n'])         ]
        condition_eval = eval(gui.Dict_query[values['-ld-']])
        if condition_eval.any():
            window.write_event_value('-PRINT-', df.iloc[-1])
        window.write_event_value('-UPDATE_TABLE-', df.values.tolist())
def Go():
    symbol = f"{values['-lc-']}USDT"
    asset = values['-lc-']
    deptH = client.get_order_book(symbol=symbol)
    best_buy, best_sell = deptH['bids'][3][0], deptH['asks'][3][0]
    parts = int(values['-LB1-'])  # количество частей на которые будет разбит ордер
    order_type = values['-LB2-']  # тип ордера, например, скользящий стоплосс
    if values['-BUY-']:
        q = float(values['-LB-']) * float(client.get_asset_balance(asset=asset)["free"]) / parts
        q = round_quantity(symbol, q)
        for _ in range(parts):
            if order_type == "trailing_stop_loss":
                Print('client.order')
            else:
                Print(client.order_limit_buy( symbol = symbol , price=float(best_buy) , quantity=q))
    else:
        q = float(values['-LB-']) * float(client.get_asset_balance(asset=asset)["free"]) / parts
        q = round_quantity(symbol , q)
        for _ in range(parts):
            if order_type == "trailing_stop_loss":
                Print('client.order')
            else:
                Print(client.order_limit_sell( symbol=symbol , price=float(best_sell) , quantity = q ))
def Bill():
    # Инициализация начальных значений балансов
    initial_btc_balance = 1
    initial_eth_balance = 5
    initial_usdt_balance = 5000
    # Функция для вычисления процентно��о изменения
    def calculate_percentage_change(initial, current):
        return ((current - initial) / initial) * 100
    # Получение текущих балансов активов
    btc_balance = float(client.get_asset_balance(asset='BTC')["free"])
    eth_balance = float(client.get_asset_balance(asset='ETH')["free"])
    usdt_balance = float(client.get_asset_balance(asset='USDT')["free"])
    # Вычисление процентного изменения
    btc_change = calculate_percentage_change(initial_btc_balance, btc_balance)
    eth_change = calculate_percentage_change(initial_eth_balance, eth_balance)
    usdt_change = calculate_percentage_change(initial_usdt_balance, usdt_balance)
    # Получение последних цен на ��������ктивы
    btc_price = float(client.get_recent_trades(symbol='BTCUSDT')[-1]['price'])
    eth_price = float(client.get_recent_trades(symbol='ETHUSDT')[-1]['price'])
    # Вычисление общей стоимости активов
    total_value = btc_price * btc_balance + eth_price * eth_balance + usdt_balance
    # Обновление значений в графическом интерфейсе
    window['-billBTC-'].update(f"{btc_balance} ({btc_change:.2f}%)")
    window['-billETH-'].update(f"{eth_balance} ({eth_change:.2f}%)")
    window['-billUSDT-'].update(f"{usdt_balance} ({usdt_change:.2f}%)")
    window['-billALL-'].update(total_value)
def display_open_orders():
    orders = pd.DataFrame(client.get_open_orders(symbol=f"{values['-lc-']}USDT"),
                          columns=['orderId', 'symbol', 'price', 'side', 'origQty', 'status', 'type', 'time'])
    orderId = orders[['symbol','orderId']].values.tolist()
    window['-TABLE1-'].update(values=orders.values.tolist())
    window['-id-'].update(values=orderId)# Обновление значений в ComboBox
def display_all_orders():
    start_date = datetime.strptime(values['-START_DATE-'], '%d/%m/%Y %H:%M:%S')
    end_date = datetime.strptime(values['-END_DATE-'], '%d/%m/%Y %H:%M:%S')
    orders = pd.DataFrame(client.get_all_orders(symbol=f"{values['-lc-']}USDT"),
                          columns=['orderId', 'symbol', 'price', 'side', 'origQty', 'status', 'type', 'time'])
    orders['time'] = pd.to_datetime(orders['time'], unit='ms')
    filtered_orders = orders[(orders['time'] >= start_date) & (orders['time'] <= end_date)]
    # Получаем текущую цену актива
    current_price = float(client.get_symbol_ticker(symbol=f"{values['-lc-']}USDT")['price'])
    # Вычисляем разницу между ценой ордера и текущей ценой
    #filtered_orders['price_diff'] = filtered_orders.apply(
    #    lambda row: current_price - float(row['price']) if row['side'] == 'BUY' else float(row['price']) - current_price, axis=1)
    filtered_orders.loc[:, 'price_diff'] = filtered_orders.apply(
    lambda row: current_price - float(row['price']) if row['side'] == 'BUY' else float(row['price']) - current_price, axis=1)
    # Округляем значения в колонке 'price_diff' до двух знаков после запятой
    filtered_orders.loc[:,'price_diff'] = filtered_orders['price_diff'].round(2)
    # Перемещаем колонку 'price_diff' на первое место
    filtered_orders.insert(0, 'price_diff', filtered_orders.pop('price_diff'))
    # Вычисляем итоговую сумму по колонке 'price_diff'
    total_price_diff = filtered_orders['price_diff'].sum()
    window['-TABLE1-'].update(values=filtered_orders.values.tolist())
    window['-id-'].update(values=filtered_orders[['symbol', 'orderId']].values.tolist())
    window['-TOTAL_DIFF-'].update(total_price_diff)
def Print(*x):
    window['-ML-'].print('\n', x, sep='')
def Cancel_order():
    if values['-id-']:
        symbol, order_id = values['-id-']
        Print(client.cancel_order(symbol=symbol, orderId=order_id))
def Cancel_all_orders():#del_all_order():
    if values['-id-']:
        symbol, order_id = values['-id-']
        for b in order_id:
            Print(client.cancel_order(symbol=symbol, orderId=b))
def get_depth():
    x = client.get_order_book(symbol=f"{values['-lc-']}USDT")
    window['-ML-'].print(x)
    df_asks = pd.DataFrame(x['asks'], columns=['ask_price', 'ask_vol']).astype(float)
    df_bids = pd.DataFrame(x['bids'], columns=['bid_price', 'bid_vol']).astype(float)
    df_bids['depth'] = df_bids['bid_price'].apply(
        lambda x: '1%' if df_bids['bid_price'].max() / x > 1.001 else '0.1%' if df_bids['bid_price'].max() / x > 1.0001 else '0.01%')
    df_bids.loc[0, 'depth'] = '0%'
    df_asks['depth'] = df_asks['ask_price'].apply(
        lambda x: '1%' if df_asks['ask_price'].min() / x < 0.99 else '0.1%' if df_asks['ask_price'].max() / x < 0.999 else '0.01%')
    df_asks.loc[0, 'depth'] = '0%'
    depth = pd.concat([df_asks.groupby('depth')['ask_vol'].sum(),
                       df_bids.groupby('depth')['bid_vol'].sum()], axis=1).sort_values('depth')
    Print(depth)
def Save_txt(x):
    with open('log.txt','wt') as f: f.write(x)#.to_string()#x.to_csv(f"{x}.csv")
    f.close()
def log_data(*data):
    with open('log.txt', 'wt') as f:
        f.write('\n')
        for item in data:
            f.write(str(item))
def round_quantity(symbol, quantity):
    # Получаем информацию о символе
    info = client.get_symbol_info(symbol)
    step_size = float(info['filters'][1]['stepSize'])

    # Округляем количество до допустимого числа знаков после запятой
    precision = int(round(-math.log(step_size, 10), 0))
    return round(quantity, precision)
window = gui.create_window()
while True:
    event, values = window.read()
    try:
        if event == '-UPDATE_TABLE-':
            window['-TABLE2-'].update(values=df.values.tolist())
        if event == '-PRINT-':
            Print(values)
        if event == 'СИГНАЛЫ':
            threading.Thread(target=Run).start()
        if event == 'Go': Go()
        if event == 'Bill': Bill()
        if event == 'ВСЕ ОРДЕРА': display_all_orders()
        if event == 'ОТКРЫТЫЕ ОРДЕРА': display_open_orders()
        if event == 'Cancel': Cancel_order()
        if event == 'Cancel_all': Cancel_all_orders()
        if event == 'Do_it': Print(eval(values['-LIST_DOIT-']))
        if event == 'Save': Save_txt(values['-ML-'])
        if event == 'Clear': window['-ML-'].update('')
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    except Exception as e:
        sg.popup(e, no_titlebar=True, background_color='#e22bc7')
window.close()
