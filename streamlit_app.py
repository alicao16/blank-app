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

oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)    # ultima data simulata
giorni_prenotazioni = pd.date_range(start=oggi, end=fine_periodo - timedelta(days=1))

# -------------------------------
data = []
disponibilità_camere = {date.date(): num_camere for date in pd.date_range(start=oggi, end=fine_periodo)}  # camere disponibili per ogni giorno

numero_prenotazione = 0

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
for data_prenotazione in giorni_prenotazioni:
    data_prenotazione = data_prenotazione.date()  # convertiamo in datetime.date
    for _ in range(prenotazioni_giornaliere):      # per ogni giorno genera tot prenotazioni giornaliere
        numero_prenotazione += 1

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
        camere_rimanenti = min(disponibilita_camere[g] for g in giorni_soggiorno)

        # percentuale di camere libere
        percentuale_libere = camere_rimanenti / num_camere

        # prezzo dinamico: più camere libere → più vicino al min_price, meno libere → più vicino al max_price
        prezzo_finale = min_price + (max_price - min_price) * (1 - percentuale_libere)*alpha

        
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
