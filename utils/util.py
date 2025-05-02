import os
import mimetypes
from config import TEMP_DIR

def get_file_extension(filename):
    return os.path.splitext(filename)[-1].lower()

def save_temp_file(file_metadata, dropbox_connector):
    file_path = os.path.join(TEMP_DIR, file_metadata.name)
    dropbox_connector.download_file(file_metadata.path_lower, file_path)
    return file_path
