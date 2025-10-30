import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import math
import altair as alt


# -------------------------------
# PARAMETRI PRINCIPALI
# -------------------------------
st.title("🏨 Generatore Prenotazioni Hotel")

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)
prenotazioni_giornaliere = st.sidebar.number_input("Prenotazioni ricevute ogni giorno", 1, 20, 1)
min_price = st.sidebar.number_input("Prezzo minimo (€)", 50, 500, 100)
max_price = st.sidebar.number_input("Prezzo massimo (€)", 50, 1000, 200)
alpha = 0.3
beta = 2


oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)


# -------------------------------
data = []
disponibilità_camere = {date.date(): num_camere for date in pd.date_range(start=oggi, end=fine_periodo)}  # camere disponibili per ogni giorno

numero_prenotazione = 0

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
giorni_prenotazioni = [oggi + timedelta(days=i) for i in range(num_giorni)]

for data_prenotazione in giorni_prenotazioni:
    prenotazioni_giornaliere_effettuate = 0
    tentativi = 0
    

    while prenotazioni_giornaliere_effettuate < prenotazioni_giornaliere and tentativi < prenotazioni_giornaliere: 
        prenotazioni_giornaliere_effettuate +=1
        tentativi += 1
        

        # Il check-in è da 1 a num_giorni dopo la prenotazione
        giorni_anticipo = random.randint(1, num_giorni)
        data_checkin = data_prenotazione + timedelta(days=giorni_anticipo)

        # Salta se il check-in supera il periodo simulato
        if data_checkin >= fine_periodo:
            continue

        # Durata del soggiorno
        durata_soggiorno = random.randint(1, 3)
        data_checkout = data_checkin + timedelta(days=durata_soggiorno)

        # lista dei giorni del soggiorno
        giorni_soggiorno = [data_checkin + timedelta(days=i) for i in range(durata_soggiorno)]

        # 1) controllo disponibilità: ogni giorno del soggiorno deve avere almeno 1 camera
        if any(disponibilità_camere.get(g, 0) <= 0 for g in giorni_soggiorno):
            continue

        # 2) calcolo camere occupate AL MOMENTO del check-in (prima di decrementare)
        camere_disponibili_oggi = disponibilità_camere.get(data_checkin, 0)
        camere_occupate = num_camere - camere_disponibili_oggi

        # 3) calcolo prezzo basato su camere_occupate (tanh normalizzata)
        centro = num_camere / 2
        prezzo_finale = min_price + (max_price - min_price) * 0.5 * (1 + math.tanh(alpha * (camere_occupate - centro) / beta))
        prezzo_finale = round(prezzo_finale, 2)

        # 4) ora decrementa 1 camera per ogni giorno del soggiorno (una camera riservata su più giorni)
        for giorno in giorni_soggiorno:
            disponibilità_camere[giorno] -= 1

    
        numero_prenotazione += 1
        prenotazioni_giornaliere_effettuate += 1


        
        # Salva prenotazione
        data.append({
            'DATA PRENOTAZIONE': data_prenotazione,
            'NUMERO PRENOTAZIONE': numero_prenotazione,
            'CHECK IN': data_checkin,
            'CHECK OUT (mattina)': data_checkout,
            'DURATA SOGGIORNO (notti)': durata_soggiorno,
            'PREZZO': round(prezzo_finale, 2),
            'CAMERE TOTALI': num_camere,
            'CAMERE OCCUPATE QUEL GIORNO': camere occupate
        })
        numero_prenotazione += 1
# -------------------------------
# CREAZIONE DEL DATAFRAME
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# VISUALIZZAZIONE CON STREAMLIT
# -------------------------------
st.subheader("📅 Prenotazioni Generate")
st.dataframe(df_prenotazioni)

# Numero prenotazioni giornaliere
st.subheader("📊 Numero Prenotazioni per Giorno")
prenotazioni_giornaliere_df = df_prenotazioni.groupby('CHECK IN').size().rename("Numero Prenotazioni")
st.bar_chart(prenotazioni_giornaliere_df)

# Grafico prezzi nel tempo
if not df_prenotazioni.empty:
    st.subheader("📈 Andamento Prezzi nel Tempo")
    st.line_chart(df_prenotazioni.set_index('CHECK IN')['PREZZO'])
else:
    st.warning("Nessuna prenotazione generata. Prova a modificare i parametri nel menu laterale.")


if not df_prenotazioni.empty:
    st.subheader("💰 Prezzo vs Camere Occupate")
    chart = alt.Chart(df_prenotazioni).mark_circle(size=60).encode(
        x='CAMERE OCCUPATE QUEL GIORNO',
        y='PREZZO',
        tooltip=['DATA PRENOTAZIONE','CHECK IN','CAMERE OCCUPATE QUEL GIORNO','PREZZO']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)


# Download CSV
if not df_prenotazioni.empty:
    csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Scarica CSV delle prenotazioni",
        data=csv,
        file_name='prenotazioni_hotel.csv',
        mime='text/csv'
    )
