import dropbox
from config import DROPBOX_ACCESS_TOKEN

class DropboxConnector:
    def __init__(self):
        self.dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

    def list_files(self, path=""):
        result = self.dbx.files_list_folder(path, recursive=True)
        files = []
        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(entry)
            if result.has_more:
                result = self.dbx.files_list_folder_continue(result.cursor)
            else:
                break
        return files

    def download_file(self, file_path, dest_path):
        with open(dest_path, "wb") as f:
            metadata, res = self.dbx.files_download(path=file_path)
            f.write(res.content)

    def list_file_ids(self):
        files = self.list_files()
        return {f.id: f for f in files}

    def get_shared_link(self, file_path):
        """Get or create a shared link for a file."""
        try:
            links = self.dbx.sharing_list_shared_links(path=file_path).links
            if links:
                return links[0].url.replace("?dl=0", "?dl=1")
            else:
                link = self.dbx.sharing_create_shared_link_with_settings(file_path)
                return link.url.replace("?dl=0", "?dl=1")
        except Exception as e:
            print(f"❌ Failed to get shared link for {file_path}: {e}")
            return ""

