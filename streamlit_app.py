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
alpha = st.sidebar.number_input("Alpha", 0.1, 1.0, 0.1)
beta= st.sidebar.number_input("Beta", 1.0, 5.0, 1.0)

oggi = pd.Timestamp(datetime.now().date())
fine_periodo = oggi + pd.Timedelta(days=num_giorni)
data_checkin = data_prenotazione + pd.Timedelta(days=giorni_anticipo)

# -------------------------------
data = []
disponibilità_camere = {date.date(): num_camere for date in pd.date_range(start=oggi, end=fine_periodo)}  # camere disponibili per ogni giorno

numero_prenotazione = 0

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
for data_prenotazione in giorni_prenotazioni:
    data_prenotazione = data_prenotazione.date()
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

        # camere rimanenti nel giorno più “critico” (minore disponibilità)
        camere_rimanenti = min(disponibilità_camere.get(g, 0) for g in giorni_soggiorno)

        if camere_rimanenti == 0:
            continue

        # decrementa camere per ogni giorno del soggiorno
        for giorno in giorni_soggiorno:
            disponibilità_camere[giorno] -= 1

        # prezzo dinamico: più camere libere → più vicino al min_price, meno libere → più vicino al max_price
         
        prezzo_finale = min_price + (max_price - min_price) * (math.tanh((alpha*(camere_rimanenti-15)+1)/beta))

        
        # Salva prenotazione
        data.append({
            'DATA PRENOTAZIONE': data_prenotazione,
            'NUMERO PRENOTAZIONE': numero_prenotazione,
            'CHECK IN': data_checkin,
            'CHECK OUT (mattina)': data_checkout,
            'DURATA SOGGIORNO (notti)': durata_soggiorno,
            'PREZZO': round(prezzo_finale, 2),
            'CAMERE TOTALI': num_camere,
            'CAMERE OCCUPATE QUEL GIORNO': num_camere - camere_rimanenti
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
