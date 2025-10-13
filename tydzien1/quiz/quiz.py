from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI()

# Nazwa modelu, którego użyjemy do generowania pytań
MODEL_NAME = "gpt-4.1-mini"

def generate_quiz_questions(quiz_topic, num_questions):
    # Prompt systemowy: opisujemy format i oczekiwania treści
    system_prompt = (
        "Jesteś asystentem generującym pytania do quizu. "
        "Twórz pytania po polsku, 4 odpowiedzi (a, b, c, d), tylko jedna poprawna."
        "Zwróć WYŁĄCZNIE JSON. Struktura:\n"
        "{\n"
        '  "questions": [\n'
        "    {\n"
        '      "question": "pytanie",\n'
        '      "a": "odpowiedź A",\n'
        '      "b": "odpowiedź B",\n'
        '      "c": "odpowiedź C",\n'
        '      "d": "odpowiedź D",\n'
        '      "correct_answer": "a|b|c|d"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Bez komentarzy, bez tekstu poza JSON."
    )
    user_prompt = (
        f"Stwórz {num_questions} pytań do quizu na temat: '{quiz_topic}'. "
    )

    # Użyjemy Chat Completions i wymusimy JSON promptem
    model_name = MODEL_NAME

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Informujemy użytkownika, że trwa generowanie pytań
    print("Generuję pytania...")

    # Wymuszamy JSON przez prompt oraz walidujemy strukturę po stronie klienta

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0,
        )
        content = completion.choices[0].message.content if getattr(completion, "choices", None) else ""
        if not content:
            print("[debug] Pusta odpowiedź modelu.")
            return []
        try:
            json_data = json.loads(content)
        except Exception as parse_err:
            print(f"[debug] Nie udało się sparsować odpowiedzi jako JSON: {parse_err}")
            print(f"[debug] content (skrócone): {content[:400]}")
            return []
    except Exception as e:
        print(f"Błąd generowania pytań: {e}")
        return []

    if not isinstance(json_data, dict) or "questions" not in json_data:
        print("Model nie zwrócił poprawnych danych (brak pola 'questions').")
        return []

    questions_list = []
    skipped_missing_fields = 0
    skipped_invalid_values = 0
    for question_item in json_data.get("questions", []):
        has_all_fields = all(
            key in question_item for key in ["question", "a", "b", "c", "d", "correct_answer"]
        )
        if not has_all_fields:
            skipped_missing_fields += 1
            continue

        # Normalizujemy literę poprawnej odpowiedzi
        correct_letter = str(question_item.get("correct_answer", "")).strip().lower()
        correct_letter_ok = correct_letter in ("a", "b", "c", "d")
        fields_not_empty = all(
            str(question_item.get(key, "")).strip() != "" for key in ["question", "a", "b", "c", "d"]
        )

        if correct_letter_ok and fields_not_empty:
            question_item["correct_answer"] = correct_letter
            questions_list.append(question_item)
        else:
            skipped_invalid_values += 1

    if skipped_missing_fields or skipped_invalid_values:
        print(
            f"Pominięto pytania: brak pól={skipped_missing_fields}, puste/niepoprawne wartości={skipped_invalid_values}."
        )

    return questions_list[:num_questions]

def run_quiz(questions_list):
    collected_answers = []
    print("\n=== Zaczynamy quiz! ===\n")
    question_number = 1

    for question_obj in questions_list:
        print(f"Pytanie {question_number}: {question_obj['question']}")
        print(f"a) {question_obj['a']}")
        print(f"b) {question_obj['b']}")
        print(f"c) {question_obj['c']}")
        print(f"d) {question_obj['d']}")

        # Pytamy o odpowiedź użytkownika (a/b/c/d) i walidujemy
        user_choice = ""
        while True:
            try:
                user_choice = input("Twoja odpowiedź (a/b/c/d, q = zakończ): ").strip().lower()
            except EOFError:
                print("\nWejście zakończone. Kończę quiz.")
                return collected_answers
            if user_choice in ("a", "b", "c", "d"):
                break
            if user_choice == "q":
                print("Zakończono na życzenie użytkownika.")
                return collected_answers
            print("Niepoprawny wybór. Wpisz a, b, c, d lub q.")

        collected_answers.append({
            "number": question_number,
            "question_text": question_obj["question"],
            "options": {
                "a": question_obj["a"],
                "b": question_obj["b"],
                "c": question_obj["c"],
                "d": question_obj["d"]
            },
            # Trzymamy znormalizowane wartości, by uniknąć powtórzeń .lower()
            "user_answer": user_choice,
            "correct_answer": question_obj["correct_answer"]
        })

        print("")
        question_number += 1

    correct_count = 0
    for answer_record in collected_answers:
        # Porównanie już znormalizowanych liter
        if answer_record["user_answer"] == answer_record["correct_answer"]:
            correct_count += 1

    total_count = len(collected_answers)
    print("=== Wynik ===")
    print(f"Poprawnych: {correct_count} / {total_count}")
    print(f"Niepoprawnych: {total_count - correct_count}")
    percentage_score = round(100 * correct_count / max(1, total_count))
    print(f"Wynik procentowy: {percentage_score}%")

    if percentage_score >= 90:
        print("Ocena: SUPER")
    elif percentage_score >= 60:
        print("Ocena: OK")
    else:
        print("Ocena: SPRÓBUJ JESZCZE RAZ")

    print("\n=== Podsumowanie odpowiedzi ===")
    for answer_record in collected_answers:
        is_correct = (answer_record["user_answer"] == answer_record["correct_answer"])
        status_text = "poprawna" if is_correct else "niepoprawna"
        print(f"Pytanie {answer_record['number']}: {status_text}")

        user_letter = answer_record["user_answer"]
        print(f"• Pytanie: {answer_record['question_text']}")
        print(f"• Twoja odpowiedź: {user_letter}) {answer_record['options'][user_letter]}")

        if not is_correct:
            correct_letter = answer_record["correct_answer"]
            print(f"• Poprawna odpowiedź: {correct_letter}) {answer_record['options'][correct_letter]}")
        print("")

    if correct_count == total_count and total_count > 0:
        print("Świetnie! Wszystkie odpowiedzi poprawne.")

def main():
    print("=== Quiz tematyczny z AI ===")
    quiz_topic = input("Podaj temat quizu (np. 'Sztuczna inteligencja', 'Python podstawy'): ").strip()
    if quiz_topic == "":
        quiz_topic = "ogólna wiedza"

    num_questions_text = input("Ile pytań wygenerować? (np. 5 lub 10): ").strip()
    if num_questions_text.isdigit():
        num_questions = int(num_questions_text)
        if num_questions <= 0:
            num_questions = 1
            print("Muszę zadać przynajmniej 1 pytanie.")
    else:
        num_questions = 5
        print("Może ustawię na 5 pytań.")

    questions_list = generate_quiz_questions(quiz_topic, num_questions)
    if len(questions_list) == 0:
        print("Nie udało się pobrać poprawnych pytań. Spróbuj inny temat albo inną liczbę pytań.")
        return

    run_quiz(questions_list)

if __name__ == "__main__":
    main()
