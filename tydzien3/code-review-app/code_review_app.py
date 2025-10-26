import os
import sys
import argparse
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from enum import Enum


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CodeIssue(BaseModel):
    type: str
    severity: SeverityLevel
    description: str
    file: Optional[str] = None
    line: Optional[int] = None


class CodeReviewResult(BaseModel):
    overall_score: str
    found_issues: List[CodeIssue]
    improved_code: str


class Config:
    MAX_CODE_LENGTH: int = 500000
    LANGUAGE_MAP: Dict[str, str] = {
        "1": "Python", "2": "JavaScript", "3": "Java",
        "4": "Go", "5": "C++", "6": "C#"
    }
    SCALE_MAP: Dict[str, str] = {
        "1": "procentowa 0-100%", "2": "skala 1-10",
        "3": "szkolna 1-6", "4": "A-F"
    }


# Global logger instance to avoid multiple initialization
_logger = None

def setup_logging() -> logging.Logger:
    """Inicjalizuje logger tylko raz, aby uniknąć redundancji."""
    global _logger
    
    if _logger is None:
        log_filename = f"code_review_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Sprawdź czy logging już został skonfigurowany
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_filename, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        
        _logger = logging.getLogger(__name__)
    
    return _logger


class CodeReviewer:
    def __init__(self, client: OpenAI) -> None:
        self.client: OpenAI = client
        self.logger: logging.Logger = setup_logging()
    
    def review_code(self, project_code: str, project_language: str, 
                   grading_scale: str) -> CodeReviewResult:
        self.logger.info(f"Rozpoczynanie przeglądu kodu - język: {project_language}")
        
        if len(project_code) > Config.MAX_CODE_LENGTH:
            return self._create_length_error_result(len(project_code))
        
        prompt = self._build_prompt(project_code, project_language, grading_scale)
        
        try:
            response = self.client.responses.parse(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": prompt}],
                text_format=CodeReviewResult
            )
            
            return self._validate_response(response)
            
        except Exception as e:
            self.logger.error(f"Błąd podczas przeglądu kodu: {e}")
            return self._create_error_result()
    
    def _create_length_error_result(self, code_length: int) -> CodeReviewResult:
        return CodeReviewResult(
            overall_score="0%",
            found_issues=[CodeIssue(
                type="Przekroczenie limitu długości",
                severity=SeverityLevel.HIGH,
                description=f"Kod jest za długi ({code_length} znaków)"
            )],
            improved_code="Skróć kod lub podziel go na mniejsze fragmenty."
        )
    
    def _build_prompt(self, project_code: str, project_language: str, 
                     grading_scale: str) -> str:
        return f"""
<instruction>
Jesteś Senior Code Reviewer i Language Specialist dla języka {project_language}.
Twoim zadaniem jest przeprowadzenie przeglądu kodu źródłowego zgodnie z najwyższymi standardami jakości.

ZADANIA:
1. Przeanalizuj kod pod kątem poprawności, czytelności, bezpieczeństwa, wydajności, testowalności i architektury
2. Zidentyfikuj problemy i przypisz im odpowiedni poziom ważności (low/medium/high/critical)
3. Zaproponuj konkretne poprawki w kodzie
4. Nadaj ocenę jakości kodu zgodnie ze skalą: {grading_scale}

WYMAGANIA FORMATU ODPOWIEDZI:
- Zwróć WYŁĄCZNIE ustrukturyzowany wynik zgodny z CodeReviewResult
- overall_score: ocena sformatowana zgodnie ze skalą {grading_scale}
- found_issues: lista problemów z typem, ważnością i opisem
- improved_code: kompletny, poprawiony kod gotowy do zastosowania
</instruction>

<code_to_review>
{project_code}
</code_to_review>

<grading_scale_info>
Skala oceny: {grading_scale}
</grading_scale_info>

<language_standards>
Język: {project_language}
Zastosuj standardy i konwencje właściwe dla tego języka programowania.
</language_standards>
"""
    
    def _validate_response(self, response: Any) -> CodeReviewResult:
        if not hasattr(response, 'output_parsed') or response.output_parsed is None:
            raise ValueError("Odpowiedź z API ma nieprawidłowy format")
        
        parsed_result = response.output_parsed
        if not isinstance(parsed_result, CodeReviewResult):
            raise ValueError("Odpowiedź nie jest instancją CodeReviewResult")
        
        required_fields = ['overall_score', 'found_issues', 'improved_code']
        for field in required_fields:
            if not hasattr(parsed_result, field) or not getattr(parsed_result, field):
                raise ValueError(f"Brak wymaganego pola '{field}' w odpowiedzi")
        
        return parsed_result
    
    def _create_error_result(self) -> CodeReviewResult:
        return CodeReviewResult(
            overall_score="0%",
            found_issues=[],
            improved_code="Błąd podczas przeglądu kodu"
        )


