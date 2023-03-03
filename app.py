from flask import Flask, request, send_file, jsonify
from pytube import YouTube
import json
from flask_cors import CORS
import io
import urllib.request
from bs4 import BeautifulSoup
import os
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#import requests
app = Flask(__name__)
cors = CORS(app)


@app.route("/download", methods=["POST"])
def download():
    try:
        yt = YouTube(request.json['url'])
        file_path = yt.streams.filter(only_audio=True).get_by_itag('140').download()
        
        temp_file = io.BytesIO()
        with open(file_path, 'rb') as fo:
            temp_file.write(fo.read())
        # (after writing, cursor will be at last byte, so move it to start)
        temp_file.seek(0)
        os.remove(file_path)
        return send_file(temp_file, as_attachment=True, download_name='song.mp3' )
    except Exception as e:
        print(f"Error downloading..: {e}") 

@app.route("/search_song", methods=["POST"])
def search_song():
    """
    page = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + request.json['title']).read()
    
    #Crear una sesión de Firefox
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    driver.maximize_window()

    print('response', request.json)
    # Acceder a la aplicación web
    driver.get('https://www.youtube.com/results?search_query=' + 'futari')
    
    # Obtener la lista de resultados de la búsqueda y mostrarla
    # mediante el método find_elements_by_class_name
    lists= driver.find_elements_by_class_name("style-scope ytd-item-section-renderer")
    #lists= driver.find_elements_by_class_name("yt-simple-endpoint style-scope ytd-video-renderer") 
    # Pasar por todos los elementos y reproducir el texto individual

    i=0 
    response = dict()
    for listitem in lists:
        #print(listitem.get_attribute("innerHTML"))        
        item = BeautifulSoup(listitem.get_attribute("innerHTML"))
        titles = item.find_all(class_="yt-simple-endpoint inline-block style-scope ytd-thumbnail")
        for title in titles:
            #response.append("https://www.youtube.com" + title['href'])
            response[title['href']] = "https://www.youtube.com" + title['href']
            print(title['href'])

    # Cerrar la ventana del navegador
    driver.quit()
    return jsonify(response)
    """
    #TODO trabajar el request de title para aceptar espacios. Ej: ride on time = ride+on+time
    page = urllib.request.urlopen('https://www.youtube.com/results?search_query=' + request.json['title']).read()
    soup = BeautifulSoup(page, "html.parser")
    body = soup.find('body')
    print(f"Now Scraping")
    script = body.find_all('script')
    lista = script[13].string.split(",")
    response = dict()
    song = dict()
    i=0
    for item in lista: 
        if 'title' in item or 'thumbnails' in item or '/watch' in item:
            if 'title' in item:
                title = item
                response[title] = {'title': clean_title(title)}
            if 'thumbnails' in item:
                thumb = item
                response[title]['thumb'] = clean_thumb(thumb)
                
            if '/watch' in item:
                watch = item 
                response[title]['watch'] = clean_watch(watch)    

    result = list(response.values())
    return json.dumps(result)

    
    
def clean_title(title): 
    if 'text' in title:
        title = title.replace("text", "")
        title = title.replace("title", "")
        title = title.replace("runs", "")
        title = title.replace("{", "")
        title = title.replace("}", "")
        title = title.replace("[", "")
        title = title.replace("]", "") 
        title = title.replace(":", "")
        title = title.replace('"\"', "")
        title = title.replace('"', "")
        return title
    
def clean_watch(watch):
    if 'commandMetadata' in watch:
        watch = watch.replace("commandMetadata", "")
        watch = watch.replace("webCommandMetadata", "")
        watch = watch.replace("url", "")
        watch = watch.replace("{", "")
        watch = watch.replace(":", "")
        watch = watch.replace('"\"', "")
        watch = watch.replace('"', "")
        return 'https://www.youtube.com' + watch

def clean_thumb(thumb):
    if 'thumbnails' in thumb:
        thumb = thumb.replace("thumbnail", "")
        thumb = thumb.replace("thumbnails", "")
        thumb = thumb.replace("url", "")
        thumb = thumb.replace("{", "")
        thumb = thumb.replace("[", "")
        thumb = thumb.replace(":", "")
        thumb = thumb.replace('"\"', "")
        thumb = thumb.replace('"s', "")
        thumb = thumb.replace('"', "")
        thumb = thumb.replace("https", "https:")
        return thumb


if __name__ == '__main__':
    app.run(debug=True)