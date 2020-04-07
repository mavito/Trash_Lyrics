from bs4 import BeautifulSoup
import requests
import re
import os

GENIUS_TOKEN_KEY='EkNLwHeDp72-QDTr-fgQYCgxajSWjkAQvqBsQsnRri1i_5OBCHrV4AMMyCzdi7gc'

def scraper(artist_name):
    lyric_list = []

    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_TOKEN_KEY}
    search_url = base_url + '/search?per_page=10&page=1'
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    jfile = response.json()

    for i in jfile['response']['hits']:
        slug = i['result']['url']
        song = i['result']['title']

        page = requests.get(slug)

        html = BeautifulSoup(page.text, "html.parser")

        lyrics = html.find('div', class_='lyrics').get_text()
        lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
        lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
        lyric_list.append([song,lyrics])
    return lyric_list
        
    

if __name__ == '__main__':
    artist_name = input('Enter Artist Name:\n').lower()

    mainpath = os.path.abspath('Artists_Songs')
    artist_path = os.path.join(mainpath,'%s'%artist_name)
    lyric_list = scraper(artist_name)
   
    if not os.path.isdir(artist_path):
        os.mkdir(artist_path)

    for i in lyric_list:
        songname = re.sub(r'[*?]', '', str(i[0]).lower())
        filename = os.path.join(artist_path,songname+'.txt')
        with open(filename, 'wb') as f:
            f.write(str(i[1]).encode('utf-8'))
            f.close()
