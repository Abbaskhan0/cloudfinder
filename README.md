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

*(Placeholder: Insert a high-level design diagram image here or provide a link. The diagram should show the relationship between the User, API, Sync Process, Dropbox, Extractors, and Elasticsearch.)*

The application consists of several key components:

1.  **Dropbox Connector (`src/connectors/dropbox_connector.py`):** Handles authentication and interaction with the Dropbox API (listing files, downloading files, getting shared links).
2.  **File Extractors (`src/extraction/extractors.py`):** Responsible for extracting text content from different file formats (TXT, PDF, CSV, etc.). Uses a base class and specific implementations for each type.
3.  **Elasticsearch Indexer (`src/indexing/elasticsearch_connector.py`):** Manages the connection to Elasticsearch, index creation, and adding/deleting/searching documents.
4.  **Sync Manager (`src/core/sync_manager.py`):** Orchestrates the synchronization process: fetching file lists from Dropbox and Elasticsearch, determining changes (new/deleted files *[Note: Update detection might require enhancement]*), triggering downloads, extractions, and indexing/deletion operations.
5.  **API (`src/api/main.py`):** A FastAPI application that exposes the `/search` endpoint, takes a query parameter, interacts with the Elasticsearch Indexer, and returns matching file results (name and shared link).
6.  **Configuration (`src/config.py`):** Manages application settings, primarily loading sensitive credentials and parameters from environment variables.

---

## Prerequisites

* **Python:** Version 3.8+ recommended.
* **Pip:** Python package installer (usually comes with Python).
* **Git:** For cloning the repository.
* **Elasticsearch:** A running instance (version 7.x or 8.x recommended). You can run it locally, via Docker, or use a cloud service.
    * [Elasticsearch Installation Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
    * [Run Elasticsearch with Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
* **Dropbox Account:** A Dropbox account with files you want to index.
* **Dropbox App:** You need to create a Dropbox App to obtain API credentials:
    1.  Go to the [Dropbox App Console](https://www.dropbox.com/developers/apps).
    2.  Choose "Dropbox API", "Full Dropbox" access (or "App Folder" if preferred, but adjust code accordingly).
    3.  Give your app a unique name.
    4.  Once created, go to the app's settings and generate an Access Token under the "OAuth 2" section. **Treat this token like a password!**
* **(Optional) Tesseract OCR:** Required *only* if you enable `.png` or other image format extraction.
    * [Tesseract Installation Guide](https://github.com/tesseract-ocr/tesseract/wiki#installation)
    * Ensure the `tesseract` command is in your system's PATH.
* **(Optional) Apache Tika:** Required *only* if using the Tika extractor (for broader file support and robust encoding detection).
    * Requires Java Runtime Environment (JRE).
    * [Apache Tika Setup](https://tika.apache.org/download.html) (Often used via the `tika-python` library which can start a Tika server).

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
    *(Note: Ensure `requirements.txt` includes `fastapi`, `uvicorn`, `dropbox`, `elasticsearch`, `PyPDF2`, `python-dotenv`, and optional dependencies like `pytesseract`, `Pillow`, `tika-python` if used.)*

4.  **Configure Environment Variables:**
    * Create a file named `.env` in the project root directory.
    * Copy the contents of `.env.example` (you should create this file) into `.env`.
    * Edit the `.env` file with your actual credentials:

    ```dotenv
    # .env file
    DROPBOX_ACCESS_TOKEN="<your_dropbox_generated_access_token>"
    ELASTICSEARCH_HOST="http://localhost:9200" # Or your Elasticsearch host URL
    INDEX_NAME="dropbox_content_index"        # Or your desired index name
    # Add other configurations like TEMP_DIR if needed
    ```
    *(Note: Add `.env` to your `.gitignore` file to avoid committing secrets!)*

5.  **Ensure Elasticsearch is Running:** Verify that your Elasticsearch instance is up and accessible at the `ELASTICSEARCH_HOST` specified in your `.env` file.

6.  **(Optional) Install Tesseract/Tika:** Follow the instructions linked in Prerequisites if you need support for image or extended file formats.

---

## Running the Application

There are two main parts: the synchronization process and the API server.

1.  **Run the Synchronization Process:**
    * This process connects to Dropbox, checks for new/deleted files, extracts content, and updates Elasticsearch.
    * It's recommended to run this periodically (e.g., via cron or a scheduler) or manually when needed.
    ```bash
    # Example: Assuming you have a script src/run_sync.py
    python src/run_sync.py
    ```
    * *(Note: You need to create this entry point script or detail how to trigger the `SyncManager().sync()` method)*
    * The first sync might take a while depending on the number and size of files. Subsequent syncs should be faster if update detection is implemented.

2.  **Start the API Server:**
    * This server handles incoming search requests.
    ```bash
    # Run from the project root directory where venv is activated
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
    ```
    * `--reload`: Enables auto-reloading for development (remove for production).
    * `--host 0.0.0.0`: Makes the server accessible on your network.
    * `--port 8000`: Specifies the port number.
    * The API server will be available at `http://localhost:8000` (or your machine's IP address).

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
