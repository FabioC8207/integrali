# pip install streamlit sympy matplotlib pytesseract pillow python-docx numpy
import streamlit as st
from sympy import symbols, integrate, latex, lambdify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pytesseract
from docx import Document
from docx.shared import Inches
import io

# Configurazione della pagina
st.set_page_config(page_title="Risolutore Integrali Pro", layout="centered")

# --- LOGICA DI PARSING AVANZATA ---
# Questa funzione permette di capire "2x" come "2*x"
transformations = (standard_transformations + (implicit_multiplication_application,))

def crea_documento_word(tipo, espressione, passaggi, fig):
    doc = Document()
    doc.add_heading(f'Risoluzione Integrale {tipo}', 0)
    doc.add_heading('Esercizio:', level=1)
    doc.add_paragraph(f"Funzione: {espressione}")
    doc.add_heading('Svolgimento:', level=1)
    for p in passaggi:
        doc.add_paragraph(p)
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)
    doc.add_picture(img_stream, width=Inches(4.5))
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

st.title("🧮 Risolutore Integrali Intelligente")
st.info("💡 Ora puoi scrivere anche '2x', '3sin(x)' o 'x^2' senza preoccuparti dei simboli di moltiplicazione!")

# --- GESTIONE INPUT SEMPLIFICATO ---
if "input_math" not in st.session_state:
    st.session_state.input_math = ""

# Layout Pulsanti in una griglia ordinata
st.subheader("Inserimento rapido")
cols = st.columns(7)
tasti = [
    ("√", "sqrt("), ("^", "**"), ("/", "/"), 
    ("sin", "sin("), ("cos", "cos("), ("ln", "log("), ("x", "x")
]

for i, (label, valore) in enumerate(tasti):
    if cols[i].button(label):
        st.session_state.input_math += valore

# Campo di testo che si aggiorna con i pulsanti
testo_equazione = st.text_input("Modifica o scrivi la funzione f(x):", value=st.session_state.input_math)

# Opzione per resettare il campo
if st.button("Cancella tutto"):
    st.session_state.input_math = ""
    st.rerun()

# Caricamento Immagine
with st.expander("📷 Carica foto esercizio"):
    foto_upload = st.file_uploader("Trascina qui l'immagine", type=["jpg", "jpeg", "png"])
    if foto_upload:
        immagine = Image.open(foto_upload)
        if st.button("Estrai testo"):
            # L'OCR a volte sbaglia, lo puliamo un po'
            testo_estratto = pytesseract.image_to_string(immagine).strip().lower()
            st.session_state.input_math = testo_estratto
            st.rerun()

# Limiti
st.subheader("Parametri integrazione")
c1, c2 = st.columns(2)
lim_inf = c1.text_input("Limite Inferiore (a)")
lim_sup = c2.text_input("Limite Superiore (b)")

# --- CALCOLO ---
if st.button("RISOLVI ORA", type="primary"):
    if testo_equazione:
        try:
            x = symbols('x')
            # Applichiamo il parsing intelligente per accettare 2x, x(x+1), ecc.
            f = parse_expr(testo_equazione, transformations=transformations)
            
            passaggi_word = []
            
            if not lim_inf and not lim_sup:
                risultato = integrate(f, x)
                st.latex(rf"\int {latex(f)} \, dx = {latex(risultato)} + C")
                passaggi_word = [f"Funzione: {f}", f"Integrale Indefinito: {risultato} + C"]
                tipo_integrale = "Indefinito"
            else:
                a = parse_expr(lim_inf, transformations=transformations)
                b = parse_expr(lim_sup, transformations=transformations)
                primitiva = integrate(f, x)
                risultato = integrate(f, (x, a, b))
                st.latex(rf"\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(f)} \, dx = {latex(risultato)}")
                passaggi_word = [f"Funzione: {f}", f"Primitiva: {primitiva}", f"Valutato tra {a} e {b}", f"Risultato: {risultato}"]
                tipo_integrale = "Definito"

            # Grafico
            fig, ax = plt.subplots()
            f_num = lambdify(x, f, "numpy")
            x_min = float(a.evalf()) - 2 if lim_inf else -5
            x_max = float(b.evalf()) + 2 if lim_sup else 5
            x_v = np.linspace(x_min, x_max, 400)
            ax.plot(x_v, f_num(x_v))
            ax.axhline(0, color='black', lw=1)
            ax.grid(True, linestyle=':')
            if lim_inf and lim_sup:
                # Coloriamo l'area dell'integrale definito
                x_area = np.linspace(float(a.evalf()), float(b.evalf()), 200)
                ax.fill_between(x_area, f_num(x_area), alpha=0.3, color='orange')
            st.pyplot(fig)

            # Download
            file_word = crea_documento_word(tipo_integrale, str(f), passaggi_word, fig)
            st.download_button("⬇️ Scarica Risoluzione (Word)", file_word, "integrali.docx")

        except Exception as e:
            st.error(f"Errore: {e}. Prova a scrivere la formula in modo più esplicito.")

# streamlit run integrali.py
# per avviare il programma dal terminale nella stessa cartella
