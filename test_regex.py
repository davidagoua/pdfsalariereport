
import re

def test_matricule(text):
    match = re.search(r'(PERCO?\d+)', text)
    return match.group(1) if match else None

# Test cases
cases = [
    ("Matricule : PERC001", "PERC001"),
    ("Matricule : PERCO123", "PERCO123"),
    ("Some text PERC999 end", "PERC999"),
    ("No match here", None)
]

print("Testing Regex: r'(PERCO?\d+)'")
for text, expected in cases:
    result = test_matricule(text)
    status = "PASS" if result == expected else f"FAIL (Expected {expected}, got {result})"
    print(f"'{text}' -> {status}")
