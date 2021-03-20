import math

def is_shifted(char):
    return char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?'

def typing_diff(text):
    current_points = 0
    total_points = 0
    words = 0

    text = f"  {text} "

    for i in range(2, len(text)):
        if text[i] == ' ':
            total_points += current_points**2
            current_points = 0
            words += 1
            continue

        current_points += 1 \
            + (is_shifted(text[i]) != is_shifted(text[i-1])) \
            + 0.25 * text[i].isdigit() \
            + 0.3 * (not text[i].isdigit() and not text[i].isalpha()) \
            + 0.5 * (text[i] == text[i-1] != text[i-2])

    return total_points / words * math.log(len(text))

print(typing_diff(""))
