"""
Tests for git.py
"""
from __future__ import division
from __future__ import unicode_literals

import os
import shutil
import tempfile
from ..git import GitCodeManager, GitHostManager

class TestGitManager():
    """
    Checks all functions of the GitCodeManager
    """
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir="/tmp/")
        self.git_code_manager = GitCodeManager(filepath=self.temp_dir, execpath="git")

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_instantiation(self):
        assert self.git_code_manager != None

    def test_init(self):
        result = self.git_code_manager.init()
        assert result and \
               self.git_code_manager.is_initialized == True

    def test_init_then_instantiation(self):
        self.git_code_manager.init()
        another_git_code_manager = GitCodeManager(filepath=self.temp_dir, execpath="git")
        result = another_git_code_manager.is_initialized
        assert result == True

    def test_clone(self):
        result = self.git_code_manager.clone("https://github.com/datmo/hello-world.git")
        assert os.path.exists(os.path.join(self.temp_dir, "hello-world",'.git'))
        shutil.rmtree(os.path.join(self.temp_dir, "hello-world"))


    def test_clone_unsecure(self):
        result = self.git_code_manager.clone("https://github.com/datmo/hello-world.git", unsecure=True)
        assert os.path.exists(os.path.join(self.temp_dir, "hello-world",'.git'))
        shutil.rmtree(os.path.join(self.temp_dir, "hello-world"))


    def test_giturl_parse(self):
        parsed = self.git_code_manager._parse_git_url("https://github.com/datmo/hello-world.git")
        assert parsed == "git@github.com:datmo/hello-world.git"
        # git@github.com:gitpython-developers/GitPython.git
        # https://github.com/gitpython-developers/GitPython.git
        parsed = self.git_code_manager._parse_git_url("git://github.com/datmo/hello-world.git")
        assert parsed == "git@github.com:datmo/hello-world.git"

    def test_commit(self):
        # TODO: try out more options
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")

        with open(test_filepath, "wb") as f:
            f.write(str("test"))
        self.git_code_manager.add(test_filepath)
        result = self.git_code_manager.commit(['-m', 'test'])
        commit_id = self.git_code_manager.latest_commit()
        assert result == True and commit_id

    # def test_branch(self):
    #     pass

    # def test_checkout(self):
    #     pass

    # def test_stash_save(self):
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
    # def test_hash(self):
    #     pass
    #
    # def test_latest_commit(self):
    #     pass
    #
    def test_reset(self):
        self.git_code_manager.init()
        self.git_code_manager.commit(options=['-m', 'test'])
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
            result = self.git_code_manager.remote("add", "origin",
                                         "https://github.com/datmo/test.git")
            remote_url = self.git_code_manager.get_remote_url()
            assert result == True and \
                remote_url == "https://github.com/datmo/test.git"
            # Test remote set-url
            result = self.git_code_manager.remote("set-url", "origin",
                                         "https://github.com/datmo/test.git")
            remote_url = self.git_code_manager.get_remote_url()
            assert result == True and \
                remote_url == "https://github.com/datmo/test.git"

    def test_get_remote_url(self):
        self.git_code_manager.init()
        if self.git_code_manager.git_host_manager.host == "github.com":
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
    #     with open(test_filepath, "wb") as f:
    #         f.write(str("test"))
    #     self.git_code_manager.add(test_filepath)
    #     self.git_code_manager.commit(['-m', 'test'])
    #     if self.git_code_manager.git_host_manager.host == "github":
    #         self.git_code_manager.remote("add", "origin",
    #                                      "https://github.com/datmo/test.git")
    #     result = self.git_code_manager.push("origin", name="master")
    #     assert result == True

    # def test_pull(self):
    #     pass

    def test_check_gitignore_exists(self):
        self.git_code_manager.init()
        result = self.git_code_manager.check_gitignore_exists()
        assert result == True
        os.remove(os.path.join(self.git_code_manager.filepath, ".gitignore"))
        result = self.git_code_manager.check_gitignore_exists()
        assert result == False

    def test_ensure_gitignore_exists(self):
        self.git_code_manager.init()
        result = self.git_code_manager.ensure_gitignore_exists()
        assert result == True and \
            os.path.isfile(os.path.join(
                self.git_code_manager.filepath,
                ".gitignore"
            ))

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

    def test_create_code_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "wb") as f:
            f.write(str("test"))
        code_id = self.git_code_manager.create_code_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                   '.git/refs/datmo/',
                                     code_id)
        assert code_id and \
            os.path.isfile(code_ref_path)

    def test_exists_code_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "wb") as f:
            f.write(str("test"))
        code_id = self.git_code_manager.create_code_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                     '.git/refs/datmo/',
                                     code_id)
        result = self.git_code_manager.exists_code_ref(code_id)
        assert result == True and \
            os.path.isfile(code_ref_path)

    def test_delete_code_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "wb") as f:
            f.write(str("test"))
        code_id = self.git_code_manager.create_code_ref()
        code_ref_path = os.path.join(self.git_code_manager.filepath,
                                     '.git/refs/datmo/',
                                     code_id)
        result  = self.git_code_manager.delete_code_ref(code_id)
        assert result == True and \
            not os.path.isfile(code_ref_path)

    def test_list_code_refs(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "wb") as f:
            f.write(str("test"))
        code_id = self.git_code_manager.create_code_ref()
        code_refs = self.git_code_manager.list_code_refs()
        assert code_refs and \
            code_id in code_refs


    # def test_push_code_ref(self):
    #     pass
    #
    # def test_fetch_code_ref(self):
    #     pass
    #
    def test_checkout_code_ref(self):
        self.git_code_manager.init()
        test_filepath = os.path.join(self.git_code_manager.filepath,
                                     "test.txt")
        with open(test_filepath, "wb") as f:
            f.write(str("test1"))
        code_id_1 = self.git_code_manager.create_code_ref()
        with open(test_filepath, "wb") as f:
            f.write(str("test2"))
        _ = self.git_code_manager.create_code_ref()
        result = self.git_code_manager.checkout_code_ref(code_id_1)
        assert result ==  True and \
            self.git_code_manager.latest_commit() == code_id_1



class TestGitHostManager():
    """
    Checks all functions of the GitHostManager
    """
    def setup_class(self):
        self.netrc_temp_dir = tempfile.mkdtemp("netrc_test")
        self.ssh_temp_dir = tempfile.mkdtemp("ssh_test")

    def teardown_class(self):
        shutil.rmtree(os.path.join(self.netrc_temp_dir))
        shutil.rmtree(os.path.join(self.ssh_temp_dir))

    def test_netrc(self):
        hostm = GitHostManager(self.netrc_temp_dir)
        assert hostm.create_git_netrc('foobar','foo')
        hostm = GitHostManager(self.netrc_temp_dir)
        assert os.path.exists(os.path.join(self.netrc_temp_dir, ".netrc"))
        assert hostm.https_enabled

    def test_ssh_git(self):
        hostm = GitHostManager(self.ssh_temp_dir)
        assert hostm.ssh_enabled == False
        shutil.copytree(
            os.path.join(os.path.expanduser('~'), '.ssh'),
            os.path.join(self.ssh_temp_dir,'.ssh'))
        assert os.path.exists(os.path.join(self.ssh_temp_dir, ".ssh", 'id_rsa'))
        hostm = GitHostManager(self.ssh_temp_dir)
        assert hostm.ssh_enabled == True


