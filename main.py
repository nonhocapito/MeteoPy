import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import csv
import numpy as np
import matplotlib.pyplot as plt

#se non esiste il path indicato, lo crea 
def dir_generator(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        check=True
    else:
        check=False
    return check
    
#riceve in input un dato tipo "bs4.element.ResultSet" e restituisce una lista
def from_bs_to_list(bs_element):
    result=str(bs_element).split()  #tipo lista
    return result

# Presa in input una lista di codice html ed un 'target' (tipo str) di ricerca per latitudine e longitudine
# estrae questi valori e assegna un segno "+" (Nord/Est) o "-" (Sud/Ovest) 
def get_latitude(html_list, target):
    index=1+html_list.index(target)
    value=float(html_list[index])
    if "S" in html_list[index+1]:
        value=(-1)*value
    elif "O" in html_list[index+1]:
        value=(-1)*value
    return value
    
def get_info(html_list, target):
    index=1+html_list.index(target)
    value=html_list[index]
    return value

def csv_generator(sub_path, file_name, station_info):
    file_path=os.path.join(sub_path, file_name+".csv")
    head=["name", "location", "date", "time", "latitude", "longitude", "altitude (mslm)", "temp (°C)", "ur (%)", "pressure (hPa)", "rain (mm)", "rain rate (mm/h)", "wind speed (km/h)", "wind dir"]
    #se il file non esiste lo crea
    if not os.path.isfile(file_path):
        file=open(file_path, mode="w", newline="")
        writer=csv.writer(file)
        writer.writerow(head)
        writer.writerow(station_info)
    else:   #se il file esiste già, lo aggiorna
        file=open(file_path, mode="a", newline="")
        writer=csv.writer(file)
        writer.writerow(station_info)
        
#presa in input una lista di opzioni, le stampa a schermo con un indice univoco
#consentendo di sceglierne una
def choose_from_list(options_list, message):
    print(message)
    for i in range(len(options_list)):
        print(f"\t[{i}] {options_list[i]}")
    print()
    n=int(input("Effettua una scelta: "))
    choice=options_list[n]
    return choice

#preso in input un percorso e una estensione, restituisce una lista dei file nel percorso
#con l'estensione indicata 
def read_directory_content(path, ext):
    ext_list=[]
    for cartelle, sottocartelle, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                ext_list.append(file)
    return ext_list

#--------------------------------------------------------------------------------------------
cwd=os.getcwd()
input_folder=os.path.join( cwd, "stations")
output_folder=os.path.join( cwd, "output")

#crea cartella di output se non esiste
dir_generator(output_folder)

#scelta del sorgente per le stazioni meteorologiche
input_file=choose_from_list( read_directory_content(input_folder, ".csv"), "Scegli il sorgente delle stazioni meteo: " )
input_file_path=os.path.join(input_folder, input_file)

rest_time=int( input("Ogni quanti minuti vuoi aggiornare i dati? ") )

cond=True
while cond==True:
    #legge il file sorgente per le stazioni dato in input
    input_file=open(input_file_path, "r")
    reader=csv.reader(input_file, delimiter=",")
    next(reader)    #elimina la prima riga di intestazione dal csv
    
    for row in reader:
        city=row[1]     #legge città
        sub_path=os.path.join(output_folder, city)  #percorso della sottocartella di output per città
        dir_generator(sub_path)                     #se non esiste, genera sottocartella di output
        name=row[2]     #legge il nome della stazione
        url=row[3]      #legge l'url
        try:
            response = requests.get(url)
            response.raise_for_status()  # Alza un'eccezione se la richiesta fallisce

            # Parsing HTML della pagina
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Estrai in blocco tutte le informazioni meteo
            block =soup.find_all("span", {"class": "c_head align-baseline text-right"}) #tipo bs4.element.ResultSet
            block=from_bs_to_list(block) # tipo lista
            temp=float(block[6])
            ur=float(block[15])
            pressure=float(block[24])
            rain=float(block[33])
            rain_rate=float(block[35][1:])
            wind_speed=float(block[44])
            wind_dir=block[46]
            
            #Dettagli della stazione meteo
            details_url=url+"/details"
            response = requests.get(details_url)
            response.raise_for_status()  # Alza un'eccezione se la richiesta fallisce
            soup = BeautifulSoup(response.text, 'html.parser') # Parsing HTML della pagina
            detail_block =soup.find_all("div", {"class": "col-lg-3 col-md-4"}) #tipo bs4.element.ResultSet
            detail_block=from_bs_to_list(detail_block)
            
            location=get_info(detail_block, "<strong>Località:</strong>").replace("<br/>","")
            latitude=get_latitude(detail_block, "<strong>Latitudine:</strong>")
            longitude=get_latitude(detail_block, "<strong>Longitudine:</strong>")
            altitude=float(get_info(detail_block, "<strong>Altitudine:</strong>"))
            
            #qui apri file csv e salvi info
            date=datetime.now().date()
            gtime=datetime.now().strftime("%H:%M")
            station_info=(name, location, date, gtime, latitude, longitude, 
            altitude, temp, ur, pressure, rain, rain_rate, wind_speed, wind_dir)
            print(f"{name}, esportazione > {sub_path}")
            file_name=f"{date}_"+name   #ogni giorno viene creato un file diverso per ogni stazione meteo
            csv_generator(sub_path, file_name, station_info)

        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta per URL {url}: {e}")
    print("Attesa...")
    
    #Rappresentazione dei dati   
    
    time.sleep(rest_time*60)
    
    
