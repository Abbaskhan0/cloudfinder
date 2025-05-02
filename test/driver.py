from elasticIndexer import ElasticIndexer
from sync import SyncManager
def test_search():
    indexer = ElasticIndexer()
    manager_to_sync = SyncManager()
    manager_to_sync.sync()
    query = input("Enter search query: ").strip()
    if not query:
        print("Query cannot be empty.")
        return

    results = indexer.search(query)
    print("Raw Results:", results)  # Debug output

    if results:
        print("Search Results:")
        for result in results:
            print(f"- {result}")  # If it's a string (file path)
            # Or if it's a dict, use this:
            # print(f"- {result['file_path']}")
    else:
        print("No matching documents found.")

if __name__ == "__main__":
    test_search()
