import os
import shutil
import glob
import hashlib
import uuid
import checksumdir

from datmo.util.exceptions import DoesNotExistException, \
    FileIOException, FileStructureException

class LocalFileManager(object):
    """
    The File Manager handles the Datmo file tree.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise DoesNotExistException("exception.file.local", {
                "filepath": filepath,
                "exception": "File path does not exist"
            })
        self._is_initialized = self.is_initialized

    @staticmethod
    def get_filehash(filepath):
        if not os.path.isfile(filepath):
            raise DoesNotExistException("exception.file.local.get_filehash",{
                "exception": "filepath is not a file."
            })
        BUFF_SIZE = 65536
        sha1 = hashlib.md5()
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def get_safe_dst_filepath(filepath, dst_dirpath):
        if not os.path.isfile(filepath):
            raise DoesNotExistException("exception.file.local.get_safe_dst_filepath",{
                "exception": "filepath is not a file."
            })
        if not os.path.isdir(dst_dirpath):
            raise DoesNotExistException("exception.file.local.get_safe_dst_filepath", {
                "exception": "dst_dirpath is not a dir."
            })
        _, filename = os.path.split(filepath)
        dst_filepath = os.path.join(dst_dirpath, filename)
        number_of_items = glob.glob(dst_filepath)
        if number_of_items:
            filepath_without_ext = os.path.splitext(dst_filepath)[0]
            extension = os.path.splitext(dst_filepath)[1]
            number_of_items = len(glob.glob(filepath_without_ext+'*'))
            new_filepath = filepath_without_ext + "_" + str(number_of_items-1)
            new_filepath_with_ext = new_filepath + extension
            return new_filepath_with_ext
        else:
            return dst_filepath

    @staticmethod
    def copytree(src_dirpath, dst_dirpath,
                 symlinks=False, ignore=None):
        if not os.path.isdir(src_dirpath):
            raise DoesNotExistException("exception.file.local.copytree",{
                "exception": "src_dirpath is not a dir."
            })
        if not os.path.isdir(dst_dirpath):
            raise DoesNotExistException("exception.file.local.copytree",{
                "exception": "dst_dirpath is not a dir."
            })
        for item in os.listdir(src_dirpath):
            src_filepath = os.path.join(src_dirpath, item)
            dst_filepath = os.path.join(dst_dirpath, item)
            if os.path.isdir(src_filepath):
                if os.path.exists(dst_filepath):
                    shutil.rmtree(dst_filepath)
                shutil.copytree(src_filepath, dst_filepath,
                                symlinks, ignore)
            else:
                if os.path.exists(dst_filepath):
                    os.remove(dst_filepath)
                shutil.copy2(src_filepath, dst_filepath)
        return True

    @staticmethod
    def copyfile(filepath, dst_dirpath):
        if not os.path.isfile(filepath):
            raise DoesNotExistException("exception.file.local.copyfile",{
                "exception": "filepath is not a file."
            })
        if not os.path.isdir(dst_dirpath):
            raise DoesNotExistException("exception.file.local.copyfile", {
                "exception": "dst_dirpath is not a dir."
            })
        dst_filepath = LocalFileManager.get_safe_dst_filepath(filepath, dst_dirpath)
        shutil.copy2(filepath, dst_filepath)
        return True

    @property
    def is_initialized(self):
        if self.exists_datmo_file_structure():
            self._is_initialized = True
            return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    def init(self):
        try:
            # Ensure the Datmo file structure exists
            self.ensure_datmo_file_structure()
        except Exception as e:
            raise FileIOException("exception.file.local.init", {
                "exception": e
            })
        return True


    def create(self, relative_filepath, dir=False):
        filepath = os.path.join(self.filepath,
                                relative_filepath)
        if os.path.exists(filepath):
            os.utime(filepath, None)
        else:
            if dir:
                os.makedirs(filepath)
            else:
                with open(os.path.join(self.filepath,
                                  relative_filepath), 'a'):
                    os.utime(filepath, None)
        return filepath

    def exists(self, relative_filepath, dir=False):
        filepath = os.path.join(self.filepath,
                                relative_filepath)
        if dir:
            return True if os.path.isdir(filepath) else False
        else:
            return True if os.path.isfile(filepath) else False

    def ensure(self, relative_filepath, dir=False):
        if not self.exists(os.path.join(self.filepath,
                                        relative_filepath),
                           dir=dir):
            self.create(os.path.join(os.path.join(self.filepath,
                                                  relative_filepath)),
                        dir=dir)
        return True

    def delete(self, relative_filepath, dir=False):
        if not os.path.exists(os.path.join(self.filepath,
                                       relative_filepath)):
            raise DoesNotExistException("exception.file.local.delete", {
                "filepath": os.path.join(self.filepath, relative_filepath),
                "exception": "File does not exist"
            })
        if dir:
            shutil.rmtree(relative_filepath)
        else:
            os.remove(os.path.join(self.filepath,
                               relative_filepath))
        return True

    # Datmo base directory
    def create_hidden_datmo_dir(self):
        filepath = os.path.join(self.filepath,
                                 ".datmo")
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        return True

    def exists_hidden_datmo_dir(self):
        filepath = os.path.join(self.filepath,
                                 ".datmo")
        return self.exists(filepath, dir=True)

    def ensure_hidden_datmo_dir(self):
        filepath = os.path.join(self.filepath,
                                 ".datmo")
        return self.ensure(filepath, dir=True)

    def delete_hidden_datmo_dir(self):
        filepath = os.path.join(self.filepath,
                                 ".datmo")
        return self.delete(filepath, dir=True)


    # Overall Datmo file structure
    def create_datmo_file_structure(self):
        return self.create_hidden_datmo_dir()

    def exists_datmo_file_structure(self):
        return self.exists_hidden_datmo_dir()

    def ensure_datmo_file_structure(self):
        return self.ensure_hidden_datmo_dir()

    def delete_datmo_file_structure(self):
        return self.delete_hidden_datmo_dir()

    # Template files handling
    def exists_dockerfile(self):
        if not os.path.isfile(os.path.join(self.filepath, "Dockerfile")):
            return False
        return True

    def ensure_dockerfile(self):
        try:
            template_dockerfile_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "templates", "sampleDockerfile")
            current_dockerfile_filepath = os.path.join(self.filepath, "Dockerfile")
            # Copy the template Dockerfile if none exists
            if not self.exists_dockerfile():
                shutil.copyfile(template_dockerfile_filepath, current_dockerfile_filepath)
        except Exception as e:
            raise FileIOException("exception.environment_driver.docker.ensure_dockerfile", {
                "exception": e
            })
        return True

    def exists_api_file(self):
        if not os.path.isfile(os.path.join(self.filepath, "api.py")):
            return False
        return True

    def ensure_api_file(self):
        try:
            template_api_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       "templates", "api.py")
            current_api_filepath = os.path.join(self.filepath, "api.py")
            if not self.exists_api_file():
                shutil.copyfile(template_api_filepath, current_api_filepath)
        except Exception as e:
            raise FileIOException("exception.file.local.ensure_api_file", {
                "exception": e
            })
        return True

    def exists_script_file(self):
        if not os.path.isfile(os.path.join(self.filepath, "script.py")):
            return False
        return True

    def ensure_script_file(self):
        try:
            template_script_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "templates", "script.py")
            current_script_filepath = os.path.join(self.filepath, "script.py")
            if not self.exists_script_file():
                shutil.copyfile(template_script_filepath, current_script_filepath)
        except Exception as e:
            raise FileIOException("exception.file.local.ensure_script_file", {
                "exception": e
            })
        return True

    # Collections
    def create_collections_dir(self):
        if not self.is_initialized:
            raise FileStructureException("exception.file.local.create_collections_dir", {
                "exception": "FileManager is not properly initialized"
            })
        collections_path = os.path.join(self.filepath, ".datmo",
                                             "collections")
        if not os.path.isdir(collections_path):
            os.makedirs(collections_path)
        return True

    def exists_collections_dir(self):
        collections_path = os.path.join(self.filepath, ".datmo",
                                             "collections")
        return self.exists(collections_path, dir=True)

    def ensure_collections_dir(self):
        collections_path = os.path.join(self.filepath, ".datmo",
                                             "collections")
        return self.ensure(collections_path, dir=True)

    def delete_collections_dir(self):
        collections_path = os.path.join(self.filepath, ".datmo",
                                    "collections")
        return self.delete(collections_path, dir=True)


    def create_collection(self, filepaths):
        if not self.is_initialized:
            raise FileStructureException("exception.file.local.create_file_collection", {
                "exception": "FileManager is not properly initialized"
            })

        # Create temp hash and folder to move all contents from filepaths
        temp_hash = hashlib.sha1(str(uuid.uuid4()).\
                                          encode("UTF=8")).hexdigest()[:20]
        self.ensure_collections_dir()
        temp_collection_path = os.path.join(self.filepath, ".datmo",
                                            "collections", temp_hash)
        os.makedirs(temp_collection_path)

        # Populate collection
        for filepath in filepaths:
            _, dirname = os.path.split(filepath)
            if os.path.isdir(filepath):
                dst_dirpath = os.path.join(temp_collection_path, dirname)
                self.create(dst_dirpath, dir=True)
                # All contents of directory are copied into the dst_dirpath
                self.copytree(filepath, dst_dirpath)
            elif os.path.isfile(filepath):
                # File is copied into the collection_path
                self.copyfile(filepath, temp_collection_path)
            else:
                raise DoesNotExistException("exception.file.local.create_file_collection", {
                    "exception": "Filepath %s does not exist." % filepath
                })

        # Hash the files to find collection_id
        collection_id = checksumdir.dirhash(temp_collection_path)

        # Move contents to folder with collection_id as name and remove temp_collection_path
        collection_path = os.path.join(self.filepath, ".datmo",
                                       "collections", collection_id)
        if os.path.isdir(collection_path):
            return collection_id
            # raise FileStructureException("exception.file.create_collection", {
            #     "exception": "File collection with id already exists."
            # })
        os.makedirs(collection_path)
        self.copytree(temp_collection_path, collection_path)
        shutil.rmtree(temp_collection_path)

        # Change permissions to read only for collection_path. File collection is immutable
        # TODO: chmod format only is for Python 2.X (doesn't work for Python 3.X)
        mode = 0755
        for root, dirs, files in os.walk(collection_path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)

        return collection_id

    def get_collection_path(self, collection_id):
        return os.path.join(self.filepath, ".datmo",
                            "collections", collection_id)

    def exists_collection(self, collection_id):
        collection_path = os.path.join(self.filepath, ".datmo",
                                       "collections", collection_id)
        return self.exists(collection_path, dir=True)

    def delete_collection(self, collection_id):
        collection_path = os.path.join(self.filepath, ".datmo",
                                       "collections", collection_id)
        return self.delete(collection_path, dir=True)

    def transfer_collection(self, collection_id, dst_dirpath):
        if not self.exists_collection(collection_id):
            raise DoesNotExistException("exception.file.local.transfer_collection", {
                "exception": "Collection does not currently exist"
            })
        collection_path = os.path.join(self.filepath, ".datmo",
                                       "collections", collection_id)
        return self.copytree(collection_path, dst_dirpath)

    def list_file_collections(self):
        if not self.is_initialized:
            raise FileStructureException("exception.file.local.list_file_collections", {
                "exception": "FileManager is not properly initialized"
            })
        collections_path = os.path.join(self.filepath, ".datmo",
                                        "collections")
        collections_list = os.listdir(collections_path)
        return collections_list


    # @staticmethod
    # def create_readme(directory, filename, model_name, model_description, model_url, echo_prefix=""):
    #     filepath = os.path.join(directory, filename)
    #     badge_text = "[![Datmo Model]" \
    #                  "(" + model_url + "/badge.svg)]" \
    #                  "(" + model_url + ")"
    #     if not os.path.exists(filepath):
    #         click.echo(echo_prefix + "Creating a stub %s." % filename)
    #         with open(filepath, 'a') as f:
    #             f.write('# ' + str(model_name) + '\n')
    #             f.write('\n')
    #             f.write(badge_text.rstrip('\r\n') + '\n')
    #             f.write('\n')
    #             f.write('\n')
    #             f.write(str(model_description) + '\n')
    #         click.echo(echo_prefix + "%s present in the model" % filename)
    #
    # @staticmethod
    # def add_badge_to_readme(directory, filename, model_url):
    #     filepath = os.path.join(directory, filename)
    #     badge_text = "[![Datmo Model]" \
    #                  "(" + model_url + "/badge.svg)]" \
    #                  "(" + model_url + ")"
    #     # Check if badge_text already exists. If so mention it and do not add
    #     if badge_text in open(filepath).read():
    #         return False
    #     with open(filepath, 'r+') as f:
    #         content = f.read()
    #         f.seek(0, 0)
    #         f.write(badge_text.rstrip('\r\n') + '\n\n\n' + content)
    #     return True





