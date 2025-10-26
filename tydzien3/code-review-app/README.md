# Code Review Agent

Aplikacja do automatycznego przeglądu kodu źródłowego zgodna ze specyfikacją CodeReview Agent.

## Funkcjonalności

- ✅ Przegląd kodu w różnych językach programowania
- ✅ Elastyczne skale oceny (procentowa, 1-10, szkolna, itp.)
- ✅ Strukturyzowane wyniki z użyciem Pydantic
- ✅ Identyfikacja problemów z poziomami ważności
- ✅ Propozycje poprawionego kodu
- ✅ Zgodność ze specyfikacją AGENTS.md

## Instalacja

1. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```

2. Skopiuj `env_example.txt` jako `.env` i uzupełnij swój klucz OpenAI API

3. Edytuj plik `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Użycie

### Tryb interaktywny

```bash
python code_review_app.py
```

Program poprosi Cię o:
1. **Wybór języka programowania** (Python, JavaScript, Java, Go, C++, C# lub własny)
2. **Wybór skali oceny** (procentowa, 1-10, szkolna, A-F)
3. **Wybór źródła kodu**:
   - Wprowadzenie kodu ręcznie (możesz wkleić kod z kilku linii)
   - Wczytanie kodu z pliku (podaj ścieżkę do pliku)

Po przeglądzie możesz wybrać czy chcesz przeprowadzić kolejny przegląd.

### Tryb wiersza poleceń

```bash
# Podstawowa składnia
python code_review_app.py -l <język> -o <skala> <plik>

# Przykłady użycia
python code_review_app.py -l python -o 1 kod.py          # Python, skala procentowa
python code_review_app.py -l javascript -o 2 app.js        # JavaScript, skala 1-10
python code_review_app.py -l go -o 3 main.go              # Go, skala szkolna
python code_review_app.py -l java -o 4 Main.java         # Java, skala A-F
python code_review_app.py -l c++ -o 1 program.cpp        # C++, skala procentowa
python code_review_app.py -l c# -o 2 Program.cs           # C#, skala 1-10
```

#### Parametry:
- `-l, --language`: Język programowania (`python`, `javascript`, `java`, `go`, `c++`, `c#`)
- `-o, --output-scale`: Skala oceny (`1`=procentowa, `2`=1-10, `3`=szkolna, `4`=A-F)
- `plik`: Ścieżka do pliku z kodem do przeglądu

#### Pomoc i wersja:
```bash
python code_review_app.py --help      # Wyświetl pomoc
python code_review_app.py --version   # Wyświetl wersję
```

#### Przykłady ścieżek do plików:
- Windows: `C:\Users\Użytkownik\Desktop\kod.py`
- Windows (z cudzysłowami): `"C:\Users\Użytkownik\Desktop\kod.py"`
- Linux/Mac: `/home/user/projects/main.py`
- Względna ścieżka: `./examples/sample.py`

### Użycie jako biblioteka

```python
from code_review_app import CodeReviewApp, print_review_result

app = CodeReviewApp()

# Przegląd kodu
result = app.review_code(
    project_code="twój kod tutaj",
    project_language="Python",
    grading_scale="procentowa 0-100%"
)

# Wyświetlenie wyniku
print_review_result(result)
```

## Struktura projektu

```
code-review/
├── code_review_app.py      # Kompletna aplikacja w jednym pliku
├── requirements.txt           # Zależności
├── env_example.txt           # Szablon zmiennych środowiskowych
├── README.md                 # Dokumentacja
└── examples/                 # Przykłady użycia
    ├── prompt_variable_example.py
    ├── reusable_prompt_example.py
    └── structured_response_example.py
```

## Parametry

### project_language
Język programowania do analizy (np. "Python", "JavaScript", "Go", "Java")

### grading_scale
Skala oceny kodu:
- "procentowa 0-100%"
- "skala 1-10"
- "szkolna 1-6"
- "A-F"

### project_code
Kod źródłowy do przeglądu

## Format wyniku

Aplikacja zwraca strukturę `CodeReviewResult` zawierającą:

- `overall_score`: Ocena jakości kodu zgodna ze skalą
- `found_issues`: Lista problemów z typem, ważnością i opisem
- `improved_code`: Propozycja poprawionego kodu

## Kryteria oceny

Agent analizuje kod pod kątem:
1. Poprawności (błędy logiczne, obsługa wyjątków)
2. Czytelności i stylu (konwencje języka, nazewnictwo)
3. Bezpieczeństwa (walidacja wejść, podatności)
4. Wydajności (złożoność, struktury danych)
5. Testowalności (separacja odpowiedzialności)
6. Architektury (modularność, SRP, skalowalność)
7. Zgodności ze standardami języka

## Przykład użycia

```python
# Przykładowy kod do przeglądu
code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
'''

# Przegląd
app = CodeReviewApp()
result = app.review_code(code, "Python", "procentowa 0-100%")
print_review_result(result)
```

## Wymagania

- Python 3.8+
- OpenAI API Key
- Połączenie z internetem
