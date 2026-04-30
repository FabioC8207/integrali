# pip install streamlit sympy matplotlib pytesseract pillow python-docx numpy
# streamlit run integrali.py
# per avviare il programma dal terminale nella stessa cartella


import streamlit as st
from sympy import symbols, integrate, latex, lambdify, sympify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from docx.shared import Inches, Pt
from fpdf import FPDF
import io

# Configurazione Pagina
st.set_page_config(page_title="Risolutore Integrali Pro LaTeX", layout="centered")

# --- LOGICA DI TRASFORMAZIONE ---
transformations = (standard_transformations + (implicit_multiplication_application,))

def pulisci_input(testo):
    return testo.replace('^', '**')

def ottieni_suggerimento(f):
    f_str = str(f).lower()
    if 'log' in f_str or 'exp' in f_str:
        return "Strategia: Integrazione per parti o sostituzione logaritmica."
    if '/' in f_str:
        return "Strategia: Scomposizione in fratti semplici o ricerca della derivata del denominatore."
    if 'sin' in f_str or 'cos' in f_str:
        return "Strategia: Sostituzione di variabili o formule di duplicazione/bisezione."
    return "Strategia: Integrazione immediata tramite regole fondamentali."

# --- FUNZIONI DI ESPORTAZIONE ---

def crea_word(tipo, f, res, steps, fig):
    doc = Document()
    # Stile Titolo
    title = doc.add_heading(f'Risoluzione Integrale {tipo}', 0)
    
    # Sezione Testo
    doc.add_heading('Esercizio', level=1)
    p = doc.add_paragraph()
    p.add_run(f"Data la funzione f(x) = ").bold = True
    p.add_run(f"{f}, calcolarne l'integrale.")

    # Sezione Passaggi
    doc.add_heading('Svolgimento', level=1)
    for s in steps:
        doc.add_paragraph(s, style='List Bullet')

    # Risultato in grassetto
    res_p = doc.add_paragraph()
    res_p.add_run("Il risultato finale è: ").bold = True
    res_p.add_run(str(res))

    # Grafico
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    doc.add_picture(img_stream, width=Inches(4.5))
    
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# --- INTERFACCIA STREAMLIT ---
st.title("🧮 LaTeX Integral Solver")

if "input_math" not in st.session_state:
    st.session_state.input_math = ""

# Pulsanti di inserimento
st.subheader("Pannello di Inserimento")
btns = st.columns(8)
tasti = [("x", "x"), ("^", "^"), ("√", "sqrt("), ("/", "/"), ("sin", "sin("), ("cos", "cos("), ("ln", "log("), ("(", "(")]

for i, (lab, val) in enumerate(tasti):
    if btns[i].button(lab):
        st.session_state.input_math += val

testo_equazione = st.text_input("Inserisci la funzione f(x):", value=st.session_state.input_math)

if st.button("🗑️ Cancella tutto", type="secondary"):
    st.session_state.input_math = ""
    st.rerun()

c1, c2 = st.columns(2)
a_in = c1.text_input("Limite inferiore (a)")
b_in = c2.text_input("Limite superiore (b)")

# --- CALCOLO E OUTPUT ---
if st.button("CALCOLA E GENERA REPORT", type="primary"):
    if testo_equazione:
        try:
            x = symbols('x')
            f_puro = pulisci_input(testo_equazione)
            f = parse_expr(f_puro, transformations=transformations)
            
            # Calcolo Matematico
            if not a_in and not b_in:
                tipo = "Indefinito"
                res = integrate(f, x)
                stringa_latex = rf"\int {latex(f)} \, dx = {latex(res)} + C"
                steps = [f"Identificazione della funzione: {f}", "Applicazione della primitiva generale."]
                res_final = f"{res} + C"
            else:
                tipo = "Definito"
                a = sympify(pulisci_input(a_in))
                b = sympify(pulisci_input(b_in))
                primitiva = integrate(f, x)
                res = integrate(f, (x, a, b))
                stringa_latex = rf"\int_{{{latex(a)}}}^{{{latex(b)}}} {latex(f)} \, dx = {latex(res)}"
                steps = [
                    f"Funzione integranda: {f}",
                    f"Calcolo della primitiva: F(x) = {primitiva}",
                    f"Applicazione degli estremi: F({b}) - F({a})"
                ]
                res_final = str(res)

            # --- VISUALIZZAZIONE ---
            st.subheader("Risultato in LaTeX")
            st.latex(stringa_latex)
            
            with st.expander("Copia Codice LaTeX"):
                st.code(stringa_latex, language='latex')

            st.success(ottieni_suggerimento(f))

            # Grafico
            fig, ax = plt.subplots()
            f_n = lambdify(x, f, "numpy")
            x_vals = np.linspace(-10, 10, 400)
            ax.plot(x_vals, f_n(x_vals), label='f(x)')
            ax.axhline(0, color='black', lw=0.5)
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

            # Export
            word_file = crea_word(tipo, f, res_final, steps, fig)
            st.download_button("⬇️ Scarica Documento Word", word_file, "risoluzione_integrale.docx")

        except Exception as e:
            st.error(f"Errore nel parsing: {e}")
