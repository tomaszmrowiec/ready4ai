# 📝 Meeting Notes Wizard

Aplikacja do automatycznego strukturyzowania chaotycznych notatek ze spotkań przy użyciu AI.

## ✨ Funkcje

- **Automatyczne strukturyzowanie** - przekształć chaotyczne notatki w profesjonalny raport
- **Format Markdown** - czytelne sekcje z informacjami podstawowymi, decyzjami, action points
- **Inteligentna walidacja** - sprawdza poprawność klucza API i długość notatek
- **Obsługa błędów** - komunikaty w języku polskim
- **Przykład notatek** - gotowy szablon do testowania

## 🚀 Jak uruchomić?

### 1. Przygotowanie środowiska

```bash
# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Konfiguracja API

Utwórz plik `.env` w katalogu projektu:
```
OPENAI_API_KEY=sk-proj-twój-klucz-tutaj
```

### 3. Uruchomienie aplikacji

```bash
streamlit run app.py --server.port=8508
```

Aplikacja otworzy się automatycznie w przeglądarce na: `http://localhost:8508`

## 🛠️ Stack technologiczny

- **Python 3.10+**
- **Streamlit** - interfejs użytkownika
- **OpenAI Responses API** - model `gpt-4.1-mini`
- **python-dotenv** - zarządzanie zmiennymi środowiskowymi


## 📋 Format raportu

Aplikacja generuje raporty w następującym formacie:

1. **Informacje podstawowe** - data, uczestnicy, typ spotkania
2. **Podsumowanie** - 2-3 zdania o spotkaniu
3. **Kluczowe decyzje** - lista najważniejszych ustaleń
4. **Action Points** - tabela z zadaniami, osobami, terminami i priorytetami
5. **Problemy i blokery** - lista przeszkód
6. **Następne kroki** - co dalej

## 🔧 Rozwiązywanie problemów

- **Błąd uwierzytelniania** - sprawdź klucz API w pliku `.env`
- **Port zajęty** - użyj innego portu z parametrem `--server.port`
- **Brak połączenia** - sprawdź połączenie internetowe

## 📄 Licencja

MIT