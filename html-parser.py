from bs4 import BeautifulSoup
import requests
import sqlite3


class KinopoiskTopParser():
    site_url = 'https://www.kinopoisk.ru/top/'

    # Записываем результат в базу
    def write_db(self, films):
        conn = sqlite3.connect("test-database.db")
        cursor = conn.cursor()

        # Создаем таблицу
        cursor.execute("""CREATE TABLE IF NOT EXISTS films
                                (id INTEGER PRIMARY KEY,
                                 name TEXT, 
                                 url TEXT, 
                                 likes INT,
                                 dislikes INT
                                 )
                       """)
        cursor.executemany("INSERT INTO films(name, url, likes, dislikes) VALUES (?,?,?,?)", films)
        conn.commit()
        sql = "select * from films limit 10"
        cursor.execute(sql)
        print(cursor.fetchall())

    # Получаем ссылки на все фильмы
    def get_film_links(self):
        response = requests.get(self.site_url)
        html = BeautifulSoup(response.content, 'html.parser')
        links_to_films = html.select('table.js-rum-hero a.all')
        return [''.join(['https://www.kinopoisk.ru', tag.attrs['href']]) for tag in links_to_films]

    # Получаем оценки
    def get_rates(self, link):
        response = requests.get(link)
        html = BeautifulSoup(response.content, 'html.parser')
        name = html.find('h1', {'class': 'moviename-big'}).text
        likes = html.find('li', {'class': 'pos'}).find('b').text
        dislikes = html.find('li', {'class': 'neg'}).find('b').text

        return [name, link, int(likes), int(dislikes)]

    def start_parsing(self):
        film_links = self.get_film_links()
        films_info = []
        for link in film_links:
            films_info.append(self.get_rates(link))
        self.write_db(films_info)

if __name__ == '__main__':
    kinopoisk_top_parser = KinopoiskTopParser()
    kinopoisk_top_parser.start_parsing()

