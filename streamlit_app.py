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


richiesto_N0 = 20          # richieste iniziali
scala_tempi = 50            # influenza dei giorni avanti
scala_prezzi = 90           # sensibilità al prezzo
sensibilità = 0.1           # pendenza della sigmoide per la conversione

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)


oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)


# Prezzi base per giorno: input modificabile dall'utente
st.sidebar.subheader("Prezzi base per giorno")
prezzi_input = st.sidebar.text_area(
    "Inserisci i prezzi separati da virgola",
    value="100," * num_giorni  # default 100€ per tutti i giorni
)
# Trasforma in lista di float
prezzi_base = [float(p.strip()) for p in prezzi_input.split(",") if p.strip()]



# Funzione conversion rate come sigmoide inversa del prezzo
def conversion_rate(prezzo_attuale):
    # formula sigmoide: più alto il prezzo, meno conversioni
    return 1 / (1 + math.exp(sensibilità * (prezzo_attuale - scala_prezzi)))

# Funzione prenotazioni
def prenotazioni(prezzo, richieste, numero_camere):
    c = conversion_rate(prezzo)
    return min(int(richieste * c), numero_camere)


# Esempio calcolo per tutti i giorni
for giorno, prezzo in enumerate(prezzi_base):
    r = richiesto_N0
    n = prenotazioni(prezzo, r, num_camere)
    print(f"Giorno {giorno}: Prezzo={prezzo}, Prenotazioni={n}")
    

# Inizializza array/dizionario con tutte le date e 0 prenotazioni
camere_occupate_per_giorno = {oggi + timedelta(days=i): 0 for i in range(num_giorni)}
data = []
disponibilità_camere = {date.date(): num_camere for date in pd.date_range(start=oggi, end=fine_periodo)}  # camere disponibili per ogni giorno

numero_prenotazione = 0


# Inizializza disponibilità camere per ogni giorno futuro
disponibilità_camere = {oggi + timedelta(days=i): num_camere for i in range(num_giorni)}

data = []
numero_prenotazione = 0

for giorno_corrente in range(num_giorni):
    data_prenotazione = oggi + timedelta(days=giorno_corrente)
    
    # Simula richieste per ogni check-in futuro
    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        data_checkin = data_prenotazione + timedelta(days=giorni_avanti)
        prezzo = prezzi_base[giorni_avanti]  # prezzo del giorno di check-in

        # Calcola quante prenotazioni avvengono per quel giorno
        richieste = richiesto_N0
        conv_rate = conversion_rate(prezzo)
        prenotazioni_effettive = min(int(richieste * conv_rate), disponibilità_camere[data_checkin])

        # Aggiorna camere disponibili
        disponibilità_camere[data_checkin] -= prenotazioni_effettive

        # Salva le prenotazioni
        for _ in range(prenotazioni_effettive):
            data.append({
                'DATA PRENOTAZIONE': data_prenotazione,
                'NUMERO PRENOTAZIONE': numero_prenotazione,
                'CHECK IN': data_checkin,
                'CHECK OUT (mattina)': data_checkin + timedelta(days=1),
                'DURATA SOGGIORNO (notti)': 1,
                'PREZZO': prezzo,
                'CAMERE TOTALI': num_camere,
                'CAMERE OCCUPATE QUEL GIORNO': num_camere - disponibilità_camere[data_checkin]
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
st.subheader("🏨 Camere Occupate per Giorno (effettive)")

# Calcolo camere occupate per giorno
camere_occupate_per_giorno = {}

for _, row in df_prenotazioni.iterrows():
    giorni_soggiorno = pd.date_range(start=row['CHECK IN'], end=row['CHECK OUT (mattina)'] - timedelta(days=1))
    for g in giorni_soggiorno:
        camere_occupate_per_giorno[g.date()] = camere_occupate_per_giorno.get(g.date(), 0) + 1

# Conversione in DataFrame ordinato per data
df_camere_occupate = pd.DataFrame(list(camere_occupate_per_giorno.items()), columns=["Data", "Camere Occupate"])
df_camere_occupate = df_camere_occupate.sort_values("Data").set_index("Data")




# Download CSV
if not df_prenotazioni.empty:
    csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Scarica CSV delle prenotazioni",
        data=csv,
        file_name='prenotazioni_hotel.csv',
        mime='text/csv'
    )
