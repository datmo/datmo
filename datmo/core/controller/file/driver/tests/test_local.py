"""
Tests for local.py
"""

import os
import shutil
import tempfile
import platform
from io import TextIOWrapper
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.util.misc_functions import get_datmo_temp_path
from datmo.core.controller.file.driver.local import LocalFileDriver
from datmo.core.util.exceptions import PathDoesNotExist
from datmo.config import Config

class TestLocalFileDriver():
    # TODO: Add more cases for each test
    """
    Checks all functions of the LocalFileDriver
    """

    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.local_file_driver = LocalFileDriver(
            root=self.temp_dir, datmo_directory_name=".datmo")

    def teardown_method(self):
        pass

    def test_initialize(self):
        assert self.local_file_driver != None

    # Static Method Tests

    def test_get_safe_dst_filepath(self):
        # Create first file to copy
        relative_filepath = "test.json"
        self.local_file_driver.create(relative_filepath)
        # Create destination directory
        relative_dirpath = "dest"
        self.local_file_driver.create(relative_dirpath, directory=True)
        # Create file within destination directory
        relative_filename_2 = os.path.join(relative_dirpath, "test.json")
        self.local_file_driver.create(relative_filename_2)

        filepath = os.path.join(self.local_file_driver.root, relative_filepath)
        dirpath = os.path.join(self.local_file_driver.root, relative_dirpath)
        result = self.local_file_driver.\
            get_safe_dst_filepath(filepath, dirpath)
        assert result == os.path.join(dirpath, "test_0.json")

    def test_copytree(self):
        # Create source directory
        relative_src_dirpath = "src"
        self.local_file_driver.create(relative_src_dirpath, directory=True)
        relative_src_filepath = os.path.join(relative_src_dirpath, "test.json")
        self.local_file_driver.create(relative_src_filepath)
        # Create destination directory
        relative_dst_dirpath = "dst"
        self.local_file_driver.create(relative_dst_dirpath, directory=True)
        # Copy source directory to destination
        src_dirpath = os.path.join(self.local_file_driver.root,
                                   relative_src_dirpath)
        src_dishash = self.local_file_driver.get_dirhash(src_dirpath)
        assert src_dishash == "74be16979710d4c4e7c6647856088456"
        dst_dirpath = os.path.join(self.local_file_driver.root,
                                   relative_dst_dirpath)
        self.local_file_driver.copytree(src_dirpath, dst_dirpath)
        dst_dirhash = self.local_file_driver.get_dirhash(dst_dirpath)
        assert dst_dirhash == "74be16979710d4c4e7c6647856088456"
        dst_filepath = os.path.join(dst_dirpath, "test.json")
        assert os.path.isdir(os.path.join(dst_dirpath)) and \
            os.path.isfile(dst_filepath) == True

    def test_copyfile(self):
        # Create first file to copy
        relative_filepath = "test.json"
        self.local_file_driver.create(relative_filepath)
        # Create destination directory
        relative_dst_dirpath = "dest"
        self.local_file_driver.create(relative_dst_dirpath, directory=True)
        # Copy file to destination
        filepath = os.path.join(self.local_file_driver.root, relative_filepath)
        dst_dirpath = os.path.join(self.local_file_driver.root,
                                   relative_dst_dirpath)
        self.local_file_driver.copyfile(filepath, dst_dirpath)
        assert os.path.isfile(os.path.join(dst_dirpath, relative_filepath))

    # Property Method Test
    def test_is_initialized(self):
        self.local_file_driver.init()
        assert self.local_file_driver.is_initialized == True

    # Instance Method Tests
    def test_init(self):
        result = self.local_file_driver.init()
        assert result and \
               self.local_file_driver.is_initialized

    def test_create(self):
        temp_relative_filepath = "test.json"
        temp_filepath = self.local_file_driver.create(temp_relative_filepath)
        assert os.path.isfile(temp_filepath) == True

    def test_exists(self):
        temp_relative_filepath = "test.json"
        result = self.local_file_driver.exists(temp_relative_filepath)
        assert result == False
        self.local_file_driver.create(temp_relative_filepath)
        result = self.local_file_driver.exists(temp_relative_filepath)
        assert result == True

    def test_get(self):
        # Test failure
        temp_relative_filepath = "test.json"
        failed = False
        try:
            self.local_file_driver.get(temp_relative_filepath)
        except PathDoesNotExist:
            failed = True
        assert failed
        # Test success with default mode
        self.local_file_driver.create(temp_relative_filepath)
        result = self.local_file_driver.get(temp_relative_filepath)
        assert isinstance(result, TextIOWrapper)
        # Test success with default mode and directory=True

        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create(os.path.join("dirpath1", "filepath1"))

        # Absolute file paths after added to collection (to test)
        filepath1 = os.path.join(self.local_file_driver.root, "dirpath1",
                                 "filepath1")
        result = self.local_file_driver.get(
            os.path.join("dirpath1"), directory=True)

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper) and \
            result[0].name == filepath1

    def test_ensure(self):
        temp_relative_filepath = "test.json"
        self.local_file_driver.ensure(temp_relative_filepath)
        assert os.path.isfile(
            os.path.join(self.local_file_driver.root,
                         temp_relative_filepath)) == True

    def test_delete(self):
        temp_relative_filepath = "test.json"
        self.local_file_driver.create(temp_relative_filepath)
        filepath = os.path.join(self.local_file_driver.root,
                                temp_relative_filepath)
        assert os.path.exists(filepath) == True
        self.local_file_driver.delete(temp_relative_filepath)
        assert os.path.exists(filepath) == False

    # Hidden .datmo directory tests
    def test_create_hidden_datmo_dir(self):
        result = self.local_file_driver.create_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(self.local_file_driver.datmo_directory)

    def test_exists_hidden_datmo_dir(self):
        result = self.local_file_driver.exists_hidden_datmo_dir()
        assert result == False
        self.local_file_driver.create_hidden_datmo_dir()
        result = self.local_file_driver.exists_hidden_datmo_dir()
        assert result == True

    def test_ensure_hidden_datmo_dir(self):
        result = self.local_file_driver.ensure_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(self.local_file_driver.datmo_directory)

    def test_delete_hidden_datmo_dir(self):
        self.local_file_driver.create_hidden_datmo_dir()
        result = self.local_file_driver.delete_hidden_datmo_dir()
        assert result == True and \
               not os.path.isdir(self.local_file_driver.datmo_directory)

    # Template tests

    # TODO : Add tests for code that handles various project templates

    # Files directory tests
    def test_create_files_dir(self):
        files_path = os.path.join(self.local_file_driver.datmo_directory,
                                  "files")
        thrown = False
        try:
            self.local_file_driver.create_files_dir()
        except Exception:
            thrown = True
        assert thrown == True and \
            not os.path.isdir(files_path)
        self.local_file_driver.init()
        result = self.local_file_driver.create_files_dir()
        assert result == True and \
            os.path.isdir(files_path)

    def test_exists_files_dir(self):
        files_path = os.path.join(self.local_file_driver.datmo_directory,
                                  "files")
        result = self.local_file_driver.exists_files_dir()
        assert result == False and \
            not os.path.isdir(files_path)
        self.local_file_driver.init()
        self.local_file_driver.create_files_dir()
        result = self.local_file_driver.exists_files_dir()
        assert result == True and \
            os.path.isdir(files_path)

    def test_ensure_files_dir(self):
        files_path = os.path.join(self.local_file_driver.datmo_directory,
                                  "files")
        result = self.local_file_driver.ensure_files_dir()
        assert result == True and \
            os.path.isdir(files_path)

    def test_delete_files_dir(self):
        files_path = os.path.join(self.local_file_driver.datmo_directory,
                                  "files")
        self.local_file_driver.init()
        self.local_file_driver.create_files_dir()
        result = self.local_file_driver.delete_files_dir()
        assert result == True and \
            not os.path.isdir(files_path)

    # Collection directory tests
    def test_create_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.datmo_directory,
                                        "collections")
        thrown = False
        try:
            self.local_file_driver.create_collections_dir()
        except Exception:
            thrown = True
        assert thrown == True and \
            not os.path.isdir(collections_path)
        self.local_file_driver.init()
        result = self.local_file_driver.create_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_exists_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.datmo_directory,
                                        "collections")
        result = self.local_file_driver.exists_collections_dir()
        assert result == False and \
            not os.path.isdir(collections_path)
        self.local_file_driver.init()
        self.local_file_driver.create_collections_dir()
        result = self.local_file_driver.exists_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_ensure_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.datmo_directory,
                                        "collections")
        result = self.local_file_driver.ensure_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_delete_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.datmo_directory,
                                        "collections")
        self.local_file_driver.init()
        self.local_file_driver.create_collections_dir()
        result = self.local_file_driver.delete_collections_dir()
        assert result == True and \
            not os.path.isdir(collections_path)

    # .datmo directory structure tests
    def test_create_hidden_datmo_file_structure(self):
        result = self.local_file_driver.create_hidden_datmo_file_structure()
        assert result == True and \
               os.path.isdir(self.local_file_driver.datmo_directory)

    def test_exists_hidden_datmo_file_structure(self):
        result = self.local_file_driver.exists_hidden_datmo_file_structure()
        assert result == False
        self.local_file_driver.ensure_hidden_datmo_file_structure()
        result = self.local_file_driver.exists_hidden_datmo_file_structure()
        assert result == True

    def test_ensure_hidden_datmo_file_structure(self):
        result = self.local_file_driver.ensure_hidden_datmo_file_structure()
        assert result == True and \
               os.path.isdir(self.local_file_driver.datmo_directory)

    def test_delete_hidden_datmo_file_structure(self):
        self.local_file_driver.create_hidden_datmo_file_structure()
        result = self.local_file_driver.delete_hidden_datmo_file_structure()
        assert result == True and \
            not os.path.isdir(self.local_file_driver.datmo_directory)

    # Other functions for collections
    def test_create_collection(self):
        self.local_file_driver.init()
        collections_path = os.path.join(self.local_file_driver.datmo_directory,
                                        "collections")

        # Test empty file collection already exists
        filehash_empty, _, _ = self.local_file_driver. \
            create_collection([])
        collection_path_empty = os.path.join(collections_path, filehash_empty)

        assert os.path.isdir(collection_path_empty)
        assert len(os.listdir(collections_path)) == 1

        # Test creating another empty file collection (should not fail again)
        filehash_empty, _, _ = self.local_file_driver. \
            create_collection([])
        collection_path_empty = os.path.join(collections_path, filehash_empty)

        assert os.path.isdir(collection_path_empty)
        assert len(os.listdir(collections_path)) == 1

        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create("filepath1")

        dirpath1 = os.path.join(self.local_file_driver.root, "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.root, "dirpath2")
        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")
        filehash, _, _ = self.local_file_driver.\
            create_collection([dirpath1, dirpath2, filepath1])
        collection_path = os.path.join(collections_path, filehash)

        assert os.path.isdir(collection_path)
        assert len(os.listdir(collections_path)) == 2
        # Run these for all platforms
        assert os.path.isdir(os.path.join(collection_path, "dirpath1"))
        assert os.path.isdir(os.path.join(collection_path, "dirpath2"))
        assert os.path.isfile(os.path.join(collection_path, "filepath1"))

        # Only assume success for non-Windows platforms
        if not platform.system() == "Windows":
            assert (oct(
                os.stat(os.path.join(collection_path, "dirpath1")).st_mode &
                0o777) == '0o755' or oct(
                    os.stat(os.path.join(collection_path, "dirpath1")).st_mode
                    & 0o777) == '0755')
            assert (oct(
                os.stat(os.path.join(collection_path, "dirpath2")).st_mode &
                0o777) == '0o755' or oct(
                    os.stat(os.path.join(collection_path, "dirpath2")).st_mode
                    & 0o777) == '0755')
            assert (oct(
                os.stat(os.path.join(collection_path, "filepath1")).st_mode &
                0o777) == '0o755' or oct(
                    os.stat(os.path.join(collection_path, "filepath1")).st_mode
                    & 0o777) == '0755')
        # TODO: Create test for Windows platform
        # else:
        #     assert (oct(
        #         os.stat(os.path.join(collection_path, "dirpath1")).st_mode &
        #         0o777) == '0o777' or oct(
        #             os.stat(os.path.join(collection_path, "dirpath1")).st_mode
        #             & 0o777) == '0777')
        #     assert (oct(
        #         os.stat(os.path.join(collection_path, "dirpath2")).st_mode &
        #         0o777) == '0o777' or oct(
        #             os.stat(os.path.join(collection_path, "dirpath2")).st_mode
        #             & 0o777) == '0777')
        #     assert (oct(
        #         os.stat(os.path.join(collection_path, "filepath1")).st_mode &
        #         0o777) == '0o777' or oct(
        #             os.stat(os.path.join(collection_path, "filepath1")).st_mode
        #             & 0o777) == '0777')

        self.local_file_driver.delete_collection(filehash)

    def test_calculate_hash_paths_simple(self):
        self.local_file_driver.init()

        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create("filepath1")
        self.local_file_driver.create("filepath2")

        dirpath1 = os.path.join(self.local_file_driver.root, "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.root, "dirpath2")
        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")
        filepath2 = os.path.join(self.local_file_driver.root, "filepath2")

        # check with just 1 blank filepath
        paths = [filepath1]
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        assert result == "74be16979710d4c4e7c6647856088456"
        shutil.rmtree(temp_dir)

        # check with 1 empty directory and 1 blank filepath (empty directories do NOT change hash)
        paths = [filepath1, dirpath1]
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        assert result == "74be16979710d4c4e7c6647856088456"
        shutil.rmtree(temp_dir)

        # check with 2 empty directories and 1 blank filepath (empty directories do NOT change hash)
        paths = [filepath1, dirpath1, dirpath2]
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        assert result == "74be16979710d4c4e7c6647856088456"
        shutil.rmtree(temp_dir)

        # check 2 blank filepaths (should be different)
        paths = [filepath1, filepath2]
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        assert result == "020eb29b524d7ba672d9d48bc72db455"
        shutil.rmtree(temp_dir)

        # check 1 blank filepath with a different name (same because name not factored into hash)
        paths = [filepath2]
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        assert result == "74be16979710d4c4e7c6647856088456"
        shutil.rmtree(temp_dir)

    def test_calculate_hash_paths_single_line(self):
        self.local_file_driver.init()

        # Create test directories to move
        self.local_file_driver.create("filepath1")

        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")

        paths = [filepath1]

        # Add contents to the file in python and verify hash
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        with open(filepath1, "wb") as f:
            f.write(to_bytes("hello\n"))
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        shutil.rmtree(temp_dir)
        assert result == "57ae7aad8abe2f317e460c92d3ed1178"

    def test_calculate_hash_paths_multiple_lines(self):
        self.local_file_driver.init()

        # Create test directories to move
        self.local_file_driver.create("filepath1")

        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")

        paths = [filepath1]

        # Add contents to the file in python and verify hash
        temp_dir = get_datmo_temp_path(self.local_file_driver.root)
        with open(filepath1, "wb") as f:
            f.write(to_bytes("FROM something:something\n"))
            f.write(to_bytes("test multiple lines\n"))
        result = self.local_file_driver.calculate_hash_paths(paths, temp_dir)
        shutil.rmtree(temp_dir)
        assert result == "a14de65c0fc13bc50cb246cc518195af"

    def test_get_filehash(self):
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, "wb") as f:
            f.write(to_bytes("hello\n"))
        result = self.local_file_driver.get_filehash(filepath)
        assert len(result) == 32
        assert result == "b1946ac92492d2347c6235b4d2611184"

    def test_get_dirhash(self):
        temp_dir_1 = get_datmo_temp_path(self.temp_dir)
        filepath = os.path.join(temp_dir_1, "test.txt")
        with open(filepath, "wb") as f:
            f.write(to_bytes("hello\n"))
        result = self.local_file_driver.get_dirhash(temp_dir_1)
        assert result == "57ae7aad8abe2f317e460c92d3ed1178"
        temp_dir_2 = get_datmo_temp_path(self.temp_dir)
        filepath_2 = os.path.join(temp_dir_2, "test.txt")
        with open(filepath_2, "wb") as f:
            f.write(to_bytes("hello\n"))
        result_2 = self.local_file_driver.get_dirhash(temp_dir_2)
        assert result == result_2

    def test_get_absolute_collection_path(self):
        self.local_file_driver.init()
        filehash, _, _ = self.local_file_driver. \
            create_collection([])
        collection_path = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash)
        returned_collection_path = self.local_file_driver.\
            get_absolute_collection_path(filehash)
        assert returned_collection_path == collection_path

    def test_get_relative_collection_path(self):
        self.local_file_driver.init()
        filehash, _, _ = self.local_file_driver. \
            create_collection([])
        relative_collection_path = os.path.join(
            self.local_file_driver.datmo_directory_name, "collections",
            filehash)
        returned_relative_collection_path = self.local_file_driver.\
            get_relative_collection_path(filehash)
        assert returned_relative_collection_path == relative_collection_path

    def test_exists_collection(self):
        self.local_file_driver.init()
        filehash, _, _ = self.local_file_driver.create_collection([])
        collection_path = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash)
        result = self.local_file_driver.exists_collection(filehash)
        assert result == True and \
            os.path.isdir(collection_path)

    def test_get_collection_files(self):
        self.local_file_driver.init()
        # Test empty file collection default mode
        filehash_empty, _, _ = self.local_file_driver. \
            create_collection([])
        result = self.local_file_driver.get_collection_files(filehash_empty)
        assert not result

        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create(os.path.join("dirpath1", "filepath1"))
        self.local_file_driver.create(os.path.join("dirpath2", "filepath2"))
        self.local_file_driver.create("filepath3")

        # Absolute file paths to add to collection
        dirpath1 = os.path.join(self.local_file_driver.root, "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.root, "dirpath2")
        filepath3 = os.path.join(self.local_file_driver.root, "filepath3")

        filehash, _, _ = self.local_file_driver. \
            create_collection([dirpath1, dirpath2, filepath3])

        # Absolute file paths after added to collection (to test)
        filepath1_after = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash, "dirpath1",
                                       "filepath1")
        filepath2_after = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash, "dirpath2",
                                       "filepath2")
        filepath3_after = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash, "filepath3")
        paths_list = [filepath1_after, filepath2_after, filepath3_after]
        result = self.local_file_driver.get_collection_files(filehash)

        assert len(result) == 3
        assert isinstance(result[0], TextIOWrapper) and \
               result[0].name in paths_list
        assert isinstance(result[1], TextIOWrapper) and \
               result[1].name in paths_list
        assert isinstance(result[2], TextIOWrapper) and \
               result[2].name in paths_list

    def test_delete_collection(self):
        self.local_file_driver.init()
        filehash, _, _ = self.local_file_driver.create_collection([])
        collection_path = os.path.join(self.local_file_driver.datmo_directory,
                                       "collections", filehash)
        result = self.local_file_driver.delete_collection(filehash)
        assert result == True and \
            not os.path.isdir(collection_path)

    def test_list_file_collections(self):
        self.local_file_driver.init()
        filehash_1, _, _ = self.local_file_driver.create_collection([])
        self.local_file_driver.create("filepath1")
        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")
        filehash_2, _, _ = self.local_file_driver.create_collection(
            [filepath1])
        collection_list = self.local_file_driver.list_file_collections()
        assert filehash_1 in collection_list and \
               filehash_2 in collection_list

    def test_transfer_collection(self):
        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create("filepath1")

        dirpath1 = os.path.join(self.local_file_driver.root, "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.root, "dirpath2")
        filepath1 = os.path.join(self.local_file_driver.root, "filepath1")
        self.local_file_driver.init()
        filehash, _, _ = self.local_file_driver. \
            create_collection([dirpath1, dirpath2, filepath1])
        dst_dirpath = os.path.join(self.temp_dir, "new_dir")
        self.local_file_driver.create(dst_dirpath, directory=True)
        result = self.local_file_driver.transfer_collection(
            filehash, dst_dirpath)
        assert result == True and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath1")) and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath2")) and \
               os.path.isfile(os.path.join(dst_dirpath,
                                           "filepath1"))
