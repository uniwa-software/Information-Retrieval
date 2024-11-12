from project import  InvertedIndex
from searchEngine import SearchEngine
def main():
    
    inverted_index = InvertedIndex()
    inverted_index.load_processed_data('processed_webpage_data.json')
    inverted_index.build_index()
    
    search_engine = SearchEngine(inverted_index)
    search_engine.run()
    
    

if __name__ == "__main__":
    main()