class CodeReviewApp:
    def __init__(self) -> None:
        self.logger: logging.Logger = setup_logging()
        self.logger.info("Inicjalizacja CodeReviewApp")
        
        load_dotenv()
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("Brak klucza OpenAI API w pliku .env")
        
        # Elastyczna walidacja klucza API
        if not self._validate_api_key(api_key):
            raise ValueError(
                "Nieprawidłowy format klucza OpenAI API. "
                "Klucz powinien mieć długość 20-200 znaków i składać się z liter, cyfr i znaków specjalnych. "
                "Sprawdź dokumentację OpenAI dla aktualnego formatu kluczy."
            )
        
        self.client: OpenAI = OpenAI(api_key=api_key)
        self.reviewer: CodeReviewer = CodeReviewer(self.client)
        self.logger.info("CodeReviewApp zainicjalizowany pomyślnie")
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Waliduje klucz API OpenAI.
        
        Args:
            api_key: Klucz API do walidacji
            
        Returns:
            True jeśli klucz jest prawidłowy, False w przeciwnym razie
            
        Note:
            Format kluczy OpenAI może się zmieniać. Ta walidacja sprawdza podstawowe
            wymagania: długość i obecność znaków alfanumerycznych.
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Usuń białe znaki
        api_key = api_key.strip()
        
        # Sprawdź długość (klucze OpenAI są zwykle w zakresie 20-200 znaków)
        if len(api_key) < 20 or len(api_key) > 200:
            self.logger.error(f"Klucz API ma nieprawidłową długość: {len(api_key)} znaków")
            return False
        
        # Sprawdź czy zawiera przynajmniej litery i cyfry
        import re
        if not re.search(r'[a-zA-Z]', api_key) or not re.search(r'[0-9]', api_key):
            self.logger.error("Klucz API musi zawierać zarówno litery jak i cyfry")
            return False
        
        # Sprawdź czy nie zawiera niebezpiecznych znaków (tylko podstawowe)
        if re.search(r'[<>"\'\s]', api_key):
            self.logger.error("Klucz API zawiera niedozwolone znaki")
            return False
        
        # Dodatkowe sprawdzenie - klucze OpenAI zwykle zaczynają się od "sk-"
        # ale nie jest to wymagane, więc tylko ostrzeżenie w logach
        if not api_key.startswith("sk-"):
            self.logger.warning(
                "Klucz API nie zaczyna się od 'sk-'. "
                "Sprawdź czy używasz prawidłowego klucza OpenAI."
            )
        
        return True
    
    def review_code(self, project_code: str, project_language: str, 
                   grading_scale: str) -> CodeReviewResult:
        return self.reviewer.review_code(project_code, project_language, grading_scale)


