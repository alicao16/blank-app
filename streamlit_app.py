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

richiesto_N0 = 20       # richieste iniziali
scala_tempi = 50         # influenza dei giorni avanti
scala_prezzi = 90        # sensibilità al prezzo
sensibilità = 0.1        # pendenza della sigmoide per la conversione

num_camere = st.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

oggi = datetime.now().date()
fine_periodo = oggi + timedelta(days=num_giorni)

# -------------------------------
# PREZZI BASE PER GIORNO (modificabili)
# -------------------------------
st.subheader("Prezzi base per giorno")
df_prezzi = pd.DataFrame({
    "Data": [oggi + timedelta(days=i) for i in range(num_giorni)],
    "Prezzo": [100] * num_giorni
})

# Tabella interattiva nella pagina principale
df_prezzi_mod = st.data_editor(df_prezzi, num_rows="dynamic")
prezzi_base = df_prezzi_mod["Prezzo"].tolist()

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

    # Simula richieste per check-in futuri
    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        data_checkin = data_prenotazione + timedelta(days=giorni_avanti)
        prezzo = prezzi_base[giorni_avanti]  # prezzo del giorno di check-in

        richieste = richiesto_N0
        prenotazioni_effettive = min(
            calcola_prenotazioni(prezzo, richieste, disponibilità_camere[data_checkin]),
            disponibilità_camere[data_checkin]
        )

        # Aggiorna disponibilità camere
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
# VISUALIZZAZIONE STREAMLIT
# -------------------------------
st.subheader("📅 Prenotazioni Generate")
st.dataframe(df_prenotazioni)

st.subheader("🏨 Camere Occupate per Giorno (effettive)")
camere_occupate_per_giorno = {}
for _, row in df_prenotazioni.iterrows():
    giorni_soggiorno = pd.date_range(start=row['CHECK IN'], end=row['CHECK OUT (mattina)'] - timedelta(days=1))
    for g in giorni_soggiorno:
        camere_occupate_per_giorno[g.date()] = camere_occupate_per_giorno.get(g.date(), 0) + 1

df_camere_occupate = pd.DataFrame(list(camere_occupate_per_giorno.items()), columns=["Data", "Camere Occupate"])
df_camere_occupate = df_camere_occupate.sort_values("Data").set_index("Data")
st.bar_chart(df_camere_occupate)

# -------------------------------
# DOWNLOAD CSV
# -------------------------------
if not df_prenotazioni.empty:
    csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Scarica CSV delle prenotazioni",
        data=csv,
        file_name='prenotazioni_hotel.csv',
        mime='text/csv'
    )
