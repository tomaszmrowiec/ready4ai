# 🤖 AGENTS.MD – Instrukcje dla AI w Cursor

## 📌 O projekcie

**Meeting Notes Wizard** – aplikacja do automatycznego strukturyzowania chaotycznych notatek ze spotkań przy użyciu AI.

**Cel:** Aplikacja Streamlit, która przyjmuje chaotyczne notatki i zwraca profesjonalny raport w formacie Markdown.

---

## 🏗️ Architektura techniczna

### Stack
- **Frontend:** Streamlit (Python)
- **AI:** OpenAI **Responses API** (model gpt-4.1-mini)
- **Środowisko:** Python 3.10+
- **Deployment:** Lokalnie

### Struktura plików
```
meeting-notes-wizard/
├── .env                    # Klucz API (NIE commitować!)
├── .gitignore              # Ignoruj venv, .env, __pycache__
├── requirements.txt        # streamlit, openai, python-dotenv
├── app.py                  # CAŁA aplikacja w 1 pliku
├── README.md               # Instrukcje uruchomienia
└── AGENTS.md               # Ten plik - instrukcje dla AI
```

---

## 🤖 Instrukcje dla Cursor AI

### Zasady kodowania
1. **Prosty kod**
   - Wszystko w jednym pliku `app.py`
   - Czytelne nazwy zmiennych (EN), komentarze w kodzie (EN), teksty UI (PL)
2. **Streamlit**
   - Standardowe komponenty
   - Wyniki w Markdown
   - Spinner w trakcie wywołania API
   - Przyjazne komunikaty o sukcesie/błędach
3. **OpenAI API (AKTUALNE – 2025)**
   - **Używaj Responses API** zamiast starego `Chat Completions`
   - Dla `gpt-4.1-mini` **nie ustawiaj** `temperature` (domyślne próbkowanie)
   - Biblioteka: `openai>=1.0.0`
   - Klucz z `.env` przez `python-dotenv`
   - Obsługa wyjątków specyficznych dla biblioteki
4. **Error handling**
   - `try/except` dla każdego wywołania
   - Komunikaty dla użytkownika po polsku

---

## 📊 MODELE (praktyczne zalecenia do tego MVP)

**Używany w aplikacji:** `gpt-4.1-mini` – szybki i opłacalny do porządkowania tekstu

> **Ważne:** **nie ustawiaj** `temperature` ani `top_p` dla żadnego modelu. Stosuj domyślne próbkowanie – część modeli ignoruje te parametry lub zwraca błąd.

---

## 💻 AKTUALNA SKŁADNIA – **Responses API** (nowy standard)

### ✅ Parametry w **Responses API** (bezpieczne, aktualne)
- `model`: np. `gpt-4.1-mini`
- `input`: lista wiadomości `{role, content}` albo `input="..."`
- `max_output_tokens`: limit tokenów odpowiedzi
- **Nie podawaj:** `temperature`, `top_p`, `logprobs` (często ignorowane lub 400)

**Inicjalizacja klienta**
```python
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**Wywołanie (strukturyzowanie notatek)**  
> W Responses API możesz przesłać stan rozmowy jako listę obiektów `{role, content}` podobnie jak wcześniej.

**Dostęp do metadanych odpowiedzi**
```python
# Pełne obiekty są dostępne w resp.output[...], resp.usage itp.
# Szybki dostęp do plain text: resp.output_text
```

**Uwaga dot. Chat Completions**  
Stara składnia nie jest zalecana dla nowych projektów. Responses API to nowy standard, który upraszcza interfejs i łączy możliwości wcześniejszych API.

---

## 📝 Wymagany format raportu (system prompt)

### Sekcje raportu (zawsze)
1. **Informacje podstawowe:** Data, uczestnicy, typ spotkania
2. **Podsumowanie:** 2–3 zdania o czym było spotkanie
3. **Kluczowe decyzje:** Lista najważniejszych ustaleń
4. **Action Points:** Tabela Markdown z kolumnami (Osoba | Zadanie | Deadline | Priorytet 🔴/🟡/🟢)
5. **Problemy i blokery:** Lista
6. **Następne kroki:** Co dalej / kiedy kolejne spotkanie

### Zasady
- Braki → „Nie podano"
- Daty → **DD.MM.RRRR**
- Język = język notatek (PL/EN)
- Markdown + emoji
- Zero halucynacji – tylko fakty z notatek

---

## 🐛 Typowe problemy i rozwiązania

**1) ModuleNotFoundError** – zainstaluj zależności: `pip install -r requirements.txt`  
**2) Brak klucza API** – `.env` z `OPENAI_API_KEY=sk-...`; wywołaj `load_dotenv()`  
**3) Stara składnia** – używasz `chat.completions.create` bez potrzeby; przejdź na **Responses**  
**4) Rate limit (429)** – zaimplementuj backoff (1s, 2s, 4s, 8s…)  
**5) Model not found** – sprawdź dokładną nazwę modelu na koncie  
**6) Timeout / sieć** – pokaż komunikat i zasugeruj ponowienie

---

## 📦 requirements.txt (propozycja)

```
streamlit>=1.36.0
openai>=1.0.0
python-dotenv>=1.0.1
```

---

## ✅ Zasady dla Cursor AI

### Kodowanie
- Używaj **Responses API** (nie Chat Completions)
- Model: `gpt-4.1-mini`
- **Nie** ustawiaj `temperature`/`top_p`
- Klucz z `.env` przez `python-dotenv`
- System prompt jako stała
- Walidacja min. 50 znaków
- Spinner podczas żądania
- Przyjazne komunikaty o błędach (ASCII)
- Komentarze w kodzie (EN), UI (PL)

### Struktura
- Wszystko w jednym pliku `app.py`
- Stałe konfiguracyjne na górze
- Prosta obsługa błędów
- Walidacja klucza API
- Normalizacja Markdown
- Raport w Markdown z 6 sekcjami
