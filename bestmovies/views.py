from django.shortcuts import render
import re

# Create your views here.

from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.template import loader

data = []

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
    return HttpResponse("Info")