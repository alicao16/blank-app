import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

# -------------------------------
# PARAMETRI PRINCIPALI
# -------------------------------
st.title("🏨 Generatore Prenotazioni Hotel")

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

# Parametri simulazione
richiesto_N0 = 20
scala_prezzi = 90
sensibilità = 0.1

oggi = datetime.now().date()

# Prezzi base per giorno: tutti inizialmente 100€
prezzi_base = [100] * num_giorni

# -------------------------------
# FUNZIONI
# -------------------------------
def conversion_rate(prezzo):
    return 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

def calcola_prenotazioni(prezzo, richieste, camere_disponibili):
    return min(int(richieste * conversion_rate(prezzo)), camere_disponibili)

# -------------------------------
# INIZIALIZZAZIONE
# -------------------------------
disponibilità_camere = {oggi + timedelta(days=i): num_camere for i in range(num_giorni)}
data = []
numero_prenotazione = 0

# -------------------------------
# GENERAZIONE DELLE PRENOTAZIONI
# -------------------------------
for giorno_corrente in range(num_giorni):
    data_prenotazione = oggi + timedelta(days=giorno_corrente)

    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        data_checkin = data_prenotazione + timedelta(days=giorni_avanti)

        # Prenotazioni effettive rispettando la disponibilità
        prenotazioni_effettive = calcola_prenotazioni(
            prezzi_base[giorni_avanti],
            richiesto_N0,
            disponibilità_camere[data_checkin]
        )

        # Aggiorna disponibilità
        disponibilità_camere[data_checkin] -= prenotazioni_effettive

        # Salva prenotazioni
        data.append({
            'DATA PRENOTAZIONE': data_prenotazione,
            'NUMERO PRENOTAZIONE': numero_prenotazione,
            'CHECK IN': data_checkin,
            'PREZZO': prezzi_base[giorni_avanti],
            'PRENOTAZIONI EFFETTIVE': prenotazioni_effettive,
            'CAMERE OCCUPATE QUEL GIORNO': num_camere - disponibilità_camere[data_checkin]
        })
        numero_prenotazione += 1

# -------------------------------
# CREAZIONE DEL DATAFRAME
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# TABELLA INTERATTIVA
# -------------------------------
st.subheader("📅 Prenotazioni Generate")
df_editor = st.data_editor(
    df_prenotazioni,
    column_config={
        "PREZZO": st.column_config.NumberColumn("Prezzo", step=1, min_value=0)
    },
    disabled=["DATA PRENOTAZIONE", "NUMERO PRENOTAZIONE", "CHECK IN", "CAMERE OCCUPATE QUEL GIORNO"],
    hide_index=True
)

# Ricalcolo prenotazioni effettive rispettando disponibilità totale
disponibilità_ricalcolata = {oggi + timedelta(days=i): num_camere for i in range(num_giorni)}

for idx, row in df_editor.iterrows():
    check_in = row['CHECK IN']
    prenotazioni_eff = calcola_prenotazioni(row['PREZZO'], richiesto_N0, disponibilità_ricalcolata[check_in])
    df_editor.at[idx, 'PRENOTAZIONI EFFETTIVE'] = prenotazioni_eff
    disponibilità_ricalcolata[check_in] -= prenotazioni_eff
    df_editor.at[idx, 'CAMERE OCCUPATE QUEL GIORNO'] = num_camere - disponibilità_ricalcolata[check_in]

# -------------------------------
# GRAFICO CAMERE OCCUPATE
# -------------------------------
camere_occupate_per_giorno = df_editor.groupby('CHECK IN')['PRENOTAZIONI EFFETTIVE'].sum()
st.subheader("🏨 Camere Occupate per Giorno")
st.bar_chart(came_occupate_per_giorno)

# -------------------------------
# DOWNLOAD CSV
# -------------------------------
csv = df_editor.to_csv(index=False).encode('utf-8')
st.download_button(
    label="💾 Scarica CSV delle prenotazioni",
    data=csv,
    file_name='prenotazioni_hotel.csv',
    mime='text/csv'
)
