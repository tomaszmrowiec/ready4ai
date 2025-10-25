import streamlit as st
import os
import json
import time
from openai import OpenAI
from openai import APIConnectionError, RateLimitError, AuthenticationError, APIStatusError
from dotenv import load_dotenv

# Configuration constants
MODEL_NAME = "gpt-4.1-mini"
MAX_TOKENS_PRIMARY = 800
MAX_TOKENS_FALLBACK = 1000
MAX_RETRY_ATTEMPTS = 3
MIN_NOTES_LENGTH = 50

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Jesteś ekspertem od strukturyzowania notatek ze spotkań.
Zwracaj wynik WYLACZNIE jako Markdown z naglowkami '##' i DOKLADNYM ukladem jak ponizej.

ZASADY:
- Jezyk = jezyk wejsciowy (PL/EN)
- Braki → 'Nie podano'
- Daty = DD.MM.RRRR
- Priorytety: Wysoki/Średni/Niski (lub 🔴/🟡/🟢)
- Zero halucynacji – tylko fakty z notatek
- Nie pokazuj procesu rozumowania; tylko finalny raport
- Zwiezlosc: maks. ~600 tokenow

SZABLON:
## Informacje podstawowe
- Data: ...
- Uczestnicy: ...
- Typ spotkania: ...

## Podsumowanie
... (2-3 zdania)

## Kluczowe decyzje
- ...
- ...

## Action Points
| Osoba | Zadanie | Deadline | Priorytet |
|-------|---------|----------|----------|
| ... | ... | ... | ... |
| ... | ... | ... | ... |

## Problemy i blokery
- ...
- ...

## Następne kroki
- ...
- ..."""

EXAMPLE_NOTES = """Spotkanie z zespołem - 25.10.2025
Jan, Anna, Piotr, Kasia
Dyskusja o nowym projekcie
- trzeba zrobic research rynku
- deadline na koniec miesiaca
- problem z budzetem - za malo kasy
- Anna ma sprawdzic konkurencje
- Piotr zrobi prototyp
- Kasia przygotuje prezentacje
- nastepne spotkanie za tydzien
- blokery: brak dostepu do danych"""

def validate_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        return "Brak klucza API. Dodaj OPENAI_API_KEY do pliku .env"
    return None

def extract_text_from_response(response):
    """Extract text content from OpenAI response object."""
    # Try direct access first
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text
    
    # Simple fallback - return empty string if no text found
    return ""

def normalize_markdown(md):
    """Ensure proper Markdown formatting for report sections."""
    if not isinstance(md, str) or not md:
        return md
    
    sections = ["Informacje podstawowe", "Podsumowanie", "Kluczowe decyzje", 
                "Action Points", "Problemy i blokery", "Następne kroki"]
    
    lines = md.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped in sections and not stripped.startswith("## "):
            out.append(f"## {stripped}")
        else:
            out.append(line)
    return "\n".join(out)

def make_api_request(notes_text):
    """Make API request to OpenAI with simple error handling."""
    key_error = validate_api_key()
    if key_error:
        return None, key_error

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": notes_text}
            ],
            max_output_tokens=MAX_TOKENS_PRIMARY
        )
        text = extract_text_from_response(response)
        
        if not text or not str(text).strip():
            return None, "Model nie zwrocil tresci. Sprobuj ponownie."

        return normalize_markdown(text), None

    except Exception as e:
        return None, f"Blad API: {str(e)}"

def structure_notes(notes_text):
    """Validate input and structure notes using AI."""
    if not notes_text or len(notes_text.strip()) < MIN_NOTES_LENGTH:
        return None, f"Wprowadź przynajmniej {MIN_NOTES_LENGTH} znaków notatek."
    return make_api_request(notes_text)

st.set_page_config(
    page_title="Meeting Notes Wizard",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Meeting Notes Wizard")
st.markdown("**Automatycznie strukturyzuj swoje chaotyczne notatki ze spotkań**")

if 'notes_input' not in st.session_state:
    st.session_state.notes_input = ""

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔧 Wstaw przykład", type="secondary"):
        st.session_state.notes_input = EXAMPLE_NOTES
        st.rerun()

with col2:
    structure_button = st.button("✨ Strukturyzuj notatki", type="primary")

notes_input = st.text_area(
    "Wklej tutaj swoje notatki ze spotkania:",
    height=200,
    placeholder=f"Wprowadź swoje chaotyczne notatki ze spotkania... (minimum {MIN_NOTES_LENGTH} znaków)",
    key="notes_input"
)

if structure_button:
    current_notes = st.session_state.get('notes_input', '')
    
    if not current_notes or len(current_notes.strip()) < MIN_NOTES_LENGTH:
        st.error(f"Wprowadź przynajmniej {MIN_NOTES_LENGTH} znaków notatek.")
    else:
        with st.spinner("Strukturyzuję notatki..."):
            result, error = structure_notes(current_notes)
            
            if error:
                st.error(error)
            else:
                if not result or not str(result).strip():
                    st.warning("Model nie zwrócił treści. Spróbuj ponownie.")
                else:
                    st.success("Notatki zostały pomyślnie strukturyzowane!")
                    st.markdown("---")
                    st.markdown(result)

st.markdown("---")
st.markdown("*Meeting Notes Wizard - Automatyczne strukturyzowanie notatek ze spotkań*")