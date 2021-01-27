from .exception import ArgumentError


def parse_args(text):
    args = []
    kwargs = {}
    index = 0
    text = text + '  '

    def next_word():
        nonlocal index, text

        if index >= len(text) - 2:
            return None

        if text[index] == '"':
            return next_quoted_string()

        if text[index:index+2] == '--' and text[index+2] != ' ':
            handle_multi_char_kwarg()
            return None

        if text[index] == '-' and text[index+1] != ' ':
            handle_single_char_kwarg()
            return None

        word = ''

        while text[index] != ' ':
            word += text[index]
            index += 1

        return word

    def next_quoted_string():
        nonlocal index, text

        index += 1
        quoted_string = ''

        while text[index:index+2] != '" ' or text[index+1] == '\\':
            quoted_string += text[index]
            index += 1

            if index == len(text):
                raise ArgumentError("One of your quotes is not closed!")

        index += 1

        return quoted_string

    def handle_single_char_kwarg():
        nonlocal index, text, kwargs

        index += 1
        chars = ''

        while text[index] != ' ':
            chars += text[index]
            index += 1

        index += 1
        word = next_word()

        if word is None:
            value = True
        else:
            value = word

        for char in chars:
            kwargs[char] = value

    def handle_multi_char_kwarg():
        nonlocal index, text, kwargs

        index += 2
        kwarg = ''

        while text[index] != ' ':
            kwarg += text[index]
            index += 1

        index += 1
        word = next_word()

        if word is None:
            kwargs[kwarg] = True
        else:
            kwargs[kwarg] = word

    while index < len(text) - 2:
        if text[index] == ' ':
            index += 1
            continue

        word = next_word()

        if word is not None:
            args.append(word)

    return args, kwargs

