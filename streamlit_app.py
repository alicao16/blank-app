import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

# -------------------------------
# Parametri principali
# -------------------------------
st.title("🏨 Simulatore Prenotazioni Hotel")

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

richiesto_N0 = st.sidebar.number_input("Richieste iniziali", 1, 100, 20)
scala_prezzi = st.sidebar.number_input("Scala prezzi", 10, 500, 90)
sensibilità = st.sidebar.number_input("Sensibilità sigmoide", 0.01, 1.0, 0.1)

oggi = datetime.now().date()

# -------------------------------
# Prezzi base per ogni giorno
# -------------------------------
prezzi_base = [100] * num_giorni  # inizialmente 100€
st.subheader("📌 Prezzi base (modificabili)")
prezzi_editor = st.data_editor(
    pd.DataFrame({"Giorni avanti": list(range(num_giorni)), "Prezzo": prezzi_base}),
    column_config={"Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0, step=1)},
    hide_index=True,
    use_container_width=True
)
prezzi_base = prezzi_editor["Prezzo"].tolist()

# -------------------------------
# Array/dizionario per camere occupate per giorno
# -------------------------------
camere_occupate_per_giorno = {oggi + timedelta(days=i): 0 for i in range(num_giorni)}

# -------------------------------
# Simulazione prenotazioni
# -------------------------------
data = []
numero_prenotazione = 0

for giorno_corrente in range(num_giorni):
    data_prenotazione = oggi + timedelta(days=giorno_corrente)
    
    # Genera prenotazioni per ogni check-in futuro
    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        data_checkin = data_prenotazione + timedelta(days=giorni_avanti)
        prezzo = prezzi_base[giorni_avanti]

        # Conversion rate inversamente proporzionale al prezzo
        conv_rate = 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

        # Numero di prenotazioni desiderato
        prenotazioni_da_aggiungere = int(richiesto_N0 * conv_rate)

        # Limita le prenotazioni in modo che non superino num_camere
        prenotazioni_effettive = 0
        while prenotazioni_da_aggiungere > 0 and camere_occupate_per_giorno[data_checkin] < num_camere:
            camere_occupate_per_giorno[data_checkin] += 1
            prenotazioni_effettive += 1
            prenotazioni_da_aggiungere -= 1

        # Salva prenotazioni
        for _ in range(prenotazioni_effettive):
            data.append({
                "DATA PRENOTAZIONE": data_prenotazione,
                "NUMERO PRENOTAZIONE": numero_prenotazione,
                "CHECK IN": data_checkin,
                "PREZZO": prezzo,
                "CONVERSION RATE": round(conv_rate, 4),
                "CAMERE OCCUPATE": camere_occupate_per_giorno[data_checkin]
            })
            numero_prenotazione += 1

# -------------------------------
# Creazione DataFrame
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# Visualizzazione Streamlit
# -------------------------------
st.subheader("📅 Prenotazioni generate")
st.dataframe(df_prenotazioni)

st.subheader("🏨 Camere occupate per giorno")
st.bar_chart(pd.DataFrame.from_dict(camere_occupate_per_giorno, orient="index", columns=["Camere Occupate"]))
