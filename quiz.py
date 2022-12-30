import os


def get_quiz(folder_name):
    folder_files = os.listdir(folder_name)
    quiz = {}
    for file in folder_files:
        with open(f'quiz_items/{file}', 'r', encoding='KOI8-R') as file:
            for question_text in file.read().split('\n\n\n'):
                for fragment in question_text.split('\n\n'):
                    fragment = fragment.replace('\n', '')
                    if fragment[:6] == 'Вопрос':
                        question = fragment.strip()
                    if fragment[:5] == 'Ответ':
                        answer = fragment.strip().replace('Ответ:', '')
                quiz[question] = answer
    return quiz

if __name__ == "__main__":
    get_quiz("quiz_items")
