import os
from services.dropboxConnector import DropboxConnector
from utils.extractors import TxtExtractor, PdfExtractor, CsvExtractor ,PngExtractor
from services.elasticIndexer import ElasticIndexer
from utils.util import get_file_extension, save_temp_file
from config import TEMP_DIR

EXTRACTOR_MAP = {
    ".txt": TxtExtractor(),
    ".csv": CsvExtractor(),
    ".pdf": PdfExtractor(),
    ".png" : PngExtractor() ,
    ".jpg" : PngExtractor()
}

class SyncManager:
    def __init__(self, connector=None, indexer=None):
        self.connector = connector or DropboxConnector()
        self.indexer = indexer or ElasticIndexer()
        os.makedirs(TEMP_DIR, exist_ok=True)
        
    def sync(self):
        print("🔄 Syncing Dropbox with Elasticsearch...")
        
        
        dropbox_files = self.connector.list_files()
        indexed_ids = self.indexer.list_indexed_ids()
        dropbox_file_map = {f.id: f for f in dropbox_files}
        dropbox_ids = set(dropbox_file_map.keys())

        if dropbox_ids == indexed_ids:
            print("✅ Already in sync.")
            return 0
            
        self.indexer.create_index()
        # Index new or updated files
        for file_id in dropbox_ids - indexed_ids:
            f = dropbox_file_map[file_id]
            ext = get_file_extension(f.name)
            extractor = EXTRACTOR_MAP.get(ext)
            if not extractor:
                print(f"⚠️ Skipping unsupported file: {f.name}")
                continue

            try:
                temp_path = save_temp_file(f, self.connector)
                content = extractor.extract(temp_path)
                os.remove(temp_path)
                shared_link = self.connector.get_shared_link(f.path_lower)

                metadata = {
                    "path": f.path_lower,
                    "file_name": f.name,
                    "shared_link": shared_link
                }

                self.indexer.index_document(doc_id=f.id, content=content, metadata=metadata)
                print(f"✅ Indexed: {f.name} → {shared_link}")

            except Exception as e:
                print(f"❌ Failed to index {f.name}: {e}")

        # Delete removed files from index
        for doc_id in indexed_ids - dropbox_ids:
            self.indexer.delete_document(doc_id)
            print(f"🗑️ Removed from index: {doc_id}")
            
       	print("refressing Index") 
        self.indexer.refresh_index()

# if __name__ == "__main__":
#     sync = SyncManager()
#     sync.sync()
