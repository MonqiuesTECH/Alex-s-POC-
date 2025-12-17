# core/prompt_parser.py

def parse_prompt_lines(lines):
    """
    Converts prompt lines into normalized units.
    POC rules-based parser.
    """
    units = []
    for line in lines:
        t = line.strip()
        if not t:
            continue

        if len(t) == 1 and t.isalpha():
            units.append({"text": t.upper(), "type": "letter"})
        elif t.isdigit():
            units.append({"text": t, "type": "number"})
        else:
            units.append({"text": t.upper(), "type": "word"})

    return units
