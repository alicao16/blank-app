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
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)
prenotazioni_giornaliere = st.sidebar.number_input("Prenotazioni ricevute ogni giorno", 1, 20, 5)
min_price = st.sidebar.number_input("Prezzo minimo (€)", 50, 500, 100)
max_price = st.sidebar.number_input("Prezzo massimo (€)", 50, 1000, 200)
alpha = 0.3
beta = 0.3

oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)
giorni_prenotazioni = pd.date_range(start=oggi, end=fine_periodo - timedelta(days=1))

# -------------------------------
# VARIABILI PER LA SIMULAZIONE
# -------------------------------
data = []
disponibilita_camere = {date: num_camere for date in pd.date_range(start=oggi, end=fine_periodo)}
random.seed(42)

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
numero_prenotazione = 0

for data_prenotazione in giorni_prenotazioni:
    for _ in range(prenotazioni_giornaliere):
        numero_prenotazione += 1

        # Il check-in è da 1 a num_giorni dopo la prenotazione
        giorni_anticipo = random.randint(1, num_giorni)
        data_checkin = data_prenotazione + timedelta(days=giorni_anticipo)

        # Se il check-in supera il periodo simulato, salta
        if data_checkin >= fine_periodo:
            continue

        # Durata del soggiorno (1–5 notti)
        durata_soggiorno = random.randint(1, 5)
        data_checkout = data_checkin + timedelta(days=durata_soggiorno)

        # Controllo camere disponibili
        camere_rimanenti = disponibilita_camere[data_checkin]
        if camere_rimanenti <= 0:
            continue

        disponibilita_camere[data_checkin] -= 1

        # Prezzo dinamico basato sull’occupazione
        occupazione = (num_camere - camere_rimanenti) / num_camere
        incremento = alpha * math.tanh(beta * (1 - occupazione))
        prezzo_finale = min_price + (max_price - min_price) * incremento

        # Salva prenotazione
        data.append({
            'DATA PRENOTAZIONE': data_prenotazione.date(),
            'NUMERO PRENOTAZIONE': numero_prenotazione,
            'CHECK IN': data_checkin.date(),
            'CHECK OUT (mattina)': data_checkout.date(),
            'DURATA SOGGIORNO (notti)': durata_soggiorno,
            'PREZZO': round(prezzo_finale, 2),
            'CAMERE TOTALI': num_camere,
            'CAMERE OCCUPATE QUEL GIORNO': num_camere - camere_rimanenti
        })

# -------------------------------
# CREAZIONE DEL DATAFRAME
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# VISUALIZZAZIONE CON STREAMLIT
# -------------------------------
st.subheader("📅 Prenotazioni Generate")
st.dataframe(df_prenotazioni)

# Grafico prezzi nel tempo
if not df_prenotazioni.empty:
    st.subheader("📈 Andamento Prezzi nel Tempo")
    st.line_chart(df_prenotazioni.set_index('CHECK IN')['PREZZO'])
else:
    st.warning("Nessuna prenotazione generata. Prova a modificare i parametri nel menu laterale.")

# Download CSV
if not df_prenotazioni.empty:
    csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Scarica CSV delle prenotazioni",
        data=csv,
        file_name='prenotazioni_hotel.csv',
        mime='text/csv'
    )
