import pytest
import os
import string

def analyze_file(file_obj):
    content = file_obj.read()

    if not content.strip():
        return {"word_count": 0, "line_count": 0, "unique_word_count": 0}

    lines = content.splitlines()

    # Видаляємо пунктуацію з кожного слова
    translator = str.maketrans('', '', string.punctuation)
    words = [w.translate(translator) for w in content.split() if w.strip()]
    unique_words = set(words)

    return {
        'word_count': len(words),
        'line_count': len(lines),
        'unique_word_count': len(unique_words)
    }

def create_sample_file(filename):
    with open(filename, 'w') as f:
        f.write("Це перший рядок.\n")
        f.write("Це другий рядок з тими самими словами.\n")
        f.write("Слова можуть бути повторені.\n")


if __name__ == '__main__':
    sample_filename = "sample_text.txt"
    create_sample_file(sample_filename)

    with open(sample_filename, 'r') as f_obj:
        results = analyze_file(f_obj)
        print("Результати аналізу:")
        print(f"Кількість слів: {results['word_count']}")
        print(f"Кількість рядків: {results['line_count']}")
        print(f"Кількість унікальних слів: {results['unique_word_count']}")

    os.remove(sample_filename)  # Видаляємо тимчасовий файл

# Тести для функції analyze_file

def test_analyze_file_with_valid_data(tmp_path):
    temp_file = tmp_path / "test_data.txt"
    test_content = """\
Hello world.
This is a test.
Hello again.
"""
    temp_file.write_text(test_content)

    with open(temp_file, 'r') as f_obj:
        results = analyze_file(f_obj)

    assert results['word_count'] == 8  # фактична кількість слів
    assert results['line_count'] == 3
    assert results['unique_word_count'] == 7  # 'Hello', 'world.', 'This', 'is', 'a', 'test.', 'again.'


def test_analyze_file_empty_file(tmp_path):

    temp_file = tmp_path / "empty_file.txt"
    temp_file.write_text("")

    with open(temp_file, 'r') as f_obj:
        results = analyze_file(f_obj)

    assert results['word_count'] == 0
    assert results['line_count'] == 0
    assert results['unique_word_count'] == 0


def test_analyze_file_with_punctuation(tmp_path):
    temp_file = tmp_path / "punctuation.txt"
    test_content = "Word one, word two. Word three!\nWord four."
    temp_file.write_text(test_content)

    with open(temp_file, 'r') as f_obj:
        results = analyze_file(f_obj)

    assert results['word_count'] == 8  # 'Word', 'one,', 'word', 'two.', 'Word', 'three!', 'Word', 'four.'
    assert results['line_count'] == 2
    assert results['unique_word_count'] == 6

