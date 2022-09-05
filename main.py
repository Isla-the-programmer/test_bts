import requests
import pandas as pd
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from difflib import SequenceMatcher
import numpy as np
from database import Database


class Browser:
    permanent_url = None
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    @classmethod
    def choose_url_by_regions(cls, region_number):
        regions = {1: 'http://nursultan.kgd.gov.kz/ru',
            2: 'http://almaty.kgd.gov.kz/ru',
            3: 'http://shymkent.kgd.gov.kz/ru',
            4: 'http://akm.kgd.gov.kz/ru',
            5: 'http://akb.kgd.gov.kz/ru',
            6: 'http://alm.kgd.gov.kz/ru',
            7: 'http://atr.kgd.gov.kz/ru',
            8: 'http://vko.kgd.gov.kz/ru',
            9: 'http://zhmb.kgd.gov.kz/ru',
            10: 'http://zko.kgd.gov.kz/ru',
            11: 'http://krg.kgd.gov.kz/ru',
            12: 'http://kst.kgd.gov.kz/ru',
            13: 'http://kzl.kgd.gov.kz/ru',
            14: 'http://mng.kgd.gov.kz/ru',
            15: 'http://pvl.kgd.gov.kz/ru',
            16: 'http://sko.kgd.gov.kz/ru',
            17: 'http://trk.kgd.gov.kz/ru'}
        cls.permanent_url = regions[region_number]

    @staticmethod
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    @classmethod
    def change_url_by(cls, url):
        cls.permanent_url = url

    @classmethod
    def change_url(cls, url):
        cls.permanent_url = url

    @classmethod
    def get_browser(cls):
        cls.browser.get(cls.permanent_url)

    @classmethod
    def get_child_elements_url_by_id_text(cls, id, text):
        url = None
        max_similarity = 0
        url_max = None
        for element in cls.browser.find_element(By.ID, id).find_elements(By.CSS_SELECTOR, "*"):
            url = element.get_attribute('href')
            if cls.similar(text, element.text) > max_similarity and url is not None:
                max_similarity = cls.similar(text, element.text)
                url_max = url
        return url_max

    @classmethod
    def get_child_elements_url_by_text(cls, text):
        url = None
        max_similarity = 0
        url_max = None
        all_elements = cls.browser.find_elements(By.CSS_SELECTOR, "*")
        num_el = len(all_elements)
        counter = 1
        for element in all_elements:
            print(f'{counter}/{num_el} ' + str('*'*counter), end = '\r')
            url = element.get_attribute('href')
            if cls.similar(text,element.text) > max_similarity and url is not None:
                max_similarity = cls.similar(text, element.text)
                url_max = url
            counter += 1
        return url_max

    @classmethod
    def close(cls):
        cls.browser.close()


if __name__ == "__main__":
    print('Введите номер региона\n'
          '(1 - Нур-Султан,\n'
          ' 2 - Алматы,\n'
          ' 3 - Шымкент,\n'
          ' 4 - Акмолинская область,\n'
          ' 5 - Актюбинская область,\n'
          ' 6 - Алматинская область,\n'
          ' 7 - Атырауская область,\n'
          ' 8 - ВКО,\n'
          ' 9 - Жамбвльская область,\n'
          ' 10 - ЗКО,\n'
          ' 11 - Карагандинская область,\n'
          ' 12 - Костанайская область,\n'
          ' 13 - Кызылординская область,\n'
          ' 14 - Мангистауская область,\n'
          ' 15 - Павлодарская область,\n'
          ' 16 - СКО,\n'
          ' 17 - Туркестанская область):')
    number = int(input())
    year = int(input("Введите год (Например, 2018):\n"))
    Browser.choose_url_by_regions(number)
    Browser.get_browser()

    """
    Парсинг по по вкладкам
    """
    path = ['ЮРИДИЧЕСКИМ ЛИЦАМ', 'Реабилитация и банкротство', f'{year} год', 'Информационные сообщения', 'Объявления о возбуждении дела о банкротстве и о порядке заявления требования кредиторами']
    url = None
    for button in path:
        print(f'Обработка страницы {button}' )
        if url is not None:
            Browser.change_url(url)
            Browser.get_browser()
        url = Browser.get_child_elements_url_by_text(button)
    resp = requests.get(url)
    rawData = pd.read_excel(resp.content).dropna(thresh=2)
    need_columns_dict = {
     'БИН/ИИН должника': 'iin',
    'Наименование /Ф.И.О.должника': 'debtor_name',
    'Номер государственной регистрации должника': '  v debtor_number',
    'Адрес местонахождения должника': 'debtor_address',
    'Наименование суда': 'trial_name',
    'Дата вынесения определения о возбуждении дела о банкротстве': 'bancruptcy_date',
    'Дата назначения временного управляющего': 'manager_date',
    'Ф.И.О. Временного управляющего': 'manager_name',
    'Срок принятия требований кредиторов временным управляющим': 'manager_term',
    'Адрес приема требований': 'requirements_address',
    'Контактные данные (телефон, электронный адрес) временного управляющего': 'contacts',
    'Дата размещения объявления': 'ad_date'}

    """ Сопоставление колонок с базовыми"""
    need_columns = list(need_columns_dict.keys())
    new_header = rawData.iloc[0]
    terms_columns = ''
    rawData = rawData[1:]
    rawData.columns = new_header
    new_header_2 = rawData.iloc[0]
    maxs = [0,0,0,0,0,0,0,0,0]
    matrix = []
    max_sim = {}
    for need in need_columns:
        similar = []
        for name in new_header:
            if type(name) is not str or '№' in name:
                continue
            similar.append(round(Browser.similar(need,name),3))
        matrix.append(similar)
    a = np.array(matrix)
    counter = 0
    inds = []
    while counter <= len(need_columns) and np.max(a,axis=None) != 0.:
        ind = np.unravel_index(np.argmax(a, axis=None), a.shape)
        inds.append(ind)
        counter += 1
        for k,i in enumerate(a):
            i[ind[1]] = 0.
            if k == ind[0]:
                for j in range(len(i)):
                    i[j] = 0.
    new_header = [i for i in list(new_header) if type(i) == str and '№' not in i]

    result_df = pd.DataFrame()
    for i in inds:
        if need_columns[i[0]] != 'Срок принятия требований кредиторов временным управляющим':
            result_df[need_columns_dict[need_columns[i[0]]]] = rawData[new_header[i[1]]]
    rawData = rawData[1:]
    rawData.columns = new_header_2
    result_df['manager_term_start'] = rawData[[i for i in rawData.columns if 'с' in str(i)][0]]
    result_df['manager_term_end'] = rawData[[i for i in rawData.columns if 'до' in str(i)][0]]
    result_df = result_df[2:]
    """Запись в бд"""
    database = Database()
    database.create_table()
    database.insert_data(result_df)
    Browser.close()
