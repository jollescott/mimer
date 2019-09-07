import os, json, random
from openpyxl import load_workbook

def scrape():
    wb = load_workbook('./greenlandic.xlsx', read_only=True)
    ws = wb.active

    islandic = []
    english = []
    tags = []

    for row in ws.iter_rows():
        original = row[0]
        translated = row[3]
        tag = row[1]

        if original.value is not None and translated.value is not None:

            if ',' not in original.value and len(original.value.split()) == 1:
                islandic.append(original.value)
                english.append(translated.value)
                tags.append(tag.value)

    return (islandic, english, tags)
        

def format_questions(words):
    questions = []
    index = 0

    for question in words[0]:
        alternatives = random.sample(words[1], 4)
        correct = words[1][index]

        alternatives.append(correct)
        random.shuffle(alternatives)

        correct_index = alternatives.index(correct)

        question = {
            'text': question,
            'alternatives': alternatives,
            'correct': correct_index
        }

        if words[2][index] is not None:
            question['tag'] = words[2][index]

        questions.append(question)

        index += 1

    return questions

if __name__ == "__main__":
    if os.path.isfile('./greenlandic.xlsx'):
        questions = scrape()
        questions = format_questions(questions)
        
        file = open('questions.json', 'w')
        file.write(json.dumps(questions))
    else:
        print('Dictionary not found.')
    