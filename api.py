from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from services.elasticIndexer import ElasticIndexer
from utils.sync import SyncManager

app = FastAPI()



class SearchResponse(BaseModel):
    results: list
    statusCode : int
@app.get("/search", response_model=SearchResponse)
def search(query: str = Query(..., description="Search query string")):
    try:
        sync_manager = SyncManager()
        sync_manager.sync()

        indexer = ElasticIndexer()
        indexer.refresh_index()
        results = indexer.search(query)


        if not results:
            return {"results": [""] , "statusCode" : 400}
        
        # Normalize results if needed
        if isinstance(results[0], dict):
            results = [r.get("file_path", str(r)) for r in results]
        print(results[0])
        return {"results": results,
                "statusCode" : 400}

    except Exception as e:
        return {"result" : "Unexpected Error oCCURED".format(e),
                "statusCode" : 400}