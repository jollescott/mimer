from bs4 import BeautifulSoup
import requests
import re
from pyppeteer import launch
import asyncio

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


async def getQuestions(url):
    browser = await launch({ 'args': ['--no-sandbox', '--disable-setuid-sandbox'] })
    page = await browser.newPage()

    await page.goto(url)
    await page.click('button#btn-success')

    groups = await page.querySelectorAll('app-single-word-view')

    questions = []

    for group in groups:
        alternatives = []

        listItems = await group.querySelectorAll('li')
        alternatives.append([item.getProperty('textContent')
                             for item in listItems])

        textLabel = await group.querySelector('div#single-word-template')
        textResult = await textLabel.getProperty('textContent')
        text = textResult.jsonValue()

        await group.click('button#btn-sm')

        correctLabel = await group.querySelector('b')
        correctResult = await correctLabel.getProperty('textContent')
        correct = await correctResult.jsonValue()

        correct = correct.replace('Rätt svar är alternativ:', '')
        correct = correct.strip()

        question = {
            alternatives: alternatives,
            text: text,
            correct: correct
        }

        questions.append(question)

    await browser.close()

links = getYears()
asyncio.run(getQuestions(links[0]))