"""Validate the shipped lesson data and its local audio references."""
import json
import re
import sys
from pathlib import Path

from gen_audio import filename

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'public/audio'
errors = []


def load(name):
    return json.loads((ROOT / 'src/data' / f'{name}.json').read_text(encoding='utf-8'))


def check(condition, message):
    if not condition:
        errors.append(message)


def normalize(text):
    return ' '.join(text.casefold().replace('’', "'").split())


words = [word['word'] for deck in load('words') for word in deck['words']]
mapping = load('word-audio')
listening, reading, grammar = (load(name) for name in ('listening', 'reading', 'grammar'))
writing, phrases = load('writing'), load('phrases')
question_total = 0
for lessons in (listening, reading, grammar):
    for lesson in lessons:
        for index, question in enumerate(lesson['questions'], 1):
            answer = question['answer']
            check(type(answer) is int and 0 <= answer < len(question['options']),
                  f"{lesson['id']} question {index}: invalid answer index {answer}")
            question_total += 1
print(f'{question_total} quiz answer indices checked')

dictation_total = 0
for lesson in listening:
    for index, entry in enumerate(lesson['dictation'], 1):
        filled = entry['prompt'].replace('____', entry['answer'])
        check(entry['prompt'].count('____') == 1 and bool(entry['answer'])
              and normalize(filled) in normalize(lesson['transcript']),
              f"{lesson['id']} dictation {index}: {filled}")
        dictation_total += 1
print(f'{dictation_total} reconstructed dictation prompts checked')

glossary_total = 0
for article in reading:
    body = '\n'.join(article['paragraphs'])
    for entry in article['glossary']:
        word = entry['word']
        base = re.escape(word)
        forms = f'{base}|{base[:-1]}ies' if word.endswith('y') else f'{base}(?:s|es)?'
        check(re.search(rf'\b(?:{forms})\b', body, re.I), f"{article['id']} glossary: {word}")
        glossary_total += 1
print(f'{glossary_total} glossary entries checked')

for template in writing['templates']:
    count = len(re.findall(r"[A-Za-z0-9]+(?:[’,.'-][A-Za-z0-9]+)*", template['sampleEssay']))
    minimum = {'IELTS Task 1': 150, 'IELTS Task 2': 250}.get(template['exam'], 150)
    target = max(template['target'], minimum)
    check(count >= target, f"{template['id']} sample: {count} < {target}")
    print(f"{template['id']}: {count} words (target {target})")

check(set(words) == set(mapping), 'Word audio mapping and vocabulary differ')
total_bytes = 0
for category, names in [
    ('words', list(mapping.values())),
    ('listening', [filename(item['id']) for item in listening]),
    ('phrases', [filename(item['id']) for item in phrases]),
]:
    actual = {path.name: path.stat().st_size for path in (AUDIO / category).glob('*.mp3') if path.is_file()}
    check(len(set(names)) == len(names), f'{category}: duplicate audio references')
    for name in sorted(set(names) - actual.keys()):
        errors.append(f'{category}/{name}: missing')
    for name, size in actual.items():
        check(size > 0, f'{category}/{name}: empty audio file')
        check(name in names, f'{category}/{name}: unused audio file')
    size = sum(actual.values())
    total_bytes += size
    print(f'{category}: {len(actual)} MP3 files, {size:,} bytes')
print(f'Total audio: {total_bytes:,} bytes')

if errors:
    sys.exit('\n'.join(errors))
