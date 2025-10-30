import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

# -------------------------------
# PARAMETRI PRINCIPALI
# -------------------------------
st.title("🏨 Generatore Prenotazioni Hotel")

# Sidebar
num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

richiesto_N0 = 20       # richieste iniziali
scala_prezzi = 90       # scala prezzi
sensibilità = 0.1       # pendenza sigmoide

oggi = datetime.now().date()

# -------------------------------
# Tabella prezzi modificabili
# -------------------------------
prezzi_base = [100] * num_giorni
df_prezzi = pd.DataFrame({
    "Giorni avanti": list(range(num_giorni)),
    "Prezzo": prezzi_base
})

st.subheader("📊 Prezzi per giorno (modificabili)")
df_editor = st.data_editor(
    df_prezzi,
    column_config={"Prezzo": st.column_config.NumberColumn("Prezzo", step=1, min_value=0)},
    hide_index=True
)

# -------------------------------
# Calcolo prenotazioni
# -------------------------------
# Disponibilità camere per ogni giorno futuro
disponibilità_camere = {oggi + timedelta(days=i): num_camere for i in range(num_giorni)}
data = []

for giorno_corrente in range(num_giorni):
    data_prenotazione = oggi + timedelta(days=giorno_corrente)

    # Simula richieste per ogni check-in futuro
    for giorni_avanti in range(1, num_giorni - giorno_corrente):
        check_in = data_prenotazione + timedelta(days=giorni_avanti)
        prezzo = df_editor.at[giorni_avanti, "Prezzo"]

        # Richieste decrescono all'aumentare dei giorni avanti
        richieste = max(richiesto_N0 - giorni_avanti, 1)

        # Conversion rate sigmoide inversa del prezzo
        conv_rate = 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

        # Prenotazioni effettive limitate dalla disponibilità camere
        prenotazioni_eff = min(int(richieste * conv_rate), disponibilità_camere[check_in])
        disponibilità_camere[check_in] -= prenotazioni_eff

        # Salva dati prenotazione
        data.append({
            "DATA PRENOTAZIONE": data_prenotazione,
            "CHECK IN": check_in,
            "Prezzo": prezzo,
            "Richieste": richieste,
            "Conversion rate": round(conv_rate, 4),
            "Prenotazioni": prenotazioni_eff,
            "Camere occupate quel giorno": num_camere - disponibilità_camere[check_in]
        })

# -------------------------------
# Creazione DataFrame prenotazioni
# -------------------------------
df_prenotazioni = pd.DataFrame(data)

# -------------------------------
# Visualizzazione
# -------------------------------
st.subheader("📅 Prenotazioni generate")
st.dataframe(df_prenotazioni)

# Grafico camere occupate per giorno
st.subheader("🏨 Camere occupate per giorno")
camere_per_giorno = df_prenotazioni.groupby('CHECK IN')['Prenotazioni'].sum()
st.bar_chart(camere_per_giorno)

# Download CSV
csv = df_prenotazioni.to_csv(index=False).encode('utf-8')
st.download_button(
    "💾 Scarica CSV",
    csv,
    file_name="prenotazioni_hotel.csv",
    mime="text/csv"
)
