import requests
import re
from bs4 import BeautifulSoup



class mohw():

    #name, value
    data_search = [
        '__eo_obj_states',
        '__eo_sc',
        '__EVENTTARGET',
        '__EVENTARGUMENT',
        '__LASTFOCUS',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__VIEWSTATEENCRYPTED',
        '__EVENTVALIDATION',
        'eo_version',
        'eo_style_keys',
        'ctl00$ContentPlaceHolder1$txtBAS_NAME',   #機構名稱
        'ctl00$ContentPlaceHolder1$ddlBAS_KIND',   #機構類別
        'ctl00$ContentPlaceHolder1$ddlAREA_CODE',  #縣市
        'ctl00$ContentPlaceHolder1$ddlZIP_CODE',   #區
        'ctl00$ContentPlaceHolder1$ddlBasDep',     #診療科別
        'ctl00$ContentPlaceHolder1$TextBox1',      #認證碼
        'ctl00$ContentPlaceHolder1$btnSearch',     #查詢
        #'ctl00$ContentPlaceHolder1$NetPager1$txtPage',
    ]

    #name, value
    data_nextpage = [
        '__eo_obj_states',
        '__eo_sc',
        '__EVENTTARGET',
        '__EVENTARGUMENT',
        '__LASTFOCUS',
        '__VIEWSTATE',
        '__VIEWSTATEGENERATOR',
        '__VIEWSTATEENCRYPTED',
        '__EVENTVALIDATION',
        'eo_version',
        'eo_style_keys',
        'ctl00$ContentPlaceHolder1$txtBAS_NAME',   #機構名稱
        'ctl00$ContentPlaceHolder1$ddlBAS_KIND',   #機構類別
        'ctl00$ContentPlaceHolder1$ddlAREA_CODE',  #縣市
        'ctl00$ContentPlaceHolder1$ddlZIP_CODE',   #區
        'ctl00$ContentPlaceHolder1$ddlBasDep',     #診療科別
        'ctl00$ContentPlaceHolder1$TextBox1',      #認證碼
        'ctl00$ContentPlaceHolder1$NetPager1$txtPage', #指定頁
        'ctl00$ContentPlaceHolder1$NetPager1$btGo', #Go
    ]

    #id, string
    parser_agencyinfo = [
        'ctl00_ContentPlaceHolder1_lblBAS_ID', #機構代碼
        'ctl00_ContentPlaceHolder1_lblBAS_NAME', #機構名稱
        'ctl00_ContentPlaceHolder1_lblBAS_AUTHOR', #權屬別
        'ctl00_ContentPlaceHolder1_lblBAS_TYPE', #型態別
        'ctl00_ContentPlaceHolder1_lblBAS_AREA', #縣市區名
        'ctl00_ContentPlaceHolder1_lblBAS_TEL', #電話
        'ctl00_ContentPlaceHolder1_lblBAS_STATUS', #開業狀態
        'ctl00_ContentPlaceHolder1_lblNHI_FLAG', #健保特約註記
        'ctl00_ContentPlaceHolder1_lblBAS_ADDRESS', #地址
    ]

    def __init__(self, name):
        self.name = name
        self.base = 'https://ma.mohw.gov.tw/'

        self.ses = requests.Session()
        self.ses.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        })
        self.header_search = {}
        self.header_next = {}

    def get_validatecode(self):
        pic = self.ses.get('https://ma.mohw.gov.tw/ValidateCode.aspx')
        with open(self.name+'_validatecode.jpg','wb') as f:
            f.write(pic.content)

    def page_search(self):
        _index = self.ses.get('https://ma.mohw.gov.tw/masearch/', verify=False)
        self.get_validatecode()
        soup_search = BeautifulSoup(_index.content)
        self.header_search = { data: parser_header(soup_search, data) for data in self.data_search}
        #_name = input('機構名稱: ')
        print(self.name)
        _code = input('輸入驗證碼: ')
        self.header_search['ctl00$ContentPlaceHolder1$txtBAS_NAME'] = self.name  #_name 正醫事放射所  長期照顧中心
        self.header_search['ctl00$ContentPlaceHolder1$TextBox1'] = _code
        _search = self.ses.post('https://ma.mohw.gov.tw/masearch/', data=self.header_search, verify=False)
        soup_result = BeautifulSoup(_search.content)
        _result_records = soup_result.find(id = 'ctl00_ContentPlaceHolder1_NetPager1_lblRecordCount')
        _result_pages = soup_result.find(id = 'ctl00_ContentPlaceHolder1_NetPager1_lblPageCount')
        self.header_next = { data: parser_header(soup_result, data) for data in self.data_nextpage}
        if _result_records:
            _result = {
                'status': 'Success',
                'page': page_total(_result_pages.string),
                'record': page_total(_result_records.string),
            }
            return _result
        else:
            return {'status': 'Error'}


    def page_next(self, page):
        self.header_next['ctl00$ContentPlaceHolder1$NetPager1$txtPage'] = page
        _next_page = self.ses.post('https://ma.mohw.gov.tw/masearch/', data=self.header_next, verify=False)
        soup_page = BeautifulSoup(_next_page.content)
        self.header_next = { data: parser_header(soup_page, data) for data in self.data_nextpage}
        _info_table = soup_page.find(id = 'ctl00_ContentPlaceHolder1_gviewMain')
        if _info_table:
            _trs = _info_table.find_all('tr')
            _result = {'status': 'Success',}
            for _tr in _trs:
                _tds = _tr.find_all('td')
                if _tds:
                    _result.update({
                        _tds[1].a.get('href') : [
                            _tds[0].string,
                            _tds[1].a.get('href'),
                            _tds[2].string,
                            _tds[3].string,
                        ]
                    })
            return _result
    
        return {'status': 'Error'}
    
    def page_detail(self, lblBAS_ID):
        _detail = self.ses.get('https://ma.mohw.gov.tw/masearch/'+lblBAS_ID, verify=False)
        print ('https://ma.mohw.gov.tw/masearch/'+lblBAS_ID)
        soup_info = BeautifulSoup(_detail.content)
        _table = soup_info.find(id = 'ctl00_ContentPlaceHolder1_Panel5')
        _result = [ _table.find(id = info).string if _table.find(id = info).string is not None else '' for info in self.parser_agencyinfo ]
        return _result


def page_total(str):
    _total = re.findall(r'\d', str)
    _total_page = ''.join(_total)
    return _total_page


def parser_header(soup, key):
    value = ''
    if soup.find('input', {'name': key}) is not None:
        value = soup.find('input', {'name': key}).get('value')
    return value

