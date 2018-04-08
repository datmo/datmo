"""
Tests for local.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile

from datmo.controller.file.driver.local import LocalFileDriver


class TestLocalFileManager():
    # TODO: Add more cases for each test
    """
    Checks all functions of the LocalFileDriver
    """
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir="/tmp/")
        self.local_file_manager = LocalFileDriver(filepath=self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_initialize(self):
        assert self.local_file_manager != None

    # Static Method Tests

    def test_get_safe_dst_filepath(self):
        # Create first file to copy
        relative_filepath = "test.json"
        self.local_file_manager.create(relative_filepath)
        # Create destination directory
        relative_dirpath = "dest"
        self.local_file_manager.create(relative_dirpath, dir=True)
        # Create file within destination directory
        relative_filename_2 = os.path.join(relative_dirpath, "test.json")
        self.local_file_manager.create(relative_filename_2)

        filepath = os.path.join(self.local_file_manager.filepath,
                                relative_filepath)
        dirpath = os.path.join(self.local_file_manager.filepath,
                               relative_dirpath)
        result = self.local_file_manager.\
            get_safe_dst_filepath(filepath, dirpath)
        assert result == os.path.join(dirpath, "test_0.json")

    def test_copytree(self):
        # Create source directory
        relative_src_dirpath = "src"
        self.local_file_manager.create(relative_src_dirpath, dir=True)
        relative_src_filepath = os.path.join(relative_src_dirpath, "test.json")
        self.local_file_manager.create(relative_src_filepath)
        # Create destination directory
        relative_dst_dirpath = "dst"
        self.local_file_manager.create(relative_dst_dirpath, dir=True)
        # Copy source directory to destination
        src_dirpath = os.path.join(self.local_file_manager.filepath,
                                   relative_src_dirpath)
        dst_dirpath = os.path.join(self.local_file_manager.filepath,
                                   relative_dst_dirpath)
        self.local_file_manager.copytree(src_dirpath, dst_dirpath)
        dst_filepath = os.path.join(dst_dirpath, "test.json")
        assert os.path.isdir(os.path.join(dst_dirpath)) and \
            os.path.isfile(dst_filepath) == True

    def test_copyfile(self):
        # Create first file to copy
        relative_filepath = "test.json"
        self.local_file_manager.create(relative_filepath)
        # Create destination directory
        relative_dst_dirpath = "dest"
        self.local_file_manager.create(relative_dst_dirpath, dir=True)
        # Copy file to destination
        filepath = os.path.join(self.local_file_manager.filepath,
                                relative_filepath)
        dst_dirpath = os.path.join(self.local_file_manager.filepath,
                                   relative_dst_dirpath)
        self.local_file_manager.copyfile(filepath, dst_dirpath)
        assert os.path.isfile(os.path.join(dst_dirpath, relative_filepath)) == True

    # Instance Method Tests

    def test_init(self):
        result = self.local_file_manager.init()
        assert result and \
               self.local_file_manager.is_initialized

    def test_create(self):
        temp_relative_filepath = "test.json"
        temp_filepath = self.local_file_manager.create(temp_relative_filepath)
        assert os.path.isfile(temp_filepath) == True

    def test_exists(self):
        temp_relative_filepath = "test.json"
        result = self.local_file_manager.exists(temp_relative_filepath)
        assert result == False
        self.local_file_manager.create(temp_relative_filepath)
        result = self.local_file_manager.exists(temp_relative_filepath)
        assert result == True

    def test_ensure(self):
        temp_relative_filepath = "test.json"
        self.local_file_manager.ensure(temp_relative_filepath)
        assert os.path.isfile(
            os.path.join(self.local_file_manager.filepath,
                         temp_relative_filepath)
        ) == True

    def test_delete(self):
        temp_relative_filepath = "test.json"
        self.local_file_manager.create(temp_relative_filepath)
        filepath = os.path.join(self.local_file_manager.filepath,
                         temp_relative_filepath)
        assert os.path.exists(filepath) == True
        self.local_file_manager.delete(temp_relative_filepath)
        assert os.path.exists(filepath) == False

    def test_create_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_manager.filepath,
                                ".datmo")
        result = self.local_file_manager.create_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(filepath)

    def test_exists_hidden_datmo_dir(self):
        result = self.local_file_manager.exists_hidden_datmo_dir()
        assert result == False
        self.local_file_manager.create_hidden_datmo_dir()
        result = self.local_file_manager.exists_hidden_datmo_dir()
        assert result == True

    def test_ensure_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_manager.filepath,
                                ".datmo")
        result = self.local_file_manager.ensure_hidden_datmo_dir()
        assert result == True and \
               os.path.isdir(filepath)

    def test_delete_hidden_datmo_dir(self):
        filepath = os.path.join(self.local_file_manager.filepath,
                                ".datmo")
        self.local_file_manager.create_hidden_datmo_dir()
        result = self.local_file_manager.delete_hidden_datmo_dir()
        assert result == True and \
               not os.path.isdir(filepath)

    def test_create_datmo_file_structure(self):
        filepath = os.path.join(self.local_file_manager.filepath,
                                ".datmo")
        result = self.local_file_manager.create_datmo_file_structure()
        assert result == True and \
               os.path.isdir(filepath)

    def test_exists_datmo_file_structure(self):
        result = self.local_file_manager.exists_datmo_file_structure()
        assert result == False
        self.local_file_manager.ensure_datmo_file_structure()
        result = self.local_file_manager.exists_datmo_file_structure()
        assert result == True

    def test_ensure_datmo_file_structure(self):
        hidden_datmo_dir_filepath = os.path.join(self.local_file_manager.filepath,
                                ".datmo")
        result = self.local_file_manager.ensure_datmo_file_structure()
        assert result == True and \
               os.path.isdir(hidden_datmo_dir_filepath)

    def test_delete_datmo_file_structure(self):
        hidden_datmo_dir_filepath = os.path.join(self.local_file_manager.filepath,
                                                 ".datmo")
        self.local_file_manager.create_datmo_file_structure()
        result = self.local_file_manager.delete_datmo_file_structure()
        assert result == True and \
            not os.path.isdir(hidden_datmo_dir_filepath)

    # Template tests

    # TODO : Add tests for code that handles various project templates

    # Collection Tests
    def test_create_collections_dir(self):
        collections_path = os.path.join(self.local_file_manager.filepath,
                                        ".datmo", "collections")
        try:
            self.local_file_manager.create_collections_dir()
            thrown = False
        except:
            thrown = True
        assert thrown == True and \
            not os.path.isdir(collections_path)
        self.local_file_manager.init()
        result = self.local_file_manager.create_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_exists_collections_dir(self):
        collections_path = os.path.join(self.local_file_manager.filepath,
                                        ".datmo", "collections")
        result = self.local_file_manager.exists_collections_dir()
        assert result == False and \
            not os.path.isdir(collections_path)
        self.local_file_manager.init()
        self.local_file_manager.create_collections_dir()
        result = self.local_file_manager.exists_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_ensure_collections_dir(self):
        collections_path = os.path.join(self.local_file_manager.filepath,
                                        ".datmo", "collections")
        result = self.local_file_manager.ensure_collections_dir()
        assert result == True and \
            os.path.isdir(collections_path)

    def test_delete_collections_dir(self):
        collections_path = os.path.join(self.local_file_manager.filepath,
                                        ".datmo", "collections")
        self.local_file_manager.init()
        self.local_file_manager.create_collections_dir()
        result = self.local_file_manager.delete_collections_dir()
        assert result == True and \
            not os.path.isdir(collections_path)

    def test_create_collection(self):
        # Create test directories to move
        self.local_file_manager.create("dirpath1", dir=True)
        self.local_file_manager.create("dirpath2", dir=True)
        self.local_file_manager.create("filepath1")

        dirpath1 = os.path.join(self.local_file_manager.filepath,
                                "dirpath1")
        dirpath2 = os.path.join(self.local_file_manager.filepath,
                                "dirpath2")
        filepath1 = os.path.join(self.local_file_manager.filepath,
                                 "filepath1")
        self.local_file_manager.init()
        collection_id = self.local_file_manager.\
            create_collection([dirpath1, dirpath2, filepath1])
        collection_path = os.path.join(self.local_file_manager.filepath,
                                       ".datmo", "collections", collection_id)

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
        self.local_file_manager.delete_collection(collection_id)

    def test_get_collection_path(self):
        self.local_file_manager.init()
        collection_id = self.local_file_manager. \
            create_collection([])
        collection_path = os.path.join(self.local_file_manager.filepath,
                                       ".datmo", "collections", collection_id)
        returned_collection_path = self.local_file_manager.\
            get_collection_path(collection_id)
        assert returned_collection_path == collection_path

    def test_exists_collection(self):
        self.local_file_manager.init()
        collection_id = self.local_file_manager.create_collection([])
        collection_path = os.path.join(self.local_file_manager.filepath,
                                       ".datmo", "collections", collection_id)
        result = self.local_file_manager.exists_collection(collection_id)
        assert result == True and \
            os.path.isdir(collection_path)

    def test_delete_collection(self):
        self.local_file_manager.init()
        collection_id = self.local_file_manager.create_collection([])
        collection_path = os.path.join(self.local_file_manager.filepath,
                                       ".datmo", "collections", collection_id)
        result = self.local_file_manager.delete_collection(collection_id)
        assert result == True and \
            not os.path.isdir(collection_path)

    def test_list_file_collections(self):
        self.local_file_manager.init()
        collection_id_1 = self.local_file_manager.create_collection([])
        self.local_file_manager.create("filepath1")
        filepath1 = os.path.join(self.local_file_manager.filepath,
                                 "filepath1")
        collection_id_2 = self.local_file_manager.create_collection([filepath1])
        collection_list = self.local_file_manager.list_file_collections()
        assert collection_id_1 in collection_list and \
               collection_id_2 in collection_list


    def test_transfer_collection(self):
        # Create test directories to move
        self.local_file_manager.create("dirpath1", dir=True)
        self.local_file_manager.create("dirpath2", dir=True)
        self.local_file_manager.create("filepath1")

        dirpath1 = os.path.join(self.local_file_manager.filepath,
                                "dirpath1")
        dirpath2 = os.path.join(self.local_file_manager.filepath,
                                "dirpath2")
        filepath1 = os.path.join(self.local_file_manager.filepath,
                                 "filepath1")
        self.local_file_manager.init()
        collection_id = self.local_file_manager. \
            create_collection([dirpath1, dirpath2, filepath1])
        dst_dirpath = os.path.join(self.temp_dir, "new_dir")
        self.local_file_manager.create(dst_dirpath, dir=True)
        result = self.local_file_manager.transfer_collection(collection_id,
                                                    dst_dirpath)
        assert result == True and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath1")) and \
               os.path.isdir(os.path.join(dst_dirpath,
                                          "dirpath2")) and \
               os.path.isfile(os.path.join(dst_dirpath,
                                           "filepath1"))