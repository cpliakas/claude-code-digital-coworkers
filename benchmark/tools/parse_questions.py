#!/usr/bin/env python3
"""Parse the raw SAA-C03 questions file into structured JSON."""

import json
import re
import sys


def parse_questions(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split on the dashed separators
    blocks = re.split(r"-{10,}", text)
    questions = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Match question number at start: "123]" or "123 ]"
        num_match = re.match(r"(\d+)\s*\]", block)
        if not num_match:
            continue

        number = int(num_match.group(1))
        rest = block[num_match.end() :].strip()

        # Split on "ans-" or "Answer:" to separate question from answer
        answer_split = re.split(r"(?:^|\n)\s*(?:ans\s*[-–:]|Answer\s*[:.])", rest, maxsplit=1)

        if len(answer_split) < 2:
            # Try alternate: line starting with a capital letter option like "A." "B." "C." "D."
            answer_split = re.split(r"\n\s*([A-D][\.\)]\s)", rest, maxsplit=1)
            if len(answer_split) >= 2:
                scenario = answer_split[0].strip()
                answer_text = "".join(answer_split[1:]).strip()
            else:
                # Can't parse answer, skip
                continue
        else:
            scenario = answer_split[0].strip()
            answer_text = answer_split[1].strip()

        # Clean up scenario: remove trailing "Which solution..." if it got cut off
        # but keep it as part of the question
        scenario = re.sub(r"\n+", " ", scenario).strip()

        # Extract just the answer (first line/sentence) vs the explanation
        answer_lines = answer_text.split("\n")
        answer_short = answer_lines[0].strip()
        explanation = "\n".join(answer_lines[1:]).strip()

        # Clean up
        answer_short = re.sub(r"^\s*[A-D][\.\)]\s*", "", answer_short).strip()
        answer_short = answer_short.rstrip(".")

        if not scenario or not answer_short:
            continue

        questions.append(
            {
                "id": number,
                "scenario": scenario,
                "correct_answer": answer_short,
                "explanation": explanation,
            }
        )

    return questions


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else "raw-questions.txt"
    questions = parse_questions(filepath)

    # Deduplicate by id (keep first occurrence)
    seen = set()
    unique = []
    for q in questions:
        if q["id"] not in seen:
            seen.add(q["id"])
            unique.append(q)

    unique.sort(key=lambda q: q["id"])

    with open("questions.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(unique)} unique questions")


if __name__ == "__main__":
    main()
