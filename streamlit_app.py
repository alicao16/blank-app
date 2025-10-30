import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
import altair as alt

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
# Prezzi base modificabili
# -------------------------------
st.subheader("📌 Prezzi base (modificabili)")
df_prezzi = pd.DataFrame({
    "Giorni avanti": list(range(num_giorni)),
    "Prezzo": [100] * num_giorni
})
df_prezzi_editor = st.data_editor(
    df_prezzi,
    column_config={"Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0, step=1)},
    hide_index=True,
    use_container_width=True
)
prezzi_base = df_prezzi_editor["Prezzo"].tolist()

# -------------------------------
# Funzione conversion rate
# -------------------------------
def conversion_rate(prezzo):
    return 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

# -------------------------------
# Array/dizionari per prenotazioni
# -------------------------------
camere_occupate_per_giorno = {oggi + timedelta(days=i): 0 for i in range(num_giorni)}

# -------------------------------
# Simulazione prenotazioni per ogni giorno di check-in
# -------------------------------
prenotazioni_totali_per_giorno = []

for giorni_avanti in range(num_giorni):
    data_checkin = oggi + timedelta(days=giorni_avanti)
    
    totale_prenotazioni = 0
    
    # Somma prenotazioni ricevute da tutti i giorni precedenti
    for giorno_corrente in range(giorni_avanti):
        prezzo = prezzi_base[giorni_avanti]
        conv_rate = conversion_rate(prezzo)
        prenotazioni_da_aggiungere = int(richiesto_N0 * conv_rate)
        # Limita per non superare le camere totali
        disponibile = num_camere - totale_prenotazioni
        prenotazioni_da_aggiungere = min(prenotazioni_da_aggiungere, disponibile)
        totale_prenotazioni += prenotazioni_da_aggiungere
    
    conv_rate = conversion_rate(prezzi_base[giorni_avanti])
    prenotazioni_totali_per_giorno.append({
        "Giorni avanti": giorni_avanti,
        "Prezzo": prezzi_base[giorni_avanti],
        "Conversion rate": round(conv_rate, 4),
        "Prenotazioni totali": totale_prenotazioni
    })

df_prenotazioni = pd.DataFrame(prenotazioni_totali_per_giorno)

# -------------------------------
# Visualizzazione Streamlit
# -------------------------------
st.subheader("📅 Prenotazioni per giorno di check-in")
st.data_editor(
    df_prenotazioni,
    column_config={
        "Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0, step=1),
        "Conversion rate": st.column_config.NumberColumn("Conversion rate", disabled=True),
        "Prenotazioni totali": st.column_config.NumberColumn("Prenotazioni totali", disabled=True)
    },
    hide_index=True,
    use_container_width=True
)

st.subheader("🏨 Camere occupate per giorno")
st.bar_chart(df_prenotazioni.set_index("Giorni avanti")["Prenotazioni totali"])

# -------------------------------
# Grafico Prezzo vs Conversion rate
# -------------------------------
st.subheader("📈 Prezzo vs Conversion rate")
chart = alt.Chart(df_prenotazioni).mark_circle(size=80).encode(
    x='Prezzo',
    y='Conversion rate',
    tooltip=['Giorni avanti', 'Prezzo', 'Conversion rate', 'Prenotazioni totali']
).interactive()
st.altair_chart(chart, use_container_width=True)
