# Cloud File Content Search Service

## Project Description

This application enables near real-time searching of content within a connected Dropbox account. It downloads files, extracts text (including from PDFs, CSVs, and optionally images via OCR), indexes this content and metadata in Elasticsearch, and provides a simple API to search by keywords in file content or names.

---

## Features

- Connects to Dropbox for file retrieval.
- Extracts text from .txt, .jpeg, .png, .csv, and .pdf files.
- Indexes extracted text and file metadata in Elasticsearch for near real-time searching.
- Supports keyword/phrase search in file content and metadata.

---

## Architecture

![image](https://github.com/user-attachments/assets/e73b9c84-5616-47f8-a8c7-aa34113bc867)

The application consists of several key components:

1.  **Dropbox Connector (`src/connectors/dropbox_connector.py`):** Handles authentication and interaction with the Dropbox API (listing files, downloading files, getting shared links).
2.  **File Extractors (`src/extraction/extractors.py`):** Responsible for extracting text content from different file formats (TXT, PDF, CSV, Image.).
3.  **Elasticsearch Indexer (`src/indexing/elasticsearch_connector.py`):** Manages the connection to Elasticsearch, index creation, and adding/deleting/searching documents.
4.  **Sync Manager (`src/core/sync_manager.py`):** Orchestrates the synchronization process: fetching file lists from Dropbox and Elasticsearch, determining changes (new/deleted files *[Note: Update detection might require enhancement]*), triggering downloads, extractions, and indexing/deletion operations.
5.  **API (`src/api/main.py`):** A FastAPI application that exposes the `/search` endpoint, takes a query parameter, interacts with the Elasticsearch Indexer, and returns matching file results (name and shared link).

---

## Prerequisites

* **Elasticsearch:** A running instance (version 7.x or 8.x recommended). You can run it locally, via Docker, or use a cloud service.
    * [Elasticsearch Installation Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
* **Dropbox Account:** A Dropbox account with files you want to index.
* **Dropbox App:** You need to create a Dropbox App to obtain API credentials:
    1.  Go to the [Dropbox App Console](https://www.dropbox.com/developers/apps).
    2.  Choose "Dropbox API", "Full Dropbox" access (or "App Folder" if preferred, but adjust code accordingly).
    3.  Give your app a unique name.
    4.  Once created, go to the app's settings and generate an Access Token under the "OAuth 2" section. **Treat this token like a password!**
---

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    * Go to the config.py and set the configuration for the Elastic Search and Dropbox.

    ```dotenv
    # .env file
    DROPBOX_ACCESS_TOKEN="<your_dropbox_generated_access_token>"
    ELASTICSEARCH_HOST="http://localhost:9200" # Or your Elasticsearch host URL
    INDEX_NAME="dropbox_content_index"        # Or your desired index name
    
    ```
   

5.  **Ensure Elasticsearch is Running:** Verify that your Elasticsearch instance is up and accessible at the `ELASTICSEARCH_HOST` specified in your `config.py` file.



---

## Running the Application


 **Start the API Server:**
    * This server handles incoming search requests.
    ```bash
    # Run from the project root directory where venv is activated
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
    ```

---

## Usage

Once the API server is running and an initial sync has been completed, you can search for files using the `/search` endpoint.

* **Send a GET request:** Use `curl`, Postman, or a web browser.
* **Parameter:** `query` (the search term).

**Example using `curl`:**

* **Search for files containing "report":**
    ```bash
    curl "http://localhost:8000/search?query=report"
    ```
    * **Expected Output (Success):**
        ```json
        {
          "results": [
            {
              "file_name": "Q1_Financial_Report.pdf",
              "shared_link": "[https://www.dropbox.com/s/abc123xyz/Q1_Financial_Report.pdf?dl=1](https://www.dropbox.com/s/abc123xyz/Q1_Financial_Report.pdf?dl=1)"
            },
            {
              "file_name": "Project Status Report.txt",
              "shared_link": "[https://www.dropbox.com/s/def456uvw/Project](https://www.dropbox.com/s/def456uvw/Project) Status Report.txt?dl=1"
            }
          ]
        }
        ```

* **Search for a term not found:**
    ```bash
    curl "http://localhost:8000/search?query=nonexistentterm123"
    ```
    * **Expected Output (Empty):**
        ```json
        {
          "results": []
        }
        ```

*(Note: The `shared_link` provided is a direct download link)*

**File Deletion:** If you delete a file from Dropbox, it will be removed from the search results after the next successful run of the synchronization process.

---

## Project Structure (Example)