def safe_input(prompt: str, max_length: int = 1000) -> str:
    """
    Bezpiecznie pobiera dane od użytkownika z ograniczeniami długości i sanitizacją.
    
    Args:
        prompt: Tekst wyświetlany użytkownikowi
        max_length: Maksymalna długość wprowadzonego tekstu
        
    Returns:
        Sanityzowany tekst wprowadzony przez użytkownika
        
    Raises:
        ValueError: Jeśli wprowadzony tekst przekracza maksymalną długość
    """
    try:
        user_input = input(prompt).strip()
        
        # Sprawdź długość
        if len(user_input) > max_length:
            raise ValueError(f"Wprowadzony tekst jest za długi (max {max_length} znaków)")
        
        # Podstawowa sanitizacja - usuń potencjalnie niebezpieczne znaki
        # W kontekście CLI jest to zwykle wystarczające
        sanitized = user_input.replace('\x00', '').replace('\r', '')
        
        return sanitized
        
    except KeyboardInterrupt:
        raise KeyboardInterrupt("Operacja przerwana przez użytkownika")
    except EOFError:
        raise EOFError("Nieoczekiwany koniec danych wejściowych")


class UserInterface:
    @staticmethod
    def get_language_choice() -> str:
        print("📝 Wybierz język programowania:")
        for key, value in Config.LANGUAGE_MAP.items():
            print(f"{key}. {value}")
        print("7. Inny (wpisz ręcznie)")
        
        while True:
            try:
                choice = safe_input("\nWybierz opcję (1-7): ", max_length=10)
                
                if choice in Config.LANGUAGE_MAP:
                    return Config.LANGUAGE_MAP[choice]
                elif choice == "7":
                    language = safe_input("Wpisz język programowania: ", max_length=50)
                    if language:
                        return language
                    print("❌ Język nie może być pusty!")
                else:
                    print("❌ Nieprawidłowy wybór! Wybierz 1-7.")
            except ValueError as e:
                print(f"❌ {e}")
            except (KeyboardInterrupt, EOFError):
                raise
    
    @staticmethod
    def get_scale_choice() -> str:
        print("📊 Wybierz skalę oceny:")
        for key, value in Config.SCALE_MAP.items():
            print(f"{key}. {value}")
        
        while True:
            try:
                choice = safe_input("\nWybierz opcję (1-4): ", max_length=10)
                if choice in Config.SCALE_MAP:
                    return Config.SCALE_MAP[choice]
                print("❌ Nieprawidłowy wybór! Wybierz 1-4.")
            except ValueError as e:
                print(f"❌ {e}")
            except (KeyboardInterrupt, EOFError):
                raise
    
    @staticmethod
    def get_code_input() -> str:
        print("💻 Wybierz źródło kodu do przeglądu:")
        print("1. Wprowadź kod ręcznie")
        print("2. Wczytaj kod z pliku")
        
        while True:
            try:
                choice = safe_input("\nWybierz opcję (1-2): ", max_length=10)
                
                if choice == "1":
                    return UserInterface._get_manual_code()
                elif choice == "2":
                    return UserInterface._get_file_code()
                print("❌ Nieprawidłowy wybór! Wybierz 1 lub 2.")
            except ValueError as e:
                print(f"❌ {e}")
            except (KeyboardInterrupt, EOFError):
                raise
    
    @staticmethod
    def _get_manual_code() -> str:
        print("💻 Wprowadź kod do przeglądu:")
        print("(Możesz wkleić kod z kilku linii. Zakończ wprowadzanie pustą linią)")
        print("-" * 40)
        
        code_lines: List[str] = []
        while True:
            try:
                line: str = safe_input("", max_length=5000)  # Pozwól na długie linie kodu
                if line.strip() == "" and code_lines:
                    break
                code_lines.append(line)
            except ValueError as e:
                print(f"❌ {e}")
            except (KeyboardInterrupt, EOFError):
                raise
        
        return "\n".join(code_lines)
    
    @staticmethod
    def _get_file_code() -> str:
        while True:
            try:
                file_path: str = safe_input("\n📁 Podaj ścieżkę do pliku z kodem: ", max_length=500)
                
                if not file_path:
                    print("❌ Ścieżka nie może być pusta!")
                    continue
                
                file_path = file_path.strip('"\'')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        code = file.read()
                    
                    if not code.strip():
                        print("❌ Plik jest pusty!")
                        continue
                    
                    print(f"✅ Wczytano kod z pliku: {file_path}")
                    print(f"📏 Rozmiar kodu: {len(code)} znaków")
                    return code
                    
                except FileNotFoundError:
                    print(f"❌ Plik nie istnieje: {file_path}")
                except PermissionError:
                    print(f"❌ Brak uprawnień do odczytu pliku: {file_path}")
                except UnicodeDecodeError:
                    print("❌ Błąd kodowania pliku. Spróbuj zapisać plik w kodowaniu UTF-8.")
                except Exception as e:
                    print(f"❌ Błąd podczas odczytu pliku: {e}")
                
                retry: str = safe_input("Czy chcesz spróbować ponownie? (t/n): ", max_length=10).strip().lower()
                if retry not in ['t', 'tak', 'y', 'yes']:
                    raise ValueError("Nie można wczytać kodu z pliku")
                    
            except ValueError as e:
                print(f"❌ {e}")
            except (KeyboardInterrupt, EOFError):
                raise


