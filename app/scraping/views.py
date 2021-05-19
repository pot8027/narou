from os import error
from django import http
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import time

import requests
from bs4 import BeautifulSoup
import re

def index(requests, narou_id):

    narou = scraping(narou_id, requests)

    template = loader.get_template('scraping/index.html')
    context = {
        "narou" : narou,
    }

    return HttpResponse(template.render(context, requests))
    
def scraping(id, r):

    result = []

    try:
        page = 1
        while True:

            #1ページ分リクエスト
            load_url = f"https://ncode.syosetu.com/{id}/{page}/"
            headers = {
                "User-Agent": r.headers._store['user-agent'][1]
            }
            html = requests.get(load_url, headers=headers)

            if html.status_code != 200:
                break

            soup = BeautifulSoup(html.content, "html.parser")

            #話のタイトル抜き出し
            title = soup.find(class_="novel_subtitle")
            if title is None:
                continue
            
            #本文抜き出し
            honbun = soup.find(id="novel_honbun")
            if honbun is None:
                continue
            
            lines = []
            for line in honbun.find_all(id=re.compile("^L")):

                #１行分のテキスト
                linecontenttext = ''
                
                #行ごとにルビなどの要素が含まれるため、for分で回しながら１行分のテキストを作成
                for linecontent in line.contents:

                    #改行は無視
                    if linecontent.name == 'br':
                        continue

                    # ルビの部分は破棄, 内容のみ取得
                    if linecontent.name == 'ruby':
                        linecontenttext += linecontent.contents[0].contents[0]
                        continue

                    #通常行
                    linecontenttext += linecontent
                
                #１行分として追加
                lines.append(linecontenttext)

            #１話分として追加
            result.append(Syosetsu(title.contents[0], lines))
            page += 1

            #サーバ負荷対策
            time.sleep(1)

        return result
    except Exception as e:
        return None

class Syosetsu:
    def __init__(self, title, lines):
        self.title = title
        self.lines = lines