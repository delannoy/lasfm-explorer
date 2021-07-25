#!/usr/bin/env python3

from logFormat import C
from util import Cred
from typing import List
import lxml.html, lxml.cssselect, os, pandas, requests

csssel = lxml.cssselect.CSSSelector
listText = lxml.etree.XPath('text()') # [https://lxml.de/tutorial.html#using-xpath-to-find-text]

headers = {
          # [https://httpbin.org/headers] [https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/]
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
          "Accept-Encoding": "gzip, deflate, br",
          "Accept-Language": "en-US,en;q=0.9,es;q=0.8,es-419;q=0.7,fr;q=0.6,ru;q=0.5",
          "Dnt": "1",
          "Referer": "https://www.google.com/",
          "User-Agent":os.environ['USERAGENT']
          }

def eTreeGet(url:str) -> lxml.html.HtmlElement:
    '''Get HTML request and return as eTree element.'''
    resp = requests.get(url=url, headers=headers).content
    return lxml.html.fromstring(resp)

def lastfmNeighbors(user:str=Cred.user) -> pandas.DataFrame:
    '''Parse lastFM neighbors page for {user}.'''
    eTree = eTreeGet(f'https://www.last.fm/user/{user}/neighbours')
    users = [user.text for user in csssel('a.user-list-link')(eTree)]
    artists = [[artist.text for artist in csssel('a')(user)] for user in csssel('p.user-list-shared-artists')(eTree)]
    return pandas.DataFrame({'user':users,'artistsInCommon':artists})

def apiMethods() -> List[str]:
    '''Parse all available lastFM API methods.'''
    eTree = eTreeGet('https://www.last.fm/api')
    section = csssel('section.sidebar-group')(eTree)[2]
    methods = [element.text for element in section.iter('a')]
    _ = [print(method) for method in methods]
    return methods

def apiDocs(method:str=None):
    '''Parse lastFM API docs for {method}.'''
    def brTagNewLine(node):
        '''Convert etree element to string, replace '<br/>' with '\n', and convert back to etree element.'''
        return lxml.html.fromstring(lxml.etree.tostring(node).decode("utf-8").replace('<br/>','\n'))
    def exampleURL(element:lxml.html.HtmlElement):
        print(f'{C.uline}{listText(element)[0].strip()}{C.reset}')
        k = csssel('strong')(div[idx+1])
        if v := csssel('a')(div[idx+1]):
            _ = [print(f"{k.text} {v.get('href')}") for k,v in zip(k,v)]
        elif v := [val for val in listText(div[idx+1]) if val.strip()]:
            _ = [print(f'{k.text} {v}') for k,v in zip(k,v)]
    def params(element:lxml.html.HtmlElement):
        print(f'{C.uline}{listText(element)[0].strip()}{C.reset}')
        _ = [print(param.strip()) for param in brTagNewLine(div[idx+1]).text_content().splitlines()]
        # k = csssel('strong')(div[idx+1])
        # v = [val for val in listText(div[idx+1]) if val.strip()]
        # _ = [print(f'{k.text}{v}') for k,v in zip(k,v)]
    if method is None:
        return apiMethods()
    else:
        eTree = eTreeGet(f'https://www.last.fm/api/show/{method}')
        div = csssel('main div.content__default')(eTree)[0]
        for idx,element in enumerate(div):
            if element.tag == 'h1':
                print(f'\n{C.uline}{C.F.green}{listText(element)[0].strip()}{C.reset}\n{div[idx+1].text}')
            if ' Example URLs' in listText(element):
                exampleURL(element)
            if ' Params' in listText(element):
                params(element)
            if ' Auth' in listText(element):
                print(f'{C.uline}{listText(element)[0].strip()}{C.reset}')
                print(f'{div[idx+1].text_content()}')
            if ' Sample Response' in listText(element):
                pass # this is too much work lol
            if ' Errors' in listText(element):
                print(f'{C.uline}{listText(element)[0].strip()}{C.reset}')
                _ = [print(f'{item.text_content()}') for item in csssel('li')(div[idx+1])]