def print_review_result(result: CodeReviewResult) -> None:
    print("=" * 60)
    print("WYNIK PRZEGLĄDU KODU")
    print("=" * 60)
    
    print(f"\n📊 OCENA OGÓLNA: {result.overall_score}")
    
    print(f"\n🔍 ZNALEZIONE PROBLEMY ({len(result.found_issues)}):")
    if result.found_issues:
        for i, issue in enumerate(result.found_issues, 1):
            print(f"\n{i}. [{issue.severity.upper()}] {issue.type}")
            print(f"   Opis: {issue.description}")
            if issue.file:
                print(f"   Plik: {issue.file}")
            if issue.line:
                print(f"   Linia: {issue.line}")
    else:
        print("   Brak znalezionych problemów! 🎉")
    
    print(f"\n💡 POPRAWIONY KOD:")
    print("-" * 40)
    print(result.improved_code)
    print("-" * 40)


def get_user_input() -> tuple[str, str, str]:
    print("=" * 60)
    print("🔍 CODE REVIEW AGENT")
    print("=" * 60)
    print()
    
    project_language: str = UserInterface.get_language_choice()
    grading_scale: str = UserInterface.get_scale_choice()
    project_code: str = UserInterface.get_code_input()
    
    if not project_code.strip():
        raise ValueError("Kod nie może być pusty!")
    
    return project_code, project_language, grading_scale


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Code Review Agent - automatyczny przegląd kodu źródłowego",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python code_review_single.py                           # Tryb interaktywny
  python code_review_single.py -l python -o 1 kod.py     # Przegląd pliku Python w skali procentowej
  python code_review_single.py -l javascript -o 2 app.js # Przegląd pliku JS w skali 1-10
  python code_review_single.py -l go -o 3 main.go        # Przegląd pliku Go w skali szkolnej
  python code_review_single.py -l java -o 4 Main.java    # Przegląd pliku Java w skali A-F

