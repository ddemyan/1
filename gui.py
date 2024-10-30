import PySimpleGUI as sg
# Настройки интерфейса
sizeW, sizeD, sizeML = (960, 670), (110, 23), (150, 30)
locationW, locationD = (5, 5), (7, 171)
font = ('Calibri', 12)
#sg.theme('default1')
# Define the variables used in the GUI
gap = ['0.1', '0.25', '0.5', '0.75', '1']
gap1 = ['1', '3', '5', '10']
gap2 = ['Стоплосс', 'Тренд', 'Отскок']
list_trading_pairs = ['BTCUSDT', 'ETHUSDT', 'ETHBTC', 'BNBUSDT', 'BNBETH', 'BNBBTC']
list_coins = ['BTC', 'ETH', 'USDT', 'BNB']
orderId = []
list_doit=['client.get_account()','client.get_asset_balance(asset="BTC")',
           'client.get_account_api_trading_status()','round(float(values["-LB-"]) * float(client.get_asset_balance(asset=values["-lc-"])),8)',
           'client.get_my_trades(symbol="BNBBTC")']
list_d=['Close и Num больше средней на дельту', 'Close и Num меньше средней на 2-дельта',
 'bear_up_high', 'bear_up_low', 'bear_', 'bull_up_high', 'bull_up_low', 'bull_']
# Определение макета интерфейса
c1 = sg.Column ([[sg.Button('Go')]])
c2 = sg.Column ([[ sg.Radio ('BUY', group_id=1, default=True, enable_events=True,
                             key='-BUY-')],
                 [sg.Radio ('SELL', group_id=1, enable_events=True, key='-SELL-')]])
c3 = sg.Combo (list_coins, key='-lc-', default_value='ETH',readonly=False)
c4 = sg.Column ([[ sg.Combo (list(gap), key='-LB-', default_value='0.1')]])
c5 = sg.Column ([[ sg.Combo (list(gap1), key='-LB1-', default_value='3')]])
c6 = sg.Column ([[ sg.Listbox (list(gap2), key='-LB2-', s=(15, 3),
                               select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)]])
c7 = sg.Column ([[ sg.Text ('ma'), sg.InputText ('7',key='-AVR-',size=(5,1))],
                  [sg.Text ('delta_ma'), sg.InputText ('13',key='-AVR1-',size=(5,1))],
                  [sg.Text ('delta_num'), sg.InputText ('13',key='-AVR2-',size=(5,1))]])

layout = [
 [sg.Text ('БАЛАНС'),
  sg.Button ('Bill'), sg.Input(key='-billETH-', s=15), sg.Input(key='-billBTC-', s=20),
  sg.Input(key='-billUSDT-', s=20), sg.Text ('ВСЕГО'), sg.Input(key='-billALL-', s=20)],
 [[c1, sg.VerticalSeparator(), c2, sg.VerticalSeparator(), c3, sg.VerticalSeparator(),
 c4, sg.VerticalSeparator(), c5, sg.VerticalSeparator(), c6, sg.VerticalSeparator(),c7]],
 [sg.Input(key='-TOTAL_DIFF-', s=10, readonly=True), sg.Button ('ВСЕ ОРДЕРА'), sg.Button ('ОТКРЫТЫЕ ОРДЕРА'),
  sg.Button ('СИГНАЛЫ'),sg.Combo (list_d, key='-ld-', default_value='bull_up_low',readonly=False)],
 [sg.Input('13/10/2024 00:00:00',key='-START_DATE-',s=20),sg.Input('23/10/2024 00:00:00',key='-END_DATE-',s=20)],
 [sg.Table (values=[],
  headings=['price_diff','orderId','symbol','price','side','origQty','status','type','time'],
  col_widths = [20, 10, 10, 10, 10, 10, 10], num_rows=5, auto_size_columns=False, justification='center',
  key='-TABLE1-', enable_events=True, expand_x=True)],

 [sg.Combo (orderId, key='-id-', s=10, readonly=False),
  sg.Button('Cancel'), sg.Button('Delete')],
 [sg.Table (values=[], headings=['time', 'open', 'high', 'low', 'close', 'volume', 'num'],
  col_widths = [20, 10, 10, 10, 10, 10, 10], num_rows=5, justification='center',
  key='-TABLE2-', enable_events=True, auto_size_columns=False, expand_x=True)],
 [sg.Button ('Exit'),sg.Button('Clear'), sg.Button('Save'),
  sg.Button('Do_it'),sg.Combo(list_doit,key='-LIST_DOIT-',s=10,font=font, expand_x=True,
  enable_events=True)],
 [sg.Multiline (size=sizeML, key='-ML-', autoscroll=True)]
         ]
def create_window():
    return sg.Window('by Dandr11', layout, finalize=True, resizable=True,
                     location=locationW, size=sizeW, font=font)
if __name__ == "__main__":
    window = create_window()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    window.close()
