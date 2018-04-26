"""
Tests for local.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile
from io import TextIOWrapper

from datmo.core.controller.file.driver.local import LocalFileDriver
from datmo.core.util.exceptions import DoesNotExistException


class TestLocalFileManager():
    # TODO: Add more cases for each test
    """
    Checks all functions of the LocalFileDriver
    """
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.local_file_driver = LocalFileDriver(filepath=self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

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

        filepath = os.path.join(self.local_file_driver.filepath,
                                relative_filepath)
        dirpath = os.path.join(self.local_file_driver.filepath,
                               relative_dirpath)
        result = self.local_file_driver.\
            get_safe_dst_filepath(filepath, dirpath)
        assert result == os.path.join(dirpath, "test_0.json")

    def test_copytree(self):
        # Create source directory
        relative_src_dirpath = "core"
        self.local_file_driver.create(relative_src_dirpath, directory=True)
        relative_src_filepath = os.path.join(relative_src_dirpath, "test.json")
        self.local_file_driver.create(relative_src_filepath)
        # Create destination directory
        relative_dst_dirpath = "dst"
        self.local_file_driver.create(relative_dst_dirpath, directory=True)
        # Copy source directory to destination
        src_dirpath = os.path.join(self.local_file_driver.filepath,
                                   relative_src_dirpath)
        dst_dirpath = os.path.join(self.local_file_driver.filepath,
                                   relative_dst_dirpath)
        self.local_file_driver.copytree(src_dirpath, dst_dirpath)
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
        filepath = os.path.join(self.local_file_driver.filepath,
                                relative_filepath)
        dst_dirpath = os.path.join(self.local_file_driver.filepath,
                                   relative_dst_dirpath)
        self.local_file_driver.copyfile(filepath, dst_dirpath)
        assert os.path.isfile(os.path.join(dst_dirpath, relative_filepath)) == True

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
        except DoesNotExistException:
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
        filepath1 = os.path.join(self.local_file_driver.filepath,
                                 "dirpath1", "filepath1")
        result = self.local_file_driver.get(os.path.join("dirpath1"), directory=True)

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper) and \
            result[0].name == filepath1

    def test_ensure(self):
        temp_relative_filepath = "test.json"
        self.local_file_driver.ensure(temp_relative_filepath)
        assert os.path.isfile(
            os.path.join(self.local_file_driver.filepath,
                         temp_relative_filepath)
        ) == True

    def test_delete(self):
        temp_relative_filepath = "test.json"
        self.local_file_driver.create(temp_relative_filepath)
        filepath = os.path.join(self.local_file_driver.filepath,
                         temp_relative_filepath)
        assert os.path.exists(filepath) == True
        self.local_file_driver.delete(temp_relative_filepath)
        assert os.path.exists(filepath) == False

    def test_create_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_driver.filepath,
                                ".datmo")
        result = self.local_file_driver.create_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(filepath)

    def test_exists_hidden_datmo_dir(self):
        result = self.local_file_driver.exists_hidden_datmo_dir()
        assert result == False
        self.local_file_driver.create_hidden_datmo_dir()
        result = self.local_file_driver.exists_hidden_datmo_dir()
        assert result == True

    def test_ensure_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_driver.filepath,
                                ".datmo")
        result = self.local_file_driver.ensure_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(filepath)

    def test_delete_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_driver.filepath,
                                ".datmo")
        self.local_file_driver.create_hidden_datmo_dir()
        result = self.local_file_driver.delete_hidden_datmo_dir()
        assert result == True and \
               not os.path.isdir(filepath)

    def test_create_datmo_file_structure(self):
        filepath = os.path.join(self.local_file_driver.filepath,
                                ".datmo")
        result = self.local_file_driver.create_datmo_file_structure()
        assert result == True and \
               os.path.isdir(filepath)

    def test_exists_datmo_file_structure(self):
        result = self.local_file_driver.exists_datmo_file_structure()
        assert result == False
        self.local_file_driver.ensure_datmo_file_structure()
        result = self.local_file_driver.exists_datmo_file_structure()
        assert result == True

    def test_ensure_datmo_file_structure(self):
        hidden_datmo_dir_filepath = os.path.join(self.local_file_driver.filepath,
                                ".datmo")
        result = self.local_file_driver.ensure_datmo_file_structure()
        assert result == True and \
               os.path.isdir(hidden_datmo_dir_filepath)

    def test_delete_datmo_file_structure(self):
        hidden_datmo_dir_filepath = os.path.join(self.local_file_driver.filepath,
                                                 ".datmo")
        self.local_file_driver.create_datmo_file_structure()
        result = self.local_file_driver.delete_datmo_file_structure()
        assert result == True and \
            not os.path.isdir(hidden_datmo_dir_filepath)

    # Template tests

    # TODO : Add tests for code that handles various project templates

    # Collection Tests
    def test_create_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.filepath,
                                        ".datmo", "collections")
        thrown = False
        try:
            self.local_file_driver.create_collections_dir()
        except:
            thrown = True
        assert thrown == True and \
            not os.path.isdir(collections_path)
        self.local_file_driver.init()
        result = self.local_file_driver.create_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_exists_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.filepath,
                                        ".datmo", "collections")
        result = self.local_file_driver.exists_collections_dir()
        assert result == False and \
            not os.path.isdir(collections_path)
        self.local_file_driver.init()
        self.local_file_driver.create_collections_dir()
        result = self.local_file_driver.exists_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_ensure_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.filepath,
                                        ".datmo", "collections")
        result = self.local_file_driver.ensure_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_delete_collections_dir(self):
        collections_path = os.path.join(self.local_file_driver.filepath,
                                        ".datmo", "collections")
        self.local_file_driver.init()
        self.local_file_driver.create_collections_dir()
        result = self.local_file_driver.delete_collections_dir()
        assert result == True and \
            not os.path.isdir(collections_path)

    def test_create_collection(self):
        self.local_file_driver.init()

        # Test empty file collection
        filehash_empty = self.local_file_driver. \
            create_collection([])
        collection_path_empty = os.path.join(self.local_file_driver.filepath,
                                             ".datmo", "collections", filehash_empty)

        assert os.path.isdir(collection_path_empty)

        # Test creating another empty file collection (should not fail)
        filehash_empty = self.local_file_driver. \
            create_collection([])
        collection_path_empty = os.path.join(self.local_file_driver.filepath,
                                             ".datmo", "collections", filehash_empty)

        assert os.path.isdir(collection_path_empty)
        self.local_file_driver.delete_collection(filehash_empty)

        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create("filepath1")

        dirpath1 = os.path.join(self.local_file_driver.filepath,
                                "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.filepath,
                                "dirpath2")
        filepath1 = os.path.join(self.local_file_driver.filepath,
                                 "filepath1")
        filehash = self.local_file_driver.\
            create_collection([dirpath1, dirpath2, filepath1])
        collection_path = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash)

        assert os.path.isdir(collection_path)
        assert os.path.isdir(os.path.join(collection_path,
                                       "dirpath1")) and \
               (oct(os.stat(os.path.join(collection_path,
                                        "dirpath1")).st_mode & 0o777) == '0o755' or
                oct(os.stat(os.path.join(collection_path,
                                         "dirpath1")).st_mode & 0o777) == '0755')
        assert os.path.isdir(os.path.join(collection_path,
                                       "dirpath2")) and \
               (oct(os.stat(os.path.join(collection_path,
                                        "dirpath2")).st_mode & 0o777) == '0o755' or
                oct(os.stat(os.path.join(collection_path,
                                         "dirpath2")).st_mode & 0o777) == '0755')
        assert os.path.isfile(os.path.join(collection_path,
                                        "filepath1")) and \
               (oct(os.stat(os.path.join(collection_path,
                                        "filepath1")).st_mode & 0o777) == '0o755' or
                oct(os.stat(os.path.join(collection_path,
                                         "filepath1")).st_mode & 0o777) == '0755')
        self.local_file_driver.delete_collection(filehash)

    def test_get_absolute_collection_path(self):
        self.local_file_driver.init()
        filehash = self.local_file_driver. \
            create_collection([])
        collection_path = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash)
        returned_collection_path = self.local_file_driver.\
            get_absolute_collection_path(filehash)
        assert returned_collection_path == collection_path

    def test_get_relative_collection_path(self):
        self.local_file_driver.init()
        filehash = self.local_file_driver. \
            create_collection([])
        relative_collection_path = os.path.join(".datmo",
                                                "collections", filehash)
        returned_relative_collection_path = self.local_file_driver.\
            get_relative_collection_path(filehash)
        assert returned_relative_collection_path == relative_collection_path

    def test_exists_collection(self):
        self.local_file_driver.init()
        filehash = self.local_file_driver.create_collection([])
        collection_path = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash)
        result = self.local_file_driver.exists_collection(filehash)
        assert result == True and \
            os.path.isdir(collection_path)

    def test_get_collection_files(self):
        self.local_file_driver.init()
        # Test empty file collection default mode
        filehash_empty = self.local_file_driver. \
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
        dirpath1 = os.path.join(self.local_file_driver.filepath,
                                "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.filepath,
                                "dirpath2")
        filepath3 = os.path.join(self.local_file_driver.filepath,
                                 "filepath3")

        filehash = self.local_file_driver. \
            create_collection([dirpath1, dirpath2, filepath3])

        # Absolute file paths after added to collection (to test)
        filepath1_after = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash,
                                       "dirpath1", "filepath1")
        filepath2_after = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash,
                                       "dirpath2", "filepath2")
        filepath3_after = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash,
                                       "filepath3")
        filepaths_list = [filepath1_after, filepath2_after, filepath3_after]
        result = self.local_file_driver.get_collection_files(filehash)


        assert len(result) == 3
        assert isinstance(result[0], TextIOWrapper) and \
               result[0].name in filepaths_list
        assert isinstance(result[1], TextIOWrapper) and \
               result[1].name in filepaths_list
        assert isinstance(result[2], TextIOWrapper) and \
               result[2].name in filepaths_list

    def test_delete_collection(self):
        self.local_file_driver.init()
        filehash = self.local_file_driver.create_collection([])
        collection_path = os.path.join(self.local_file_driver.filepath,
                                       ".datmo", "collections", filehash)
        result = self.local_file_driver.delete_collection(filehash)
        assert result == True and \
            not os.path.isdir(collection_path)

    def test_list_file_collections(self):
        self.local_file_driver.init()
        filehash_1 = self.local_file_driver.create_collection([])
        self.local_file_driver.create("filepath1")
        filepath1 = os.path.join(self.local_file_driver.filepath,
                                 "filepath1")
        filehash_2 = self.local_file_driver.create_collection([filepath1])
        collection_list = self.local_file_driver.list_file_collections()
        assert filehash_1 in collection_list and \
               filehash_2 in collection_list


    def test_transfer_collection(self):
        # Create test directories to move
        self.local_file_driver.create("dirpath1", directory=True)
        self.local_file_driver.create("dirpath2", directory=True)
        self.local_file_driver.create("filepath1")

        dirpath1 = os.path.join(self.local_file_driver.filepath,
                                "dirpath1")
        dirpath2 = os.path.join(self.local_file_driver.filepath,
                                "dirpath2")
        filepath1 = os.path.join(self.local_file_driver.filepath,
                                 "filepath1")
        self.local_file_driver.init()
        filehash = self.local_file_driver. \
            create_collection([dirpath1, dirpath2, filepath1])
        dst_dirpath = os.path.join(self.temp_dir, "new_dir")
        self.local_file_driver.create(dst_dirpath, directory=True)
        result = self.local_file_driver.transfer_collection(filehash,
                                                    dst_dirpath)
        assert result == True and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath1")) and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath2")) and \
               os.path.isfile(os.path.join(dst_dirpath,
                                           "filepath1"))