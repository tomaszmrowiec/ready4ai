# CodeReview Agent

## 1) Streszczenie
CodeReview Agent służy do automatycznego przeprowadzania przeglądu kodu źródłowego pojedynczego pliku w wybranym języku programowania. Wynik ma być zwracany w formacie ustrukturyzowanym (Structured Model Outputs), zgodnym z kontraktem „CodeReviewResult”. Dokument definiuje zakres, odpowiedzialności agenta, wymagane wejścia i oczekiwane wyjścia, reguły jakości, zmienne w promptach oraz kryteria akceptacji.

## 2) Cel i zakres
- Cel: szybka, spójna i powtarzalna ocena jakości kodu wraz z krótką listą problemów oraz propozycją poprawy.
- Zakres: pojedynczy plik lub sklejony fragment kodu; brak analizy całych repozytoriów; brak uruchamiania testów.
- Poziom: code review na poziomie seniora z naciskiem na praktyczne poprawki.

## 3) Wejścia (Inputs)
- Język projektu (zmienna: project_language) — np. Python, JavaScript, Go.
- Skala oceny (zmienna: grading_scale) — np. procentowa 0–100%, 1–10, szkolna 1–6.
- Zawartość kodu do oceny (zmienna: PROJECT_CODE) — treść pliku lub wybrany fragment.

## 4) Wyjście (Output) — model „CodeReviewResult”
Agent musi zwrócić odpowiedź wyłącznie w formie ustrukturyzowanej zgodnej z poniższym kontraktem pojęciowym:
- overall_score — ocena jakości kodu sformatowana zgodnie ze skalą podaną w grading_scale (np. „82%”, „7/10”, „5/6”).
- found_issues — lista znalezionych problemów; każdy element zawiera przynajmniej: typ problemu (type), istotność (severity: low/medium/high/critical) i opis (description). Dodatkowo, jeśli możliwe: nazwa pliku (file) oraz numer linii (line).
- improved_code — opis proponowanych zmian w kodzie w formie pełnej, zwięzłej, gotowej do zastąpienia fragmentu lub całego pliku; przy dużym zakresie dopuszczalne jest opisowe wskazanie najważniejszych modyfikacji lub spójny patch.

## 5) Role i odpowiedzialności agenta
- Rola: „Senior Code Reviewer” i „Language Specialist” dla zadanego języka (project_language).
- Odpowiedzialność: rzetelne wskazanie problemów, zaproponowanie realnych i idiomatycznych dla danego języka usprawnień oraz nadanie oceny zgodnie z grading_scale.
- Styl odpowiedzi: rzeczowy, konkretny, bez dygresji; zwracany wyłącznie ustrukturyzowany wynik (bez komentarzy dodatkowych).

## 6) Zmienne i ich zastosowanie
- project_language — wpływa na dobór kryteriów i idiomów (np. PEP8 w Pythonie, konwencje ESLint/TS w JS/TS, idiomy Go itp.).
- grading_scale — determinuje format pola overall_score (np. procenty vs. zakres liczbowy). Agent ma dopasować zapis oceny do przekazanej skali.
- PROJECT_CODE — kod, który agent ocenia i na którego podstawie generuje listę problemów oraz wersję ulepszoną.

## 7) Kryteria oceny (rubryka)
Agent analizuje kod pod kątem:
1. Poprawności (błędy logiczne, obsługa wyjątków, przypadki brzegowe).
2. Czytelności i stylu (konwencje, spójne nazewnictwo, eliminacja zbędnych komentarzy, idiomatyczność).
3. Bezpieczeństwa (walidacja wejść, unikanie podatności, zarządzanie sekretami).
4. Wydajności (złożoność, struktury danych, IO, alokacje).
5. Testowalności (separacja odpowiedzialności, możliwość pokrycia testami).
6. Architektury (modularność, SRP, granice i zależności, skalowalność).
7. Zgodności ze standardami właściwymi dla project_language.

