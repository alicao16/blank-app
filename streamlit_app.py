import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

# -------------------------------
# Parametri principali
# -------------------------------
st.title("🏨 Generatore Prenotazioni Hotel")

num_camere = st.sidebar.number_input("Numero totale camere", 10, 200, 30)
num_giorni = st.sidebar.number_input("Periodo simulato (giorni futuri)", 10, 365, 60)

richiesto_N0 = 20       # richieste iniziali
scala_prezzi = 90       # scala prezzi
sensibilità = 0.1       # pendenza sigmoide

oggi = datetime.now().date()

# -------------------------------
# Inizializza DataFrame con prezzi modificabili
# -------------------------------
prezzi_base = [100] * num_giorni
df_tabella = pd.DataFrame({
    "Giorni avanti": list(range(num_giorni)),
    "Prezzo": prezzi_base,
    "Richieste": [richiesto_N0 - i if richiesto_N0 - i > 0 else 1 for i in range(num_giorni)],
    "Conversion rate": 0.0,
    "Prenotazioni": 0,
    "Camere occupate": 0
})

# -------------------------------
# Funzione per aggiornare conversion rate e prenotazioni
# -------------------------------
def aggiorna_prenotazioni(df):
    disponibilità_camere = {oggi + timedelta(days=i): num_camere for i in range(num_giorni)}

    for i, row in df.iterrows():
        check_in = oggi + timedelta(days=row["Giorni avanti"])
        prezzo = row["Prezzo"]
        richieste = row["Richieste"]

        # Conversion rate sigmoide inversa del prezzo
        conv_rate = 1 / (1 + math.exp(sensibilità * (prezzo - scala_prezzi)))

        # Prenotazioni effettive limitate dalle camere disponibili
        prenotazioni_previste = int(richieste * conv_rate)
        prenotazioni_effettive = min(prenotazioni_previste, disponibilità_camere[check_in])
        disponibilità_camere[check_in] -= prenotazioni_effettive

        df.at[i, "Conversion rate"] = round(conv_rate, 4)
        df.at[i, "Prenotazioni"] = prenotazioni_effettive
        df.at[i, "Camere occupate"] = num_camere - disponibilità_camere[check_in]

    return df

# -------------------------------
# Tabella interattiva
# -------------------------------
st.subheader("📊 Prenotazioni giornaliere (modifica Prezzo per aggiornare)")
df_editor = st.data_editor(
    df_tabella,
    column_config={
        "Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0, step=1)
    },
    hide_index=True,
    use_container_width=True
)

# Aggiorna prenotazioni in base ai prezzi modificati
df_finale = aggiorna_prenotazioni(df_editor)
st.dataframe(df_finale)

# -------------------------------
# Grafico camere occupate
# -------------------------------
st.subheader("🏨 Camere occupate per giorno")
st.bar_chart(df_finale.set_index("Giorni avanti")["Camere occupate"])

# -------------------------------
# Download CSV
# -------------------------------
csv = df_finale.to_csv(index=False).encode('utf-8')
st.download_button("💾 Scarica CSV", csv, file_name="prenotazioni_hotel.csv", mime="text/csv")
