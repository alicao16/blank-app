import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import math

# -------------------------------
# PARAMETRI PRINCIPALI
# -------------------------------
st.title("🏨 Generatore Prenotazioni Hotel")

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Giorni da generare", 10, 365, 60)
prenotazioni_giornaliere = st.sidebar.number_input("Prenotazioni giornaliere", 1, 20, 5)
min_price = st.sidebar.number_input("Prezzo minimo (€)", 50, 500, 100)
max_price = st.sidebar.number_input("Prezzo massimo (€)", 50, 1000, 200)
alpha = 0.3
beta = 0.2

check_in_iniziale = datetime.now().date()
check_out_finale = check_in_iniziale + timedelta(days=num_giorni)
date_range = pd.date_range(start=check_in_iniziale, end=check_out_finale - timedelta(days=1))

# -------------------------------
# VARIABILI PER LA SIMULAZIONE
# -------------------------------
data = []
disponibilita_camere = {date: num_camere for date in date_range}

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
numero_prenotazione = 0

for giorno, single_date in enumerate(date_range, start=1):
    prenotazioni_oggi = min(prenotazioni_giornaliere, disponibilita_camere[single_date])
    disponibilita_camere[single_date] -= prenotazioni_oggi

    for _ in range(prenotazioni_oggi):
        numero_prenotazione += 1

        giorni_anticipo = random.randint(1, num_giorni)
        data_prenotazione = single_date - timedelta(days=giorni_anticipo)

        durata_soggiorno = random.randint(1, 3)
        check_in = single_date
        check_out = check_in + timedelta(days=durata_soggiorno)

        camere_rimanenti = disponibilita_camere[single_date]
        occupazione = (num_camere - camere_rimanenti) / num_camere
        incremento = alpha * math.tanh(beta * (1 - occupazione))
        prezzo_finale = min_price + (max_price - min_price) * incremento

        data.append({
            'GIORNO': giorno,
            'DATA PRENOTAZIONE': data_prenotazione,
            'NUMERO CAMERE': num_camere,
            'NUMERO PRENOTAZIONE': numero_prenotazione,
            'CHECK IN': check_in,
            'CHECK OUT (mattina)': check_out,
            'DURATA SOGGIORNO (notti)': durata_soggiorno,
            'PREZZO': round(prezzo_finale, 2),
            'NUMERO CAMERE OCCUPATE': num_camere - camere_rimanenti
        })



# -------------------------------
# VISUALIZZAZIONE CON STREAMLIT
# -------------------------------
st.subheader("📅 Prenotazioni Generate")

# Grafico prezzi
st.subheader("📈 Andamento Prezzi nel Tempo")

# Download CSV
csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
st.download_button(
    label="💾 Scarica CSV delle prenotazioni",
    data=csv,
    file_name='prenotazioni_hotel.csv',
    mime='text/csv'
)
