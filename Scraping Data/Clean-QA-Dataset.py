import html
import json
from pathlib import Path

#paths 
SCRIPT_DIR = Path(__file__).resolve().parent            
PROJECT_ROOT = SCRIPT_DIR.parent                        

INPUT_FILE = PROJECT_ROOT / "arch_questions.json"
OUTPUT_FILE = PROJECT_ROOT / "arch_training_data.json"

# clean-ups
UNESCAPE_HTML = True       # '&#39;' -> "'"  (the SE API escapes HTML entities)
NORMALIZE_NEWLINES = True  # '\r\n'  -> '\n'


def clean_text(text):
    """Normalize a body_markdown / title string for training data."""
    if not text:
        return ""
    if NORMALIZE_NEWLINES:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    if UNESCAPE_HTML:
        text = html.unescape(text)
    return text.strip()


def find_accepted_answer(question):
    """Return the answer dict with is_accepted == True, or None."""
    for answer in question.get("answers") or []:
        if answer.get("is_accepted") is True:
            accepted_id = question.get("accepted_answer_id")
            if accepted_id is not None and answer.get("answer_id") != accepted_id:
                print(f"  ! answer_id mismatch on question {question.get('question_id')}")
            return answer
    return None


def main():
    if not INPUT_FILE.exists():
        raise SystemExit(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions from {INPUT_FILE.name}")

    # Append mode: load existing records first, then extend the list.
    records = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
        print(f"Appending to existing {OUTPUT_FILE.name} ({len(records)} records)")

    skipped_no_accept_id = 0
    skipped_no_accepted_answer = 0

    for question in questions:
        if "accepted_answer_id" not in question:
            skipped_no_accept_id += 1
            continue

        answer = find_accepted_answer(question)
        if answer is None:
            skipped_no_accepted_answer += 1
            continue

        records.append({
            "title": clean_text(question.get("title")),
            "tags": question.get("tags") or [],
            "question": clean_text(question.get("body_markdown")),
            "answer": clean_text(answer.get("body_markdown")),
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"Skipped {skipped_no_accept_id} questions (no accepted_answer_id)")
    print(f"Skipped {skipped_no_accepted_answer} questions (accepted answer not found)")
    print(f"Wrote {len(records)} clean Q/A records to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
