"""
Tests for git.py
"""
from __future__ import division
from __future__ import unicode_literals

import os
import shutil
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.code.driver.git import (GitCodeDriver,
                                                   GitHostDriver)
from datmo.core.util.exceptions import (
    GitCommitDoesNotExist, PathDoesNotExist, GitExecutionException,
    DatmoFolderInWorkTree)


class TestGitCodeDriver():
    """
    Checks all functions of the GitCodeDriver
    """

    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.git_code_manager = GitCodeDriver(
            filepath=self.temp_dir, execpath="git")

    def teardown_method(self):
        pass

    def test_instantiation(self):
        assert self.git_code_manager != None

    def test_instantiation_fail_dne(self):
        failed = False
        try:
            _ = GitCodeDriver(filepath="nonexistant_path", execpath="git")
        except PathDoesNotExist:
            failed = True
        assert failed

    def test_instantiation_fail_git_does_not_exist(self):
        failed = False
        try:
            _ = GitCodeDriver(
                filepath=self.temp_dir, execpath="nonexistant_execpath")
        except GitExecutionException:
            failed = True
        assert failed

    def test_instantiation_fail_git_version_out_of_date(self):
        pass

    def test_init(self):
        result = self.git_code_manager.init()
        assert result and \
               self.git_code_manager.is_initialized == True

    def test_init_then_instantiation(self):
        self.git_code_manager.init()
        another_git_code_manager = GitCodeDriver(
            filepath=self.temp_dir, execpath="git")
        result = another_git_code_manager.is_initialized
        assert result == True

    def test_instantiation_fail_datmo_files_in_worktree(self):
        self.git_code_manager.init()
        # Add random file to .datmo directory before next ref
        os.makedirs(os.path.join(self.git_code_manager.filepath, ".datmo"))
        random_filepath = os.path.join(self.git_code_manager.filepath,
                                       ".datmo", ".test")
        with open(random_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        # Add files and commit then check they exist
        self.git_code_manager.add(".datmo", "-f")
        self.git_code_manager.commit(["-m", "test message"])
        failed = False
        try:
            _ = GitCodeDriver(filepath=self.temp_dir, execpath="git")
        except DatmoFolderInWorkTree:
            failed = True
        assert failed

    def test_exists_datmo_files_ignored(self):
        self.git_code_manager.init()
        result = self.git_code_manager.exists_datmo_files_ignored()
        assert result == True
        # Remove .datmo from exclude
        exclude_file = os.path.join(self.git_code_manager.filepath,
                                    ".git/info/exclude")
        with open(exclude_file) as f:
            lines = f.readlines()
        with open(exclude_file, 'w') as f:
            f.writelines([to_unicode(item) for item in lines[:-2]])
        result = self.git_code_manager.exists_datmo_files_ignored()
        assert result == False

    def test_ensure_datmo_files_ignored(self):
        self.git_code_manager.init()
        # Remove .datmo from exclude
        exclude_file = os.path.join(self.git_code_manager.filepath,
                                    ".git/info/exclude")
        with open(exclude_file) as f:
            lines = f.readlines()
        with open(exclude_file, 'w') as f:
            f.writelines([to_unicode(item) for item in lines[:-2]])
        result = self.git_code_manager.ensure_datmo_files_ignored()
        assert result and \
               self.git_code_manager.exists_datmo_files_ignored()

    def test_exists_datmo_files_in_worktree(self):
        self.git_code_manager.init()
        # Add random file to .datmo directory before next ref
        os.makedirs(os.path.join(self.git_code_manager.filepath, ".datmo"))
        random_filepath = os.path.join(self.git_code_manager.filepath,
                                       ".datmo", ".test")
        with open(random_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        # Check that it doesn't exist
        result = self.git_code_manager.exists_datmo_files_in_worktree()
        assert result == False
        # Add files and commit then check they exist
        self.git_code_manager.add(".datmo", "-f")
        self.git_code_manager.commit(["-m", "test message"])
        result = self.git_code_manager.exists_datmo_files_in_worktree()
        assert result == True

    def test_clone(self):
        result = self.git_code_manager.clone(
            "https://github.com/datmo/hello-world.git", mode="https")
        assert result and os.path.exists(
            os.path.join(self.temp_dir, "hello-world", ".git"))
        result = self.git_code_manager.clone(
            "https://github.com/datmo/hello-world.git",
            repo_name="hello-world-2",
            mode="http")
        assert result and os.path.exists(
            os.path.join(self.temp_dir, "hello-world-2", ".git"))
        if self.git_code_manager.git_host_manager.ssh_enabled:
            result = self.git_code_manager.clone(
                "https://github.com/datmo/hello-world.git",
                repo_name="hello-world-3",
                mode="ssh")
            assert result and os.path.exists(
                os.path.join(self.temp_dir, "hello-world-3", ".git"))

    def test_parse_git_url(self):
        parsed = self.git_code_manager._parse_git_url(
            "https://github.com/datmo/hello-world.git", mode="ssh")
        assert parsed == "git@github.com:datmo/hello-world.git"
        parsed = self.git_code_manager._parse_git_url(
            "https://github.com/datmo/hello-world.git", mode="https")
        assert parsed == "https://github.com/datmo/hello-world.git"
        parsed = self.git_code_manager._parse_git_url(
            "https://github.com/datmo/hello-world.git", mode="http")
        assert parsed == "http://github.com/datmo/hello-world.git"
        # git@github.com:gitpython-developers/GitPython.git
        # https://github.com/gitpython-developers/GitPython.git
        parsed = self.git_code_manager._parse_git_url(
            "git://github.com/datmo/hello-world.git", mode="ssh")
        assert parsed == "git@github.com:datmo/hello-world.git"
        parsed = self.git_code_manager._parse_git_url(
            "git://github.com/datmo/hello-world.git", mode="https")
        assert parsed == "https://github.com/datmo/hello-world.git"
        parsed = self.git_code_manager._parse_git_url(
            "git://github.com/datmo/hello-world.git", mode="http")
        assert parsed == "http://github.com/datmo/hello-world.git"

    def test_add(self):
        self.git_code_manager.init()
        # Test True case for new file no option
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        result = self.git_code_manager.add(test_filepath)
        assert result == True
        # Test True case for new file with option
        result = self.git_code_manager.add(test_filepath, option="-f")
        assert result == True

    def test_commit(self):
        # TODO: try out more options (for failed execution)
        self.git_code_manager.init()
        # Test False case if no new commit created
        result = self.git_code_manager.commit(["-m", "test"])
        assert result == False
        # Test True case for new commit
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        self.git_code_manager.add(test_filepath)
        result = self.git_code_manager.commit(["-m", "test"])
        commit_id = self.git_code_manager.latest_commit()
        assert result == True and commit_id

    def test_exists_commit(self):
        self.git_code_manager.init()
        random_code_id = "random"
        result = \
            self.git_code_manager.exists_commit(random_code_id)
        assert result == False
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        self.git_code_manager.add(test_filepath)
        self.git_code_manager.commit(["-m", "test"])
        commit_id = self.git_code_manager.latest_commit()
        result = self.git_code_manager.exists_commit(commit_id)
        assert result == True

    # def test_branch(self):
    #     pass

    def test_checkout(self):
        # TODO: Test remote checkout
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test1")))
        self.git_code_manager.add(test_filepath)
        _ = self.git_code_manager.commit(["-m", "test"])
        commit_id_1 = self.git_code_manager.latest_commit()
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test2")))
        self.git_code_manager.add(test_filepath)
        _ = self.git_code_manager.commit(["-m", "test"])
        commit_id_2 = self.git_code_manager.latest_commit()
        result = self.git_code_manager.checkout(commit_id_1)

        assert commit_id_1 != commit_id_2
        assert result == True and \
               self.git_code_manager.latest_commit() == commit_id_1

    # def test_stash_save(self):s
    #     pass
    #
    # def test_stash_list(self):
    #     pass
    #
    # def test_stash_pop(self):
    #     pass
    #
    # def test_stash_apply(self):
    #     pass
    #
    def test_latest_commit(self):
        self.git_code_manager.init()
        # Check if properly returns error without commit
        failed = False
        try:
            self.git_code_manager.latest_commit()
        except:
            failed = True
        assert failed
        # Check if properly returns latest commit
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        self.git_code_manager.add(test_filepath)
        self.git_code_manager.commit(["-m", "test"])
        latest_commit = self.git_code_manager.latest_commit()
        assert latest_commit

    def test_reset(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        self.git_code_manager.add(test_filepath)
        self.git_code_manager.commit(["-m", "test"])
        commit_id = self.git_code_manager.latest_commit()
        result = self.git_code_manager.reset(git_commit=commit_id)
        assert result == True

    def test_check_git_work_tree(self):
        self.git_code_manager.init()
        result = self.git_code_manager.check_git_work_tree()
        assert result == True

    def test_remote(self):
        # TODO: test all options
        self.git_code_manager.init()
        # Test remote add
        if self.git_code_manager.git_host_manager.host == "github.com":
            result = self.git_code_manager.remote(
                "add", "origin", "https://github.com/datmo/test.git")
            remote_url = self.git_code_manager.get_remote_url()
            assert result == True and \
                remote_url == "https://github.com/datmo/test.git"
            # Test remote set-url
            result = self.git_code_manager.remote(
                "set-url", "origin", "https://github.com/datmo/test.git")
            remote_url = self.git_code_manager.get_remote_url()
            assert result == True and \
                remote_url == "https://github.com/datmo/test.git"

    def test_get_remote_url(self):
        self.git_code_manager.init()
        # Check if properly returns None
        remote_url = self.git_code_manager.get_remote_url()
        assert remote_url == None
        # Check if properly returns value set
        if self.git_code_manager.git_host_manager.host == "github.com":
            self.git_code_manager.remote("add", "origin",
                                         "https://github.com/datmo/test.git")
            self.git_code_manager.remote("set-url", "origin",
                                         "https://github.com/datmo/test.git")
            remote_url = self.git_code_manager.get_remote_url()
            assert remote_url == "https://github.com/datmo/test.git"

    # def test_fetch(self):
    #     pass
    #
    # def test_push(self):
    #     self.git_code_manager.init()
    #     test_filepath = os.path.join(self.git_code_manager.filepath,
    #                                  "test.txt")
    #
    #     with open(test_filepath, "w") as f:
    #         f.write(to_unicode(str("test")))
    #     self.git_code_manager.add(test_filepath)
    #     self.git_code_manager.commit(["-m", "test"])
    #     if self.git_code_manager.git_host_manager.host == "github":
    #         self.git_code_manager.remote("add", "origin",
    #                                      "https://github.com/datmo/test.git")
    #     result = self.git_code_manager.push("origin", name="master")
    #     assert result == True

    # def test_pull(self):
    #     pass

    # Datmo refs
    def test_exist_code_refs_dir(self):
        self.git_code_manager.init()
        result = self.git_code_manager.exists_code_refs_dir()
        assert result == True
        dir = ".git/refs/datmo"
        shutil.rmtree(os.path.join(self.git_code_manager.filepath, dir))
        result = self.git_code_manager.exists_code_refs_dir()
        assert result == False

    def test_ensure_code_refs_dir(self):
        dir = ".git/refs/datmo"
        self.git_code_manager.init()
        result = self.git_code_manager.ensure_code_refs_dir()
        assert result == True and \
            os.path.isdir(os.path.join(
                self.git_code_manager.filepath,
                dir
            ))

    def test_delete_code_refs_dir(self):
        self.git_code_manager.init()
        result = self.git_code_manager.delete_code_refs_dir()
        assert result == True and \
            not os.path.isdir(
                os.path.join(self.git_code_manager.filepath,
                             ".git/refs/datmo")
            )

    def test_create_ref(self):
        self.git_code_manager.init()
        # Test failing case with no code_id and nothing to commit
        failed = False
        try:
            self.git_code_manager.create_ref()
        except GitCommitDoesNotExist:
            failed = True
        assert failed
        # Test passing case with no code_id
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        code_id = self.git_code_manager.create_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                     ".git/refs/datmo/", code_id)
        assert code_id and \
            os.path.isfile(code_ref_path)
        # Test error raised with commit_id
        random_commit_id = str("random")
        failed = False
        try:
            self.git_code_manager.\
                create_ref(commit_id=random_commit_id)
        except GitCommitDoesNotExist:
            failed = True
        assert failed

    def test_exists_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        code_id = self.git_code_manager.create_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                     ".git/refs/datmo/", code_id)
        result = self.git_code_manager.exists_ref(code_id)
        assert result == True and \
            os.path.isfile(code_ref_path)

    def test_delete_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        code_id = self.git_code_manager.create_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                     ".git/refs/datmo/", code_id)
        result = self.git_code_manager.delete_ref(code_id)
        assert result == True and \
            not os.path.isfile(code_ref_path)

    def test_list_refs(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        code_id = self.git_code_manager.create_ref()
        code_refs = self.git_code_manager.list_refs()
        assert code_refs and \
            code_id in code_refs

    # def test_push_ref(self):
    #     pass
    #
    # def test_fetch_ref(self):
    #     pass
    #
    def test_checkout_ref(self):
        # TODO: Test remote checkout
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test1")))
        # Create first ref
        ref_id_1 = self.git_code_manager.create_ref()
        with open(test_filepath, "w") as f:
            f.write(to_unicode(str("test2")))
        # Add random file to .datmo directory before next ref
        os.makedirs(os.path.join(self.git_code_manager.filepath, ".datmo"))
        random_filepath = os.path.join(self.git_code_manager.filepath,
                                       ".datmo", ".test")
        with open(random_filepath, "w") as f:
            f.write(to_unicode(str("test")))
        # Check to make sure .datmo/.test exists and has contents
        assert os.path.isfile(random_filepath) and \
               "test" in open(random_filepath, "r").read()
        # Create second ref
        ref_id_2 = self.git_code_manager.create_ref()
        # Checkout to previous ref, .datmo should be unaffected
        result = self.git_code_manager.checkout_ref(ref_id_1)

        # Check code was properly checked out
        assert ref_id_1 != ref_id_2
        assert result == True and \
            self.git_code_manager.latest_commit() == ref_id_1
        # Check to make sure .datmo is not affected
        assert os.path.isfile(random_filepath) and \
            "test" in open(random_filepath, "r").read()


class TestGitHostDriver():
    """
    Checks all functions of the GitHostDriver
    """

    def setup_class(self):
        self.netrc_temp_dir = tempfile.mkdtemp("netrc_test")
        self.ssh_temp_dir = tempfile.mkdtemp("ssh_test")

    def teardown_class(self):
        shutil.rmtree(os.path.join(self.netrc_temp_dir))
        shutil.rmtree(os.path.join(self.ssh_temp_dir))

    def test_netrc(self):
        hostm = GitHostDriver(self.netrc_temp_dir)
        assert hostm.create_git_netrc("foobar", "foo")
        hostm = GitHostDriver(self.netrc_temp_dir)
        assert os.path.exists(os.path.join(self.netrc_temp_dir, ".netrc"))
        assert hostm.https_enabled

    def test_ssh_git(self):
        hostm = GitHostDriver(self.ssh_temp_dir)
        assert hostm.ssh_enabled == False
        # If id_rsa already synced with remote account
        # if os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa"):
        #     shutil.copytree(
        #         os.path.join(os.path.expanduser("~"), ".ssh"),
        #         os.path.join(self.ssh_temp_dir,".ssh"))
        #     assert os.path.exists(os.path.join(self.ssh_temp_dir, ".ssh", "id_rsa"))
        #     hostm = GitHostDriver(self.ssh_temp_dir)
        #     assert hostm.ssh_enabled == True
