__author__ = "Shawn Wu"
__email__ = "hsiang924@gmail.com"
__version__ = "2.0"

import time

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import mohw

#auth_json_path = 'mohw-bdabb6b0a7eb.json'
auth_json_path = 'mohw-b4ed85594b1e.json'
gss_scopes = ['https://spreadsheets.google.com/feeds']
#spreadsheet_key_path = '1F9FMRl4J-r43sJ44ZLrmDoOek2b5rH1grVSnlQdPB48'

#google sheet
sht_longterm = '1e6BIO_Gl2T3dMQPbCK1UcSkDs0Q4g6xjn-ge5V52D5I'
sht_nurse = '16cOzDj2f880eA6pfOYHM6dAPpHer2QSm2JH8tKz3aYY'
sht_home = '1rBFwZ1Veg2WyZLtyjNayhF9XlrvnrhrE4wpQQuyQaGs'
sht_daily = '1gjorGT2zgfNrWRaocL2FjYp_gb1LHIJ1BlUhH5u4Ios'
sht_recovery = '1bjyk0e6Qcj2YWA3CexhVOgmint3uI3bD9Pxl_lMFwn4'

sht_map = {
    '長期照顧中心': sht_longterm, 
    '護理之家': sht_nurse, 
    '居家護理所': sht_home, 
    '日間照顧中心': sht_daily,
    '康復之家': sht_recovery
}

keylist = ['長期照顧中心', '護理之家', '居家護理所', '日間照顧中心','康復之家']
reject_keylist = ['產後護理之家']


def auth_gss_client(path, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path,
                                                                   scopes)
    return gspread.authorize(credentials)


def update_sheet(gss_client, key, items):
    wks = gss_client.open_by_key(key)
    sheet = wks.sheet1
    sheet.insert_row(items, 2)




if __name__ == '__main__':

    today = time.strftime('%Y-%m-%d', time.localtime())
    gss_client = auth_gss_client(auth_json_path, gss_scopes)

    parsers = {key: {'parser':mohw.mohw(key)} for key in keylist}
    for key in keylist:
        parsers[key].update(parsers[key]['parser'].page_search())
    
    if 'Error' not in str(parsers):
        for key in keylist:
            print('====== %s ======' % key)
            print('Pages: %s 頁' % parsers[key]['page'])
            print('Records: %s 筆' % parsers[key]['record'])

        for key in keylist:
            pages = parsers[key]['page']
            spreadsheet_key_path = sht_map[key]
            ids = gss_client.open_by_key(spreadsheet_key_path).sheet1.col_values(3)

            for page in range(1, int(pages)+1):
                parser = parsers[key]['parser']
                parser_info = parser.page_next(page)
                print('Page: %s' % page)
                print('\n'.join(parser_info.keys()))
                if parser_info.get('status') == 'Success':
                    for infoids in parser_info.keys():
                        _name = parser_info.get(infoids)[0]
                        reject_key = [rk for rk in reject_keylist if rk in _name]
                        if infoids != 'status' and infoids not in ids and not reject_key:
                            detail = parser.page_detail(parser_info.get(infoids)[1])
                            info = [today] + parser_info.get(infoids) + (detail)
                            update_sheet(gss_client, spreadsheet_key_path, info)
                            print ('\n'.join(info))
                            print("====== Page %s / %s ======" % (page, pages))
                            time.sleep(0.5)

                print("====== Page %s / %s ======" % (page, pages))
                time.sleep(1)
    print ("====== Finish ======")

