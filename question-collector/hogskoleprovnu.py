from bs4 import BeautifulSoup
import requests
import re, json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

BASE_URL = 'https://www.högskoleprovet.nu/ord'


def getYears():
    try:
        request = requests.get(BASE_URL)
        soup = BeautifulSoup(request.text, 'html.parser')

        hrefRegex = re.compile('^https://hpskolan.kurser.io/gamla-prov/test/')

        years = soup.find_all(
            'a', attrs={'class': 'elementor-button-link', 'href': hrefRegex})
        links = [year['href'] for year in years]

        return links
    except:
        print('Could not load years')
        return None


def getQuestions(url, driver):
    driver.get(url)

    try:
        start_btn = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-success')))
        start_btn.click()

        question_containers = driver.find_elements_by_tag_name('app-single-word-view')
        questions = []

        for question_container in question_containers:
            text = question_container.find_element_by_class_name('single-word-template').text
            alternatives = [a.text for a in question_container.find_elements_by_class_name('alternative')]
            
            correct_btn = question_container.find_element_by_class_name('btn-inline-default')
            correct_btn.click()

            modal = driver.find_element_by_tag_name('app-explanation-modal')
            correct_label = modal.find_element_by_tag_name('b')

            correct_letter = correct_label.text.replace('Rätt svar är alternativ:', '').strip()
            correct = 0

            if correct_letter == 'A':
                correct = 0
            elif correct_letter == 'B':
                correct = 1
            elif correct_letter == 'C':
                correct = 2
            elif correct_letter == 'D':
                correct = 3
            elif correct_letter == 'E':
                correct = 4

            close = modal.find_element_by_class_name('btn-outline-default')
            close.click()

            question = {
                'text': text,
                'alternatives': alternatives,
                'correct': correct
            }

            questions.append(question)

        return questions

    except TimeoutException:
        print("Check your internet connection.")


def main():
    years = getYears()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('no-sandbox')

    driver = webdriver.Chrome(chrome_options=options)
    all_questions = []

    for year in years:
        questions = getQuestions(year, driver)
        all_questions.extend(questions)

    driver.close()

    questions_json = json.dumps(all_questions)
    result_file = open('questions.json', 'w')
    result_file.write(questions_json)

if __name__ == "__main__":
    main()
