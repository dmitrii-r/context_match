import json
import re
from typing import List, Dict, Union

import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def parse_expression(expression: str) -> List[str]:
    """
    Разбирает логическое выражение и возвращает его в виде обратной польской записи.
    """
    words = re.findall(r'\b\w+\b|\(|\)', expression.lower())
    operators = {'или': 1, 'и': 2, 'не': 3}

    result = []
    stack = []

    for word in words:
        if word in operators:
            while stack and stack[-1] in operators and operators[stack[-1]] >= operators[word]:
                result.append(stack.pop())
            stack.append(word)
        elif word == '(':
            stack.append(word)
        elif word == ')':
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            stack.pop()
        else:
            result.append(word)

    while stack:
        result.append(stack.pop())

    return result


def evaluate_expression(parsed_expression: List[str], word_values: Dict[str, Union[bool, str]]) -> Union[bool, str]:
    """
    Вычисляет значение логического выражения.
    """
    stack = []
    operators = {'или', 'и', 'не'}

    for token in parsed_expression:
        if token not in operators:
            stack.append(word_values.get(token, False))
        else:
            if token == 'и':
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(operand1 and operand2)
            elif token == 'или':
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(operand1 or operand2)
            elif token == 'не':
                operand = stack.pop()
                stack.append(not operand)

    return stack[0]


def normalize_word(word: str) -> str:
    """
    Нормализует слово с использованием pymorphy2.
    """
    parsed_word = morph.parse(word)[0]
    return parsed_word.normal_form


def check_rule(input_text: str, rule: str) -> bool:
    """
    Проверяет, соответствует ли текст заданному правилу.
    """
    parsed_expression = parse_expression(rule)
    word_values = {word: True for word in re.findall(r'\b\w+\b', input_text)}
    normalized_word_values = {normalize_word(word): value for word, value in word_values.items()}

    result = evaluate_expression(parsed_expression, normalized_word_values)
    return result


if __name__ == '__main__':

    rules = [
        'Екатеринбург',
        'центр и (Екатеринбург или Екб) и не Москва',
        'центр и Москва',
        'Екатеринбург и (вчера и (не Москва или не Петербург))',
        'Екатеринбург и (вчера и (не город или не проект))',
        'Екатеринбург и (вчера и не (производство или инфраструктура))',
    ]

    json_path = 'news_sample.json'

    with open(json_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        input_text = data.get('text', '')

    for rule in rules:
        if check_rule(input_text, rule):
            print(f'Tекст соответствует правилу: {rule}.')
        else:
            print(f'Текст не соответствует правилу: {rule}.')
