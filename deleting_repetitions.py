import re


def remove_repeated_words(text):
    parts = re.split(r'(\[.*?\])', text)
    processed_parts = []

    for part in parts:
        if re.match(r'\[.*?\]', part):
            processed_parts.append(part)
            continue

        def collapse_repeats(match):
            return match.group(1)

        cleaned = re.sub(r'\b(\w+)(?:\s+\1){3,}\b',
                         collapse_repeats,
                         part,
                         flags=re.IGNORECASE)
        processed_parts.append(cleaned)

    result = ''.join(processed_parts)
    result = re.sub(r'\s+', ' ', result).strip()
    return result