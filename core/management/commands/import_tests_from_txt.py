import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Test, Question, Choice


OPTION_RE = re.compile(r"^(?P<label>[A-Z])\s*[\).:-]\s*(?P<text>.+)$")
ANSWER_RE = re.compile(r"^\s*(answer|javob)\s*[:\-]\s*(?P<label>[A-Z])\s*$", re.IGNORECASE)
CORRECT_MARKERS = ("✅", "[x]", "(correct)", "(to'g'ri)", "(tog'ri)", "*", "✔")


def normalize_question(line: str) -> str:
    return re.sub(r"^\s*\d+\s*[\).:-]\s*", "", line).strip()


def parse_blocks(text: str):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        yield lines


def extract_correct_label(option_text: str) -> tuple[str, bool]:
    marker_found = False
    cleaned = option_text
    for marker in CORRECT_MARKERS:
        if marker in cleaned:
            marker_found = True
            cleaned = cleaned.replace(marker, "").strip()
    return cleaned, marker_found


class Command(BaseCommand):
    help = "Import test questions from a .txt file."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to .txt file with questions")
        parser.add_argument("--title", required=True, help="Test title to create or update")
        parser.add_argument("--published", action="store_true", help="Mark the test as published")
        parser.add_argument("--dry-run", action="store_true", help="Parse only, do not write to DB")

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        raw = file_path.read_text(encoding="utf-8")
        blocks = list(parse_blocks(raw))
        if not blocks:
            raise CommandError("No questions found in file.")

        parsed_questions = []
        for lines in blocks:
            question_text = normalize_question(lines[0])
            if not question_text:
                continue
            answer_label = None
            options = []
            for line in lines[1:]:
                answer_match = ANSWER_RE.match(line)
                if answer_match:
                    answer_label = answer_match.group("label").upper()
                    continue

                match = OPTION_RE.match(line)
                if match:
                    label = match.group("label").upper()
                    opt_text, marked = extract_correct_label(match.group("text").strip())
                    options.append({"label": label, "text": opt_text, "is_correct": marked})

            if not options:
                continue

            if answer_label:
                for opt in options:
                    opt["is_correct"] = opt["label"] == answer_label

            parsed_questions.append({"text": question_text, "options": options})

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"Dry run: parsed {len(parsed_questions)} questions."))
            return

        with transaction.atomic():
            test, _ = Test.objects.get_or_create(title=options["title"], defaults={"is_published": options["published"]})
            if options["published"]:
                test.is_published = True
                test.save()

            for index, payload in enumerate(parsed_questions, start=1):
                question = Question.objects.create(
                    test=test,
                    text=payload["text"],
                    order=index,
                )
                for opt in payload["options"]:
                    Choice.objects.create(
                        question=question,
                        text=opt["text"],
                        is_correct=opt["is_correct"],
                    )

        self.stdout.write(self.style.SUCCESS(f"Imported {len(parsed_questions)} questions into '{test.title}'."))
