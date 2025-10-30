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

# Sidebar per parametri principali
num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

# Parametri della simulazione
richiesto_N0 = 20       # richieste iniziali
scala_tempi = 50        # influenza dei giorni avanti
scala_prezzi = 90       # sensibilità al prezzo
sensibilità = 0.1       # pendenza della sigmoide per la conversione

oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)

# -------------------------------
# PREZZI BASE PER GIORNO (modificabili)
# -------------------------------
st.subheader("Prezzi base per giorno")
df_prezzi = pd.DataFrame({
    "Data": [oggi + timedelta(days=i) for i in range(num_giorni)],
    "Prezzo Base": [100] * num_giorni
})

# Tabella interattiva prezzi
df_prezzi_mod = st.data_editor(df_prezzi, num_rows="dynamic")
prezzi_base = df_prezzi_mod["Prezzo Base"].tolist()

# -------------------------------
# FUNZIONI
# -------------------------------
def conversion_rate(prezzo_attuale):
    """Sigmoide inversa: più alto il prezzo, meno conversioni"""
    return 1 / (1 + math.exp(sensibilità * (prezzo_attuale - scala_prezzi)))

def calcola_prenotazioni(prezzo, richieste, numero_camere):
    """Numero di prenotazioni effettive per quel giorno"""
    c = conversion_rate(prezzo)
    return min(int(richieste * c), numero_camere)

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
        prezzo = prezzi_base[giorni_avanti]  # prezzo del giorno di check-in

        richieste = richiesto_N0
        prenotazioni_effettive = min(
            calcola_prenotazioni(prezzo, richieste, disponibilità_camere[data_checkin]),
            disponibilità_camere[data_checkin]
        )

        disponibilità_camere[data_checkin] -= prenotazioni_effettive

        for _ in range(prenotazioni_effettive):
            data.append({
                'DATA PRENOTAZIONE': data_prenotazione,
                'NUMERO PRENOTAZIONE': numero_prenotazione,
                'CHECK IN': data_checkin,
                'CHECK OUT (mattina)': data_checkin + timedelta(days=1),
                'DURATA SOGGIORNO (notti)': 1,
                'PREZZO BASE': prezzo,
                'PREZZO MODIFICABILE': prezzo,  # nuova colonna modificabile
                'CAMERE TOTALI': num_camere,
                'CAMERE OCCUPATE QUEL GIORNO': num_camere - disponibilità_camere[data_checkin]
            })
            numero_prenotazione += 1

# -------------------------------
# CREAZIONE DEL DATAFRAME
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# VISUALIZZAZIONE STREAMLIT
# -------------------------------
st.subheader("📅 Prenotazioni Generate")
# Tabella interattiva con possibilità di modificare i prezzi
df_prenotazioni_mod = st.data_editor(df_prenotazioni, column_config={
    "PREZZO MODIFICABILE": st.column_config.NumberColumn("Prezzo", step=1)
})

# Numero prenotazioni giornaliere
st.subheader("🏨 Camere Occupate per Giorno (effettive)")
camere_occupate_per_giorno = {}
for _, row in df_prenotazioni_mod.iterrows():
    giorni_soggiorno = pd.date_range(start=row['CHECK IN'], end=row['CHECK OUT (mattina)'] - timedelta(days=1))
    for g in giorni_soggiorno:
        camere_occupate_per_giorno[g.date()] = camere_occupate_per_giorno.get(g.date(), 0) + 1

df_camere_occupate = pd.DataFrame(list(camere_occupate_per_giorno.items()), columns=["Data", "Camere Occupate"])
df_camere_occupate = df_camere_occupate.sort_values("Data").set_index("Data")
st.bar_chart(df_camere_occupate)

# -------------------------------
# DOWNLOAD CSV
# -------------------------------
if not df_prenotazioni_mod.empty:
    csv = df_prenotazioni_mod.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Scarica CSV delle prenotazioni",
        data=csv,
        file_name='prenotazioni_hotel.csv',
        mime='text/csv'
    )
