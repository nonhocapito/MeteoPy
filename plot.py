import numpy as np
import matplotlib.pyplot as plt
import os
import csv

#se non esiste il path indicato, lo crea 
def dir_generator(path):
    if not os.path.isdir(path):
        os.mkdir(path)
        check=True
    else:
        check=False
    return check
    
#genera un file .png nel percorso 'path' indicato a partire dai dati 'x' ed 'y' dati in input
def plot_generator(x, y, output_path, x_label, y_label, plot_title, ext):
    #genera il plot
    plt.figure(figsize=(10, 5))  #imposta la dimensione del grafico
    plt.grid(False)  #opzionale, per aggiungere o rimuovere griglia
    plt.plot(x, y, marker='o', color='b', linestyle='-')  #grafico linea con punti
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(plot_title)
    plt.savefig( output_path , format="png", dpi=300)  # Puoi scegliere 'ext' anche come "jpg", "pdf", ecc.
    plt.close() #si chiude l'immagine generata, per risparmiare memoria

#SETUP DELLE CARTELLE
cwd=os.path.join(os.getcwd(), "output") #directory di lavoro corrente

#lista con i nomi delle sottocartelle nella cartella "output"
place_list = [d for d in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, d))]

#per ogni sottocartella in 'place_list' genera un percorso fino alla sottocartella
#e lo memorizza nella lista 'path_dir'
path_dir = [os.path.join(cwd, place) for place in place_list]

#in ogni sottocartella individuo solo i file con estensione ".csv" e li salvo in una lista
for path in path_dir:
    csv_list = [f for f in os.listdir(path) if f.endswith(".csv") and os.path.isfile(os.path.join(path, f))]
    ext="png"   # Puoi scegliere 'ext' anche come "jpg", "pdf", ecc.
    #apro ogni file csv e genero un grafico che salvo nel percorso 'path'
    for file in csv_list:
        file_name=file.replace(".csv",f".{ext}")   #nome del file da esportare
        file=open( os.path.join(path, file), "r" )  #apertura csv 
        reader=csv.reader(file, delimiter=",")
        rows = list(reader)[1:]  # Converte il reader in una lista di righe
        date, name= rows[0][2], rows[0][0]
        
        #creo due liste per tempo (t_list) e temperatura (T_list)
        t_list, T_list = [row[3] for row in rows], [float(row[7]) for row in rows]
        
        #creo e salvo il grafico
        plot_title=f"{name}, {date}: Temperatura - Orario"
        print(f"Esportazione in corso di '{file_name}'.")
        output_path=os.path.join(path, file_name)
        plot_generator(t_list, T_list, output_path, "ora", "temperatura (°C)", plot_title, ext)
