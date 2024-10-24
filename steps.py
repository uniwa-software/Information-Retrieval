from bs4 import BeautifulSoup
import requests
import json
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
#Κώδικας για το web crawler. - Βήμα 1

subject = input("Δώσε ένα θέμα:").strip()
subject = subject.replace(" ", "_")
url = f'https://en.wikipedia.org/wiki/{subject}'
print(url)
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

data= {}

data['title'] = soup.title.string

paragraphs = [p.get_text() for p in soup.find_all('p')]
data['paragraphs'] = paragraphs

json_data = json.dumps(data, indent=4)

file_path = 'webpage_data.json'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        try:
            existing_data = json.load(json_file)
        except json.JSONDecodeError:
            existing_data = []
else:
    existing_data = []

existing_data.append(data)

with open(file_path, 'w', encoding='utf-8') as json_file:
    json.dump(existing_data, json_file, indent=4, ensure_ascii=False)

#Προεπεξεργασία κειμένου. - Βήμα 2

processed_data = {}
processed_data['title'] = data['title']
wnl = nltk.WordNetLemmatizer()
stop_words = nltk.corpus.stopwords.words('english')


def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  #Διγραφή special χαρακτήρων.
    text = re.sub(r'\s+', ' ', text) #Αντικατάσταση πολλαπλών space με ένα.
    text = text.strip() 
    
    tokens = word_tokenize(text)
    
    tokens = [wnl.lemmatize(word.lower()) for word in tokens if word.lower() not in stop_words]
    
    return tokens

processed_data['paragraphs'] = [preprocess_text(p) for p in paragraphs]
processed_json_data = json.dumps(processed_data, indent=4, ensure_ascii=False)
processed_file_path = 'processed_webpage_data.json'

if os.path.exists(file_path):
    with open(processed_file_path, 'r', encoding='utf-8') as json_file:
        try:
            existing_processed_data = json.load(json_file)
        except json.JSONDecodeError:
            existing_processed_data = []
else:
    existing_processed_data = []

existing_processed_data.append(processed_data)

with open(processed_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(existing_processed_data, json_file, indent=4, ensure_ascii=False)

print(f"New data has been appended to '{file_path}' (unprocessed) and '{processed_file_path}' (processed).")