Dostępne języki: python, javascript, java, go, c++, c#
Dostępne skale: 1=procentowa, 2=1-10, 3=szkolna, 4=A-F
        """
    )
    
    parser.add_argument(
        '-l', '--language',
        choices=['python', 'javascript', 'java', 'go', 'c++', 'c#'],
        help='Język programowania (python, javascript, java, go, c++, c#)'
    )
    
    parser.add_argument(
        '-o', '--output-scale',
        type=int,
        choices=[1, 2, 3, 4],
        help='Skala oceny: 1=procentowa, 2=1-10, 3=szkolna, 4=A-F'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Ścieżka do pliku z kodem do przeglądu'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Code Review Agent 1.0'
    )
    
    return parser.parse_args()


def load_code_from_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        
        if not code.strip():
            raise ValueError("Plik jest pusty")
        
        return code
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Plik nie istnieje: {file_path}")
    except PermissionError:
        raise PermissionError(f"Brak uprawnień do odczytu pliku: {file_path}")
    except UnicodeDecodeError:
        raise ValueError("Błąd kodowania pliku. Spróbuj zapisać plik w kodowaniu UTF-8.")


def run_interactive_mode() -> None:
    """Uruchamia tryb interaktywny z pętlą zamiast rekurencji."""
    MAX_REVIEWS: int = 10  # Limit na liczbę przeglądów w jednej sesji
    
    try:
        app: CodeReviewApp = CodeReviewApp()
        review_count: int = 0
        
        while review_count < MAX_REVIEWS:
            try:
                project_code: str
                project_language: str
                grading_scale: str
                project_code, project_language, grading_scale = get_user_input()
                
                print("\n🔍 Rozpoczynam przegląd kodu...")
                print(f"Język: {project_language}")
                print(f"Skala oceny: {grading_scale}")
                print()
                
                result: CodeReviewResult = app.review_code(project_code, project_language, grading_scale)
                print_review_result(result)
                
                review_count += 1
                
                print("\n" + "=" * 60)
                while True:
                    try:
                        again: str = safe_input("Czy chcesz przeprowadzić kolejny przegląd? (t/n): ", max_length=10).strip().lower()
                        if again in ['t', 'tak', 'y', 'yes']:
                            print("\n")
                            break
                        elif again in ['n', 'nie', 'no']:
                            print("👋 Dziękujemy za korzystanie z Code Review Agent!")
                            return
                        else:
                            print("❌ Wpisz 't' (tak) lub 'n' (nie)")
                    except ValueError as e:
                        print(f"❌ {e}")
                    except (KeyboardInterrupt, EOFError):
                        raise
                
            except KeyboardInterrupt:
                print("\n\n👋 Program przerwany przez użytkownika.")
                return
            except Exception as e:
                print(f"\n❌ Wystąpił błąd: {e}")
                try:
                    retry: str = safe_input("Czy chcesz spróbować ponownie? (t/n): ", max_length=10).strip().lower()
                    if retry not in ['t', 'tak', 'y', 'yes']:
                        return
                except ValueError as e:
                    print(f"❌ {e}")
                except (KeyboardInterrupt, EOFError):
                    raise
        
        print(f"\n⚠️ Osiągnięto limit {MAX_REVIEWS} przeglądów w jednej sesji.")
        print("👋 Dziękujemy za korzystanie z Code Review Agent!")
                
    except KeyboardInterrupt:
        print("\n\n👋 Program przerwany przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {e}")


def run_command_line_mode(args: argparse.Namespace) -> None:
    try:
        app = CodeReviewApp()
        
        language_map: Dict[str, str] = {
            "python": "Python", "javascript": "JavaScript", "java": "Java",
            "go": "Go", "c++": "C++", "c#": "C#"
        }
        
        scale_map: Dict[int, str] = {
            1: "procentowa 0-100%", 2: "skala 1-10",
            3: "szkolna 1-6", 4: "A-F"
        }
        
        project_language: str = language_map[args.language]
        grading_scale: str = scale_map[args.output_scale]
        
        print(f"📁 Wczytuję kod z pliku: {args.file}")
        project_code: str = load_code_from_file(args.file)
        
        print(f"✅ Wczytano kod z pliku: {args.file}")
        print(f"📏 Rozmiar kodu: {len(project_code)} znaków")
        print("🔍 Rozpoczynam przegląd kodu...")
        print(f"Język: {project_language}")
        print(f"Skala oceny: {grading_scale}")
        print()
        
        result: CodeReviewResult = app.review_code(project_code, project_language, grading_scale)
        print_review_result(result)
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        sys.exit(1)


def main() -> None:
    args: argparse.Namespace = parse_arguments()
    
    if not args.language and not args.output_scale and not args.file:
        run_interactive_mode()
    else:
        if not all([args.language, args.output_scale, args.file]):
            print("❌ Błąd: W trybie wiersza poleceń wymagane są wszystkie parametry:")
            print("   -l/--language (język programowania)")
            print("   -o/--output-scale (skala oceny)")
            print("   ścieżka do pliku")
            print("\nUruchom program bez argumentów dla trybu interaktywnego.")
            sys.exit(1)
        
        run_command_line_mode(args)


if __name__ == "__main__":
    main()
