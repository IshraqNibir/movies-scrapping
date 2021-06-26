from django.shortcuts import render
import re
import csv
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.template import loader
import csv, urllib.request
import threading

data = []
movie_name = []
user_dict = {}
rating_dict = {}

def home(request):
    global data
    data.clear()
    template = loader.get_template('bestmovies/home.html')
    base_informations()
    page = 1
    if request.GET.get('page'):
        page = request.GET.get('page')
        page = int(page)
    page_wise_data = data
    if page == 1:
        th = threading.Thread(target=avg_rating)
        th.start()
        start = -1
    else:
        start = (page - 1) * 20 
    start = start + 1
    end = page * 20
    page_wise_data = page_wise_data[start:end+1]
    context = {
        'movies': page_wise_data,
        'next_page': page + 1,
        'previous_page': page - 1 if page > 1 else 1
    }
    return HttpResponse(template.render(context, request))
    


def base_informations():
    url="https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")

    table = soup.find("table", attrs={"class": "wikitable"})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    # print(rows[1])
    id = 1
    global movie_name
    
    for row in rows:
        cols = row.find_all('td')
        dc = {}
        dc['id'] = id
        global data
        cnt = 1
        for col in cols:
            if col.find('i'):
                tmp = col.find('i')
                movie_link = 'https://en.wikipedia.org'
                if tmp.find('b'):
                    tmp_b = tmp.find('b')
                    movie_text = tmp_b.text
                    movie_name.append(movie_text)
                    for ln in tmp_b.find_all('a'):
                        movie_link = movie_link + ln.get('href')
                else:
                    movie_text = tmp.text
                    for ln in tmp.find_all('a'):
                        movie_link = movie_link + ln.get('href')
                dc['name'] = movie_text
                dc['link'] = movie_link

            else:
                if cnt == 1:
                    movie_year = col.text
                    dc['year'] = movie_year
                    cnt = 2
                elif cnt == 2:
                    movie_award = col.text
                    dc['award'] = movie_award
                    cnt = 3
                else:
                    movie_nominations = col.text
                    dc['nominations'] = movie_nominations
                    # if id == 2:
                    #     print(dc)
                    data.append(dc)
        id = id + 1
                    

def individual_movie_information(request):
    template = loader.get_template('bestmovies/movie.html')
    index = int(request.GET.get('id'))
    index = index - 2
    global data
    movie = data[index]
    url = movie['link']

    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")

    table = soup.find("table", attrs={"class": "infobox"})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    # print(rows)
    movie_data = []
    
    cnt = 1

    for row in rows:
        if cnt == 1 or cnt == 2:
            cnt = cnt + 1
            continue
        cnt = cnt + 1
        cols = row.find_all('td')
        col_head = row.find('th')
        dc_movie = {}
        for col in cols:
            if col.find('div'):
                div = col.find('div')
                if div.find('ul'):
                    ul = div.find('ul')
                    list = ul.find_all('li')
                    values = ''
                    for li in list:
                        if values == '':
                            values = values + li.text
                        else:
                            values = values + ',' + li.text
                    dc_movie[col_head.text] = values
            else:
                try:
                    dc_movie[col_head.text] = col.text
                except:
                    pass

        movie_data.append(dc_movie)

    # print(movie_data)
    context = {
        'movie_info': movie_data, 
    }
    # str = avg_rating()
    return HttpResponse(template.render(context, request))


def avg_rating():
    url_movies = 'https://school.cefalolab.com/assignment/python/movies.csv'
    response_movies = urllib.request.urlopen(url_movies)
    lines_movies = [l.decode('utf-8') for l in response_movies.readlines()]
    cr_movies = csv.reader(lines_movies)

    url_ratings = 'https://school.cefalolab.com/assignment/python/ratings.csv'
    response_ratings = urllib.request.urlopen(url_ratings)
    lines_ratings = [l.decode('utf-8') for l in response_ratings.readlines()]
    cr_ratings = csv.reader(lines_ratings)
    global user_dict
    cnt = 1

    # cereal_df = pd.read_csv("https://school.cefalolab.com/assignment/python/movies.csv")
    # cereal_df2 = pd.read_csv("https://school.cefalolab.com/assignment/python/ratings.csv")

    for row in cr_ratings:
        if cnt == 1:
            cnt = cnt + 1
            continue
        movie_id = row[1]
        rating = row[2]
        if user_dict.get(movie_id):
            user_dict[movie_id] = user_dict[movie_id] + 1
            rating_dict[movie_id] = float(rating_dict[movie_id]) + float(rating)
        else:
            user_dict[movie_id] =  1
            rating_dict[movie_id] = float(rating)

    for k in rating_dict.keys():
        rating_dict[k] = rating_dict[k]/user_dict[k]
        rating_dict[k] = "{:.2f}".format(rating_dict[k])