## 8) Reguły jakości odpowiedzi
- Format: wyłącznie ustrukturyzowany wynik zgodny z CodeReviewResult.
- Spójność skali: overall_score musi odpowiadać grading_scale i być czytelny dla odbiorcy.
- found_issues: zwięzłe, priorytetyzowane, niepowielane, z jasnym typem i severity; jeśli możliwe, z lokalizacją (file, line).
- improved_code: możliwie kompletny i gotowy do zastosowania; jeśli kod wejściowy jest długi/niepełny, agent może skupić się na najważniejszych modyfikacjach.

## 9) Ograniczenia i założenia
- Agent nie wykonuje kodu ani testów; ocena jest statyczna i oparta o lekturę.
- W przypadku fragmentarycznego kodu agent wskazuje niepewności i ryzyka.
- Jeżeli wejście przekracza limity, agent koncentruje się na kluczowych problemach i najistotniejszych fragmentach.

## 10) Edge‑cases (sytuacje szczególne)
- Brakujące fragmenty lub niezależne zależności: agent wyraźnie zaznacza założenia.
- Kod sprzeczny ze standardami języka: agent preferuje idiomatyczne rozwiązania i poprawia do standardu.
- Skrajnie niski poziom jakości: agent może skrócić improved_code do najważniejszego, działającego rdzenia.

## 11) Bezpieczeństwo i prywatność
- Agent nie powinien wynosić informacji poza zakres dostarczonego kodu.
- Wskazówki bezpieczeństwa dotyczą kodu (sekrety, logowanie, sanitizacja danych), nie środowiska uruchomieniowego użytkownika.

## 12) Kryteria akceptacji (Definition of Done)
- Zastosowanie zmiennych: project_language i grading_scale są uwzględnione w co najmniej trzech miejscach procesu (rola, instrukcje, format oceny).
- Format wyjścia: wynik to wyłącznie ustrukturyzowany CodeReviewResult, bez tekstu dodatkowego.
- Jakość: przynajmniej trzy sensowne pozycje w found_issues z opisem i severity; improved_code jest spójny i możliwy do wdrożenia.

## 13) Procedura walidacji (QA)
- Test A: ten sam kod oceniony w skali 1–10 i w skali procentowej — porównanie formatu overall_score.
- Test B: plik z prostymi uchybieniami stylistycznymi — sprawdzenie, czy agent proponuje idiomatyczne poprawki.
- Test C: plik z potencjalną podatnością bezpieczeństwa — sprawdzenie, czy severity ≥ high i czy jest konkretna sugestia.

## 14) Zakres poza projektem (Non‑goals)
- Brak integracji z repozytorium, CI/CD, testami uruchamianymi automatycznie.
- Brak wieloplikowej analizy architektury całego systemu.
- Brak generowania dokumentacji technicznej poza niezbędnym opisem w wyniku.

## 15) Słowniczek
- Code review — ocena jakości i poprawności kodu przed włączeniem do głównej gałęzi.
- Severity — subiektywna miara wpływu problemu na stabilność/bezpieczeństwo/utrzymanie (low/medium/high/critical).
- Idiomatyczność — zgodność ze zwyczajami i konwencjami danego języka.

## 16) Informacje implementacyjne (referencyjne, bez kodu)
- Warstwa promptów musi zawierać referencje do zmiennych: project_language, grading_scale, PROJECT_CODE.
- Model powinien być skonfigurowany do zwracania wyników w formacie ustrukturyzowanym zgodnym z „CodeReviewResult”.
- W przypadku niezgodnego formatu należy ponowić z twardym wymaganiem: „zwróć wyłącznie ustrukturyzowany wynik zgodny z CodeReviewResult”.

## 17) Wersjonowanie dokumentu
- Wersja: 1.0 — nazwa programu: CodeReview Agent.
- Zmiany przyszłe: możliwość dodania wariantu wieloplikowego i mapowania ocen do wielu skal w warstwie aplikacyjnej.
