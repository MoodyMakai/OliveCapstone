import os
from unittest.mock import patch

import anyio
import pytest

from src.storage import LocalFileStorage


class TestLocalFileStorageInit:
    def test_init_creates_new_directory(self, tmp_path):
        """INIT-01: Directory is created if it does not exist."""
        upload_dir = str(tmp_path / "new_uploads")
        LocalFileStorage(upload_dir)
        assert os.path.exists(upload_dir)

    def test_init_handles_existing_directory(self, temp_upload_dir):
        """INIT-02: No error is raised if the directory already exists."""
        os.makedirs(temp_upload_dir, exist_ok=True)
        storage = LocalFileStorage(temp_upload_dir)
        assert storage.upload_folder == temp_upload_dir

    @patch("src.storage.os.makedirs")
    def test_init_raises_and_logs_oserror(self, mock_makedirs, caplog, tmp_path):
        """INIT-Error: OSError is logged and raised on failure."""
        mock_makedirs.side_effect = OSError("Permission denied")
        with pytest.raises(OSError):
            LocalFileStorage(str(tmp_path / "bad_dir"))
        assert "Initialization error" in caplog.text


class TestLocalFileStorageSave:
    @pytest.mark.asyncio
    async def test_save_standard_file_stream(self, storage):
        """SAVE-01: File is created with correct data and extension."""
        data = b"test data"
        uri = await storage.save(data, "txt")

        # Resolve the local physical path for verification
        filename = os.path.basename(uri)
        local_path = anyio.Path(storage.upload_folder) / filename
        assert uri.endswith(".txt")
        assert uri.startswith("/images/")
        assert await local_path.exists()

        async with await anyio.open_file(str(local_path), "rb") as f:
            file_content = await f.read()
            assert file_content == data

    @pytest.mark.asyncio
    async def test_validate_uuid_uniqueness(self, storage):
        """SAVE-02: Two identical uploads get unique filenames."""
        data = b"same data"
        uri_1 = await storage.save(data, "png")
        uri_2 = await storage.save(data, "png")

        assert uri_1 != uri_2
        assert os.path.basename(uri_1) != os.path.basename(uri_2)

    @pytest.mark.asyncio
    async def test_save_empty_file_stream(self, storage):
        """SAVE-03: Can save an empty file stream successfully."""
        uri = await storage.save(b"", "txt")

        local_path = anyio.Path(storage.upload_folder) / os.path.basename(uri)
        assert await local_path.exists()

        stat = await local_path.stat()
        assert stat.st_size == 0


class TestLocalFileStorageDelete:
    @pytest.mark.asyncio
    async def test_delete_existing_file(self, storage):
        """DEL-01: Calling delete removes the file and returns True."""
        uri = await storage.save(b"data to delete", "txt")
        local_path = anyio.Path(storage.upload_folder) / os.path.basename(uri)
        assert await local_path.exists()

        result = await storage.delete(uri)
        assert result is True
        assert not await local_path.exists()

    @pytest.mark.asyncio
    async def test_delete_non_existent_file(self, storage):
        """DEL-02: Calling delete on a fake path returns True gracefully."""
        # Using anyio.Path to construct the fake path as well
        fake_path = anyio.Path(storage.upload_folder) / "fake_file.txt"
        result = await storage.delete(str(fake_path))
        assert result is True

    @pytest.mark.asyncio
    @patch("anyio.Path.exists", return_value=True)
    @patch("anyio.Path.unlink")
    async def test_delete_handles_oserror(self, mock_unlink, mock_exists, caplog, storage):
        """DEL-03: OSError during unlink logs error and returns False."""
        mock_unlink.side_effect = OSError("File locked")
        result = await storage.delete("dummy/path.txt")

        assert result is False
        assert "Disk error" in caplog.text
