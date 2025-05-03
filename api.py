from fastapi import FastAPI, Query
from pydantic import BaseModel
from services.elasticIndexer import ElasticIndexer
from utils.sync import SyncManager

app = FastAPI()

class SearchResponse(BaseModel):
    results: list
    statusCode: int

@app.get("/search", response_model=SearchResponse)
def search(query: str = Query(..., description="Search query string")):
    try:
        indexer = ElasticIndexer()
        sync_manager = SyncManager(indexer=indexer)
        if sync_manager.sync():
            indexer.refresh_index()
        results = indexer.search(query)

        if not results:
            return {"results": [], "statusCode": 204} 

        if isinstance(results[0], dict):
            results = [r if isinstance(r, dict) else {"file_path": r} for r in results]


        return {"results": results, "statusCode": 200}

    except Exception as e:
        return {
            "results": [f"Unexpected Error OCCURRED: {str(e)}"],
            "statusCode": 500
        }
