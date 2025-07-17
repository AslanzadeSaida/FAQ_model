import requests
from bs4 import BeautifulSoup
import csv
import json
 
URL = "https://e-gov.az/az/home/faq?name=asan_login"


headers = {
    'User-Agent': 'Mozilla/5.0'
}

response = requests.get(URL, headers=headers, timeout =15)

with open("asan_login.html", "w", encoding="utf-8") as f:
    f.write(response.text)



soup = BeautifulSoup(response.text, 'html.parser')
questions = soup.find_all("span", class_="faq-title")
answers = soup.find_all("p", class_="faq-content")


faq_data_asan_login = []

for i, (q, a) in enumerate(zip(questions, answers), 1):
    question = q.get_text(strip=True)
    answer = a.get_text(strip=True)
    faq_data_asan_login.append({
        "Questions": question,
        "Answers": answer
    })

with open("faq_data_asan_login.csv", "w", encoding="utf-8", newline="") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=["Questions", "Answers"])
    writer.writeheader()
    writer.writerows(faq_data_asan_login)


with open("faq_data_asan_login.json", "w", encoding="utf-8") as f_json:
    json.dump(faq_data_asan_login, f_json, ensure_ascii=False, indent=2)







