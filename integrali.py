# pip install streamlit sympy matplotlib pytesseract pillow python-docx numpy
import streamlit as st
from sympy import symbols, integrate, sympify, latex, lambdify
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pytesseract
from docx import Document
from docx.shared import Inches
import io

# Configurazione della pagina
st.set_page_config(page_title="Risolutore Integrali 2026", layout="centered")

# Funzione per creare il documento Word
def crea_documento_word(tipo, espressione, passaggi, fig):
    doc = Document()
    doc.add_heading(f'Risoluzione Integrale {tipo}', 0)
    
    doc.add_heading('Esercizio:', level=1)
    doc.add_paragraph(f"Funzione inserita: {espressione}")
    
    doc.add_heading('Svolgimento e Passaggi:', level=1)
    for p in passaggi:
        doc.add_paragraph(p)
        
    # Inserimento grafico
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)
    doc.add_heading('Grafico della Funzione:', level=1)
    doc.add_picture(img_stream, width=Inches(4.5))
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

st.title("🧮 Calcolo Integrali Online")
st.write("Inserisci la funzione, visualizza i passaggi e scarica il file Word pronto per la scuola o l'università.")

# Inizializzazione session state per l'input
if "input_math" not in st.session_state:
    st.session_state.input_math = ""

# Funzione helper per i pulsanti
def inserisci_simbolo(simbolo):
    st.session_state.input_math += simbolo

# --- INTERFACCIA DI INPUT ---
st.subheader("1. Inserimento Funzione")

# Pulsanti rapidi
cols = st.columns(7)
tasti = [("√", "sqrt()"), ("^", "**"), ("/", "/"), ("sin", "sin()"), ("cos", "cos()"), ("ln", "log()"), ("π", "pi")]

for i, (label, valore) in enumerate(tasti):
    if cols[i].button(label):
        st.session_state.input_math += valore

# Campo di testo principale
testo_equazione = st.text_input("Scrivi qui la tua funzione f(x):", value=st.session_state.input_math)

# Caricamento Immagine
foto_upload = st.file_uploader("Oppure carica una foto dell'integrale", type=["jpg", "jpeg", "png"])
if foto_upload:
    immagine = Image.open(foto_upload)
    if st.button("Analizza Foto"):
        testo_estratto = pytesseract.image_to_string(immagine).strip()
        st.session_state.input_math = testo_estratto
        st.rerun()

# Limiti di integrazione
st.subheader("2. Parametri")
c1, c2 = st.columns(2)
lim_inf = c1.text_input("Limite Inferiore (a) - opzionale")
lim_sup = c2.text_input("Limite Superiore (b) - opzionale")

# --- CALCOLO E OUTPUT ---
if st.button("CALCOLA E GENERA REPORT", type="primary"):
    if testo_equazione:
        try:
            x = symbols('x')
            f = sympify(testo_equazione)
            passaggi_word = []
            
            # Calcolo Logica
            if not lim_inf and not lim_sup:
                # INTEGRALE INDEFINITO
                risultato = integrate(f, x)
                st.success("Integrale Indefinito Calcolato!")
                st.latex(rf"\int {latex(f)} \, dx = {latex(risultato)} + C")
                passaggi_word = [f"Funzione f(x) = {testo_equazione}", f"Integrale Indefinito: {risultato} + C"]
                tipo_integrale = "Indefinito"
            else:
                # INTEGRALE DEFINITO
                a = sympify(lim_inf)
                b = sympify(lim_sup)
                primitiva = integrate(f, x)
                risultato = integrate(f, (x, a, b))
                st.success("Integrale Definito Calcolato!")
                st.latex(rf"\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(f)} \, dx")
                st.write(f"1. Primitiva: {primitiva}")
                st.write(f"2. Calcolo: F({b}) - F({a})")
                st.latex(rf"= {latex(risultato)}")
                passaggi_word = [
                    f"Funzione f(x) = {testo_equazione}",
                    f"Primitiva F(x) = {primitiva}",
                    f"Limiti di integrazione: da {a} a {b}",
                    f"Risultato finale: {risultato}"
                ]
                tipo_integrale = "Definito"

            # Generazione Grafico
            st.subheader("3. Grafico")
            fig, ax = plt.subplots()
            f_num = lambdify(x, f, "numpy")
            # Range del grafico basato sui limiti o standard
            x_min = float(a.evalf()) - 2 if lim_inf else -10
            x_max = float(b.evalf()) + 2 if lim_sup else 10
            x_vals = np.linspace(x_min, x_max, 400)
            ax.plot(x_vals, f_num(x_vals), label=f"f(x)")
            ax.axhline(0, color='black', linewidth=1)
            ax.axvline(0, color='black', linewidth=1)
            ax.fill_between(x_vals, f_num(x_vals), alpha=0.2)
            ax.grid(True, linestyle=':')
            st.pyplot(fig)

            # Preparazione download Word
            file_word = crea_documento_word(tipo_integrale, testo_equazione, passaggi_word, fig)
            st.download_button(
                label="⬇️ Scarica Risoluzione (Word)",
                data=file_word,
                file_name="integrali.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"Errore nella formula: {e}. Controlla di aver usato correttamente la 'x'.")
    else:
        st.warning("Inserisci una funzione per iniziare.")

# streamlit run integrali.py
# per avviare il programma dal terminale nella stessa cartella