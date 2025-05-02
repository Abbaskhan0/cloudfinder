from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, BadRequestError
from config import ELASTICSEARCH_HOST, INDEX_NAME

class ElasticIndexer:
    def __init__(self):
        self.client = Elasticsearch(ELASTICSEARCH_HOST, verify_certs=False)

    def create_index(self):
        try:
            if not self.client.indices.exists(index=INDEX_NAME):
                self.client.indices.create(index=INDEX_NAME)
        except BadRequestError as e:
            print(f"Elasticsearch BadRequestError: {e.info}")
        except Exception as e:
            print(f"Unexpected error while creating index: {e}")

    def index_document(self, doc_id, content, metadata):
        self.client.index(index=INDEX_NAME, id=doc_id, document={
            "content": content,
            "file_name": metadata.get("file_name", ""),
            "file_path": metadata.get("path", ""),
            "shared_link": metadata.get("shared_link", "")
        })

    def delete_document(self, doc_id):
        try:
            self.client.delete(index=INDEX_NAME, id=doc_id)
        except NotFoundError:
            pass

    def search(self, query):
        res = self.client.search(index=INDEX_NAME, query={
            "bool": {  # Use a boolean query for more control
                "should": [ #should gives the flexibility to search in multiple fields
                    {
                        "match_phrase": {  # Use match_phrase for exact matching
                            "content": query
                        }
                    },
                    {
                        "match_phrase": {
                            "file_name": query
                        }
                    },
                    {
                        "match_phrase": {
                            "file_path": query
                        }
                    }
                ]
            }
        })
        return [
            {
                "file_name": hit["_source"].get("file_name", ""),
                "shared_link": hit["_source"].get("shared_link", "")
            }
            for hit in res["hits"]["hits"]
        ]

    def refresh_index(self):
        self.client.indices.refresh(index=INDEX_NAME)

    def list_indexed_ids(self):
        result = self.client.search(index=INDEX_NAME, body={"query": {"match_all": {}}}, size=1000)
        return set(hit["_id"] for hit in result["hits"]["hits"])

