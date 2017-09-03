# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import json, time, datetime
from datetime import date

# GET ~/keyboard/ 요청에 반응
def keyboard(request):
    return JsonResponse({
        'type': 'buttons',
        'buttons': ['중식', '석식']
    })

# csrf 토큰 에러 방지, POST 요청에 message response
@csrf_exempt
def message(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    meal = received_json_data['content']

    if meal == '중식':
        return JsonResponse({
            'message': {
                'text':'오늘의 중식 메뉴입니다.\n' + schoolmeal()
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['중식', '석식']
            }
        })
    if meal == '석식':
        return JsonResponse({
            'message': {
                'text':'오늘의 석식 메뉴입니다.\n' + schoolmeal()
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['중식', '석식']
            }
        })

# message 요청 받을시 크롤링 실시
def schoolmeal():
    from bs4 import BeautifulSoup
    import urllib.request
    import re

    if meal == '중식':
        sccode = 2
    if meal == '석식':
        sccode = 3

    #NEIS에서 파싱  
    url = ("http://stu.goe.go.kr/sts_sci_md01_001.do?schulCode=J100000502&schulCrseScCode=4&schulKndScCode=04&schMmealScCode=" + str(sccode))

    source = urllib.request.urlopen(url)

    #BeautifulSoup를 이용해 HTML에서 메뉴 추출
    soup = BeautifulSoup(source, "lxml")
    table_div = soup.find(id="contents")
    tables = table_div.find_all("table")
    menu_table = tables[0]
    td = menu_table.find_all('td')
    td_menu = td[8]
    str_menu = str(td_menu)

    today = datetime.datetime.today().weekday()

    # 월요일 ~ 일요일 = td[8] ~ td[14]
    if meal == '중식' or meal == '석식':
        if today == 6:
            menu = '일요일'
        else:
            menu = td[today + 8]
    if meal == '일요일':
        menu = '오늘은 일요일입니다. 내일 학교가네요ㅠ'
        
    #HTML 태그 제거
    pre_menu = re.sub(r'[<td class="textC"></td>\d.*]', '', str_menu)
    menu = re.sub('(br)', '\n', pre_menu)

    #급식 한줄평 기능
    re_menu = '(찜닭|미역)'

    #re_menu와 menu에서 일치하는 키워드를 찾아 리스트로 만듦
    li_menu = re.findall(re_menu, menu) 

    #li_menu 속 element의 개수 세기
    c_menu = len(li_menu)

    ev = " " #evaluation의 줄임말

    #c_menu의 개수대로 평가가 달라짐
    if c_menu == 0:
        ev = "ㅅㅌㅊ"
    elif c_menu == 1:
        ev = "그래도 급식을 먹는 게 나을 것 같아요!"
    elif c_menu >= 2:
        ev = "오늘 매점 장사가 잘되겠네요."

    finalstring = "오늘의 급식은:\n" + menu + '\n' + "한줄평: " + ev
    print(finalstring)