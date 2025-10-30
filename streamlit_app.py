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
st.subheader("📌 Prezzi base (modificabili)")
prezzi_editor = st.data_editor(
    pd.DataFrame({"Giorni avanti": list(range(num_giorni)), "Prezzo": [100]*num_giorni}),
    column_config={"Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0, step=1)},
    hide_index=True,
    use_container_width=True
)
prezzi_base = prezzi_editor["Prezzo"].tolist()

# -------------------------------
# Inizializza camere occupate per ogni giorno
# -------------------------------
camere_occupate_per_giorno = {oggi + timedelta(days=i): 0 for i in range(num_giorni)}

# -------------------------------
# Funzione conversion rate
# -------------------------------
def conversion_rate(prezzo):
    return 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

# -------------------------------
# Simulazione prenotazioni
# -------------------------------
data = []
numero_prenotazione = 0

for giorno_corrente in range(num_giorni):
    data_prenotazione = oggi + timedelta(days=giorno_corrente)
    
    # Prenotazioni per tutti i check-in futuri
    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        data_checkin = oggi + timedelta(days=giorni_avanti)
        prezzo = prezzi_base[giorni_avanti]

        # Calcolo conversion rate
        conv_rate = conversion_rate(prezzo)

        # Prenotazioni potenziali
        prenotazioni_da_aggiungere = int(richiesto_N0 * conv_rate)

        # Limita prenotazioni totali a num_camere
        posti_disponibili = num_camere - camere_occupate_per_giorno[data_checkin]
        prenotazioni_effettive = min(prenotazioni_da_aggiungere, posti_disponibili)

        # Aggiorna camere occupate
        camere_occupate_per_giorno[data_checkin] += prenotazioni_effettive

        # Salva prenotazioni individuali
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
