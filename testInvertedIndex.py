from project import  InvertedIndex

def main():
    # Δημιουργία του ευρετηρίου
    inverted_index = InvertedIndex()
    
    # Φόρτωση των επεξεργασμένων δεδομένων
    inverted_index.load_processed_data('processed_webpage_data.json')
    
    # Δημιουργία του ευρετηρίου
    inverted_index.build_index()
    
    # Εμφάνιση στατιστικών
    inverted_index.display_index_stats(top_n=5)

if __name__ == "__main__":
    main()