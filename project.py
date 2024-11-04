import os
import re
import json
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

#Κλάση για την εξαγωγή και επεξεργασία περιεχομένου από τη Wikipedia.
class WikipediaCrawler:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def get_wikipedia_content(self, subject: str) -> Dict[str, Any]:
        # Μορφοποίηση του θέματος για χρήση στο URL
        formatted_subject = subject.strip().replace(" ", "_")
        url = f'https://en.wikipedia.org/wiki/{formatted_subject}'
        
        try:
            # Λήψη και επεξεργασία της σελίδας
            page = requests.get(url)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, 'html.parser')
            
            #Επιστρέφει:Dict[str, Any]: Λεξικό με τον τίτλο και τις παραγράφους της σελίδας
            return {
                'title': soup.title.string,
                'paragraphs': [p.get_text() for p in soup.find_all('p')]
            }
        except requests.RequestException as e:
            print(f"Σφάλμα κατά τη λήψη της σελίδας Wikipedia: {e}")
            return None

    def preprocess_text(self, text: str) -> List[str]:
        """
        Επεξεργάζεται το κείμενο αφαιρώντας ειδικούς χαρακτήρες, μετατρέποντας
        σε πεζά, αφαιρώντας stop words και εφαρμόζοντας lemmatization.
        """
        # Αφαίρεση ειδικών χαρακτήρων και περιττών κενών
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Διαχωρισμός σε tokens και επεξεργασία
        tokens = word_tokenize(text)
        return [
            self.lemmatizer.lemmatize(word.lower())
            for word in tokens
            if word.lower() not in self.stop_words
        ]

    def process_wikipedia_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Επεξεργάζεται τα δεδομένα της Wikipedia εφαρμόζοντας προεπεξεργασία
        σε όλες τις παραγράφους.
        """
        return {
            'title': data['title'],
            'paragraphs': [
                self.preprocess_text(paragraph)
                for paragraph in data['paragraphs']
            ]
        }

class DataStorage:
    """
    Διαχειρίζεται την αποθήκευση και φόρτωση των δεδομένων.
    """
    @staticmethod
    def save_to_json(data: Dict[str, Any], filename: str) -> None:
        """
        Αποθηκεύει δεδομένα σε αρχείο JSON, προσθέτοντάς τα αν το αρχείο υπάρχει.
        """
        try:
            # Φόρτωση υπαρχόντων δεδομένων ή δημιουργία κενής λίστας
            existing_data = []
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        pass

            # Προσθήκη νέων δεδομένων και αποθήκευση
            existing_data.append(data)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
                
            print(f"Τα δεδομένα αποθηκεύτηκαν επιτυχώς στο {filename}")
        except Exception as e:
            print(f"Σφάλμα κατά την αποθήκευση στο {filename}: {e}")


class InvertedIndex:
    def __init__(self):
        """
        Αρχικοποίηση του ανεστραμμένου ευρετηρίου.
        Δημιουργούμε ένα dictionary που θα αποθηκεύει για κάθε λέξη
        τα έγγραφα στα οποία εμφανίζεται και τη συχνότητά της.
        """
        self.index = {}  # το κυρίο ευρετηρίο
        self.documents = {}  # Αποθυκευσή εγγραφώ με τα IDs τους

    def load_processed_data(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            print(f"Τα δεδομένα φορτώθηκαν επιτυχώς από το {filename}")
        except Exception as e:
            print(f"Σφάλμα κατα την φορτώση αρχείου {filename} : {e}")

    def build_index(self) -> None:
            """
            Δημιουργία του ανεστραμμένου ευρετηρίου από τα επεξεργασμένα δεδομένα.
            Για κάθε λέξη, αποθηκεύουμε:
            - Σε ποια έγγραφα εμφανίζεται
            - Πόσες φορές εμφανίζεται σε κάθε έγγραφο
            """
            try:
                # Για κάθε έγγραφο στα δεδομένα μας
                for doc_id, doc_data in enumerate(self.documents):
                    # Παίρνουμε τον τίτλο και τις επεξεργασμένες παραγράφους
                    title = doc_data['title']
                    paragraphs = doc_data['paragraphs']

                    # Για κάθε παράγραφο στο έγγραφο
                    for paragraph in paragraphs:
                        for word in paragraph:
                            # Αν η λέξη δεν υπάρχει στο ευρετήριο, την προσθέτουμε
                            if word not in self.index:
                                self.index[word] = {
                                    'documents': {},  # Έγγραφα που περιέχουν τη λέξη
                                    'total_occurrences': 0  # Συνολικές εμφανίσεις
                                }

                            # Ενημερώνουμε τη συχνότητα για το συγκεκριμένο έγγραφο
                            if doc_id not in self.index[word]['documents']:
                                self.index[word]['documents'][doc_id] = {
                                    'count': 1,
                                    'title': title
                                }
                            else:
                                self.index[word]['documents'][doc_id]['count'] += 1

                            # Αυξάνουμε το συνολικό μετρητή εμφανίσεων
                            self.index[word]['total_occurrences'] += 1

                print("Το ανεστραμμένο ευρετήριο δημιουργήθηκε επιτυχώς!")


                # Προαιρετικά: Εκτύπωση στατιστικών
                print(f"Συνολικός αριθμός μοναδικών λέξεων: {len(self.index)}")
            except Exception as e:
                print(f"Σφάλμα κατά τη δημιουργία του ευρετηρίου: {e}")


    def get_format_for_term(self, term: str) -> Dict[str, Any]:
            """
            Επιστρέφει τα έγγραφα που περιέχουν τον συγκεκριμένο όρο.
            """
            return self.index.get(term, {})

    def display_index_stats(self, top_n:int = 5):
            """
            Εμφανίζει στατιστικά για το ευρετήριο.
            Args:
                top_n: Πόσες από τις πιο συχνές λέξεις να εμφανίσει
            """
            print("\n=== Στατιστικά Ευρετηρίου ===")
            print(f"Συνολικός αριθμός μοναδικών λέξεων: {len(self.index)}")

            sorted_words = sorted(
                self.index.items(),
                key= lambda x: x[1]['total_occurrences'],
                reverse=True
            )

            print(f"\nΟι {top_n} πιο συχνές λέξεις:")
            for word, data in sorted_words[:top_n]:
                print(f"'{word}': {data['total_occurrences']} εμφανίσεις σε {
                      len(data['documents'])} έγγραφα")
                # Εμφάνιση μερικών εγγράφων που περιέχουν τη λέξη
                print("Εμφανίζεται στα έγγραφα:")
                for doc_id, doc_info in list(data['documents'].items())[:3]:
                    print(f"  - {doc_info['title']
                          } ({doc_info['count']} φορές)")
                print()
        
        

def main():
    # Αρχικοποίηση των κλάσεων
    crawler = WikipediaCrawler()
    storage = DataStorage()
    
    # Λήψη θέματος από το χρήστη
    subject = input("Δώσε ένα θέμα: ")
    
    # Εξαγωγή περιεχομένου από Wikipedia
    raw_data = crawler.get_wikipedia_content(subject)
    if not raw_data:
        print("Αποτυχία λήψης περιεχομένου από τη Wikipedia. Παρακαλώ δοκιμάστε ξανά.")
        return
    
    # Αποθήκευση ακατέργαστων δεδομένων
    storage.save_to_json(
        raw_data,
        'webpage_data.json'
    )
    
    # Επεξεργασία και αποθήκευση επεξεργασμένων δεδομένων
    processed_data = crawler.process_wikipedia_data(raw_data)
    storage.save_to_json(
        processed_data,
        'processed_webpage_data.json'
    )

if __name__ == "__main__":
    main()