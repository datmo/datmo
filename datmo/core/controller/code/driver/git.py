import os
import shutil
import subprocess
import semver
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from giturlparse import parse

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (
    PathDoesNotExist, GitUrlArgumentException, GitExecutionException,
    FileIOException, GitCommitDoesNotExist, DatmoFolderInWorkTree)
from datmo.core.controller.code.driver import CodeDriver


class GitCodeDriver(CodeDriver):
    """
    TODO: Reimplement functions with robust library: https://github.com/gitpython-developers/GitPython

    This CodeDriver manages source control management for the project using git
    """

    def __init__(self, filepath, execpath, remote_url=None):
        super(GitCodeDriver, self).__init__()
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise PathDoesNotExist(
                __("error", "controller.code.driver.git.__init__.dne",
                   filepath))
        self.execpath = execpath
        # Check the execpath and the version
        try:
            p = subprocess.Popen(
                [self.execpath, "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.filepath)
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.__init__.giterror",
                       err))
            version = str(out.split()[2].split(".windows")[0])
            if not semver.match(version, ">=1.9.7"):
                raise GitExecutionException(
                    __("error",
                       "controller.code.driver.git.__init__.gitversion",
                       out.split()[2]))
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.__init__.giterror",
                   str(e)))

        # TODO: handle multiple remote urls
        self.git_host_manager = GitHostDriver()

        self._is_initialized = self.is_initialized

        if self._is_initialized:
            # If initialized ensure .datmo is not in working tree else error
            if self.exists_datmo_files_in_worktree():
                raise DatmoFolderInWorkTree(
                    __("error", "controller.code.driver.git.__init__.datmo"))
            # If initialized ensure .datmo is ignored (in .git/info/exclude)
            self.ensure_datmo_files_ignored()
            # If initialized update remote information
            if remote_url:
                self.remote("set-url", "origin", remote_url)
            self._remote_url = self.remote_url
            self._remote_access = False
        self.type = "git"

    @property
    def is_initialized(self):
        if os.path.isdir(os.path.join(self.filepath, ".git")) and \
                self.exists_code_refs_dir() and \
                self.exists_datmo_files_ignored():
            self._is_initialized = True
            return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    @property
    def remote_url(self):
        try:
            self._remote_url = self.get_remote_url()
        except GitExecutionException:
            self._remote_url = None
        return self._remote_url

    @property
    def remote_access(self):
        try:
            self._remote_access = self.push("origin", option="--dry-run")
        except Exception as e:
            if "403" in e or "git pull" in e:
                self._remote_access = False
            elif "no upstream branch" in e:
                self._remote_access = False
        return self._remote_access

    # Implemented functions for every CodeDriver

    def create_ref(self, commit_id=None):
        """Add remaining files, make a commit and add it to a datmo code ref

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is given, it will not add files and not create a commit

        Returns
        -------
        commit_id : str
            code id for the ref created

        Raises
        ------
        GitCommitDoesNotExist
            commit id specified does not match a valid commit within the tree
        """
        self.ensure_code_refs_dir()
        if not commit_id:
            # add files and commit changes on current branch
            self.add("-A")
            new_commit_bool = self.commit(
                options=["-m", "auto commit by datmo"])
            try:
                commit_id = self.latest_commit()
            except GitExecutionException as e:
                raise GitCommitDoesNotExist(
                    __("error",
                       "controller.code.driver.git.create_ref.cannot_commit",
                       str(e)))
            # revert back to the original commit
            if new_commit_bool:
                self.reset(commit_id)
        # writing git commit into ref if exists
        if not self.exists_commit(commit_id):
            raise GitCommitDoesNotExist(
                __("error", "controller.code.driver.git.create_ref.no_commit",
                   commit_id))
        code_ref_path = os.path.join(self.filepath, ".git/refs/datmo/",
                                     commit_id)
        with open(code_ref_path, "w") as f:
            f.write(to_unicode(commit_id))
        return commit_id

    def exists_ref(self, commit_id):
        code_ref_path = os.path.join(self.filepath, ".git/refs/datmo/",
                                     commit_id)
        if not os.path.isfile(code_ref_path):
            return False
        return True

    def delete_ref(self, commit_id):
        self.ensure_code_refs_dir()
        code_ref_path = os.path.join(self.filepath, ".git/refs/datmo/",
                                     commit_id)
        if not self.exists_ref(commit_id):
            raise FileIOException(
                __("error", "controller.code.driver.git.delete_ref"))
        os.remove(code_ref_path)
        return True

    def list_refs(self):
        self.ensure_code_refs_dir()
        code_refs_path = os.path.join(self.filepath, ".git/refs/datmo/")
        code_refs_list = os.listdir(code_refs_path)
        return code_refs_list

    # Datmo specific remote calls
    def push_ref(self, commit_id="*"):
        datmo_ref = "refs/datmo/" + commit_id
        datmo_ref_map = "+" + datmo_ref + ":" + datmo_ref
        try:
            return self.push("origin", name=datmo_ref_map)
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.push_ref", str(e)))

    def fetch_ref(self, commit_id):
        try:
            datmo_ref = "refs/datmo/" + commit_id
            datmo_ref_map = "+" + datmo_ref + ":" + datmo_ref
            success, err = self.fetch("origin", datmo_ref_map, option="-fup")
            if not success:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.fetch_ref",
                       (commit_id, err)))
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.fetch_ref",
                   (commit_id, str(e))))
        return True

    def checkout_ref(self, commit_id, remote=False):
        try:
            # Run checkout for the specific ref as usual
            if remote:
                self.fetch_ref(commit_id)
            datmo_ref = "refs/datmo/" + commit_id
            checkout_result = self.checkout(datmo_ref)
            return checkout_result
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.checkout_ref",
                   (commit_id, str(e))))

    def exists_datmo_files_ignored(self):
        exclude_file = os.path.join(self.filepath, ".git/info/exclude")
        try:
            if ".datmo" not in open(exclude_file, "r").read():
                return False
            else:
                return True
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.ensure_code_refs_dir",
                   str(e)))

    def ensure_datmo_files_ignored(self):
        exclude_file = os.path.join(self.filepath, ".git/info/exclude")
        try:
            if not self.exists_datmo_files_ignored():
                with open(exclude_file, "a") as f:
                    f.write(to_unicode("\n.datmo/*\n"))
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.ensure_code_refs_dir",
                   str(e)))
        return True

    def exists_datmo_files_in_worktree(self):
        try:
            result = subprocess.check_output(
                [self.execpath, "ls-files", "|", "grep", ".datmo"],
                cwd=self.filepath).strip()
            return True if result else False
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.init", str(e)))

    def init(self):
        try:
            subprocess.check_output(
                [self.execpath, "init",
                 str(self.filepath)], cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.init", str(e)))
        try:
            code_refs_success = self.ensure_code_refs_dir()
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.init.file", str(e)))
        try:
            datmo_files_ignored_success = self.ensure_datmo_files_ignored()
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.init.file", str(e)))
        return code_refs_success and datmo_files_ignored_success

    def clone(self, original_git_url, repo_name=None, mode="https"):
        clone_git_url = self._parse_git_url(original_git_url, mode=mode)

        if not repo_name:
            repo_name = clone_git_url.split("/")[-1][:-4]

        try:
            subprocess.check_output(
                [
                    self.execpath, "clone",
                    str(clone_git_url),
                    os.path.join(self.filepath, repo_name)
                ],
                cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.clone",
                   (original_git_url, str(e))))
        return True

    def _parse_git_url(self, original_git_url, mode="https"):
        if original_git_url[-4:] != ".git":
            original_git_url = original_git_url + ".git"
        p = parse(original_git_url)

        if not p.valid:
            raise GitUrlArgumentException(
                __("error", "controller.code.driver.git._parse_git_url.url",
                   original_git_url))
        if mode == "ssh":
            clone_git_url = p.url2ssh
        elif mode == "https":
            clone_git_url = p.url2https
        elif mode == "http":
            # If unsecured specified http connection used instead
            clone_git_url = "://".join(["http", p.url2https.split("://")[1]])
        else:
            raise GitUrlArgumentException(
                __("error", "controller.code.driver.git._parse_git_url.access",
                   original_git_url))
        return clone_git_url

    def add(self, filepath, option=None):
        try:
            if option:
                subprocess.check_output(
                    [self.execpath, "add", option, filepath],
                    cwd=self.filepath).strip()
            else:
                subprocess.check_output(
                    [self.execpath, "add", filepath],
                    cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.add",
                   (filepath, str(e))))
        return True

    def commit(self, options):
        """Git commit wrapper

        Parameters
        ----------
        options: list
            List of strings for the command (e.g. ["-m", "hello"])

        Returns
        -------
        bool
            True if new commit was created, False if no commit was created

        Raises
        ------
        GitExecutionException
            If any errors occur in running git
        """
        try:
            p = subprocess.Popen(
                [self.execpath, "commit"] + options,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.filepath)
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.commit",
                       (options, err)))
            elif "nothing" in out:
                return False
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.commit",
                   (options, str(e))))
        return True

    def exists_commit(self, commit_id):
        try:
            p = subprocess.Popen(
                [self.execpath, "show", commit_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.filepath)
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err or "fatal" in out:
                return False
        except Exception:
            return False
        return True

    def branch(self, name, option=None):
        try:
            if option:
                subprocess.check_output(
                    [self.execpath, "branch", option, name],
                    cwd=self.filepath).strip()
            else:
                subprocess.check_output(
                    [self.execpath, "branch", name],
                    cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.branch",
                   (name, str(e))))
        return True

    def checkout(self, name, option=None):
        try:
            if option:
                subprocess.check_output(
                    [self.execpath, "checkout", option, name],
                    cwd=self.filepath).strip()
            else:
                subprocess.check_output(
                    [self.execpath, "checkout", name],
                    cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.checkout",
                   (name, str(e))))
        return True

    def stash_save(self, message=None):
        # TODO: Test this function
        try:
            if message:
                subprocess.check_output(
                    [self.execpath, "stash", "save", message],
                    cwd=self.filepath).strip()
            else:
                subprocess.check_output(
                    [self.execpath, "stash"], cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.stash_save", str(e)))
        return True

    def stash_list(self, regex="datmo"):
        # TODO: Test this function
        try:
            git_stash_list = subprocess.check_output(
                [
                    self.execpath, "stash", "list", "|", "grep",
                    """ + regex + """
                ],
                cwd=self.filepath)
            git_stash_list = git_stash_list.decode().strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.stash_list", str(e)))
        return git_stash_list

    def stash_pop(self, regex=None):
        # TODO: Test this function
        try:
            if regex:
                git_stash_pop = subprocess.check_output(
                    [self.execpath, "stash", "pop", "stash^{/" + regex + "}"],
                    cwd=self.filepath)
                git_stash_pop = git_stash_pop.decode().strip()
            else:
                git_stash_pop = subprocess.check_output(
                    [self.execpath, "stash", "pop"], cwd=self.filepath)
                git_stash_pop = git_stash_pop.decode().strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.stash_pop", str(e)))
        return git_stash_pop

    def stash_apply(self, regex=None):
        # TODO: Test this function
        try:
            if regex:
                git_stash_apply = subprocess.check_output(
                    [
                        self.execpath, "stash", "apply",
                        "stash^{/" + regex + "}"
                    ],
                    cwd=self.filepath)
                git_stash_apply = git_stash_apply.decode().strip()
            else:
                git_stash_apply = subprocess.check_output(
                    [self.execpath, "stash", "apply", "stash^{0}"],
                    cwd=self.filepath)
                git_stash_apply = git_stash_apply.decode().strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.stash_apply", str(e)))
        return git_stash_apply

    def latest_commit(self):
        try:
            git_commit = subprocess.check_output(
                [self.execpath, "log", "--format=%H", "-n", "1"],
                cwd=self.filepath)
            git_commit = git_commit.decode().strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.latest_commit",
                   str(e)))
        return git_commit

    def reset(self, git_commit):
        try:
            subprocess.check_output(
                [self.execpath, "reset", git_commit],
                cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.reset", str(e)))
        return True

    def check_git_work_tree(self):
        try:
            git_work_tree_exists = subprocess.check_output(
                [self.execpath, "rev-parse", "--is-inside-work-tree"],
                cwd=self.filepath)
            git_work_tree_exists = git_work_tree_exists.decode().strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.check_git_work_tree",
                   str(e)))
        return True if git_work_tree_exists == "true" else False

    def remote(self, mode, origin, git_url):
        # TODO: handle multiple remote urls
        try:
            if mode == "set-url":
                p = subprocess.Popen(
                    [self.execpath, "remote", "set-url", origin, git_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.filepath)
                out, err = p.communicate()
                out, err = out.decode(), err.decode()
            elif mode == "add":
                p = subprocess.Popen(
                    [self.execpath, "remote", "add", origin, git_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.filepath)
                out, err = p.communicate()
                out, err = out.decode(), err.decode()
            else:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.remote",
                       (mode, origin, git_url, "Incorrect mode specified")))
            if err:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.remote",
                       (mode, origin, git_url, err)))
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.remote",
                   (mode, origin, git_url, str(e))))
        return True

    def get_remote_url(self):
        try:
            # TODO: handle multiple remote urls
            git_url = subprocess.check_output(
                [self.execpath, "config", "--get", "remote.origin.url"],
                cwd=self.filepath)
            git_url = git_url.decode().strip()
        except Exception as e:
            # TODO: handle error vs. empty response properly
            return None
            # raise GitExecutionException(__("error",
            #                                 "controller.code.driver.git.get_remote_url",
            #                                 str(e)))
        return git_url

    def fetch(self, origin, name, option=None):
        try:
            if option:
                subprocess.check_output(
                    [self.execpath, "fetch", option, origin, name],
                    cwd=self.filepath).strip()
            else:
                subprocess.check_output(
                    [self.execpath, "fetch", origin, name],
                    cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.fetch",
                   (origin, name, str(e))))
        return True

    def push(self, origin, option=None, name=None):
        try:
            if option:
                if name:
                    p = subprocess.Popen(
                        [self.execpath, "push", option, origin, name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.filepath)
                    out, err = p.communicate()
                    out, err = out.decode(), err.decode()
                else:
                    p = subprocess.Popen(
                        [self.execpath, "push", option, origin],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.filepath)
                    out, err = p.communicate()
                    out, err = out.decode(), err.decode()
            else:
                if name:
                    p = subprocess.Popen(
                        [self.execpath, "push", origin, name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.filepath)
                    out, err = p.communicate()
                    out, err = out.decode(), err.decode()
                else:
                    p = subprocess.Popen(
                        [self.execpath, "push", origin],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=self.filepath)
                    out, err = p.communicate()
                    out, err = out.decode(), err.decode()
            if err:
                raise GitExecutionException(
                    __("error", "controller.code.driver.git.push",
                       (origin, err)))
        except Exception as e:
            raise GitExecutionException(
                __("error", "controller.code.driver.git.push",
                   (origin, str(e))))
        return True

    def pull(self):
        pass

    # Datmo Code Refs

    def exists_code_refs_dir(self):
        dir = ".git/refs/datmo"
        if not os.path.isdir(os.path.join(self.filepath, dir)):
            return False
        return True

    def ensure_code_refs_dir(self):
        dir = ".git/refs/datmo"
        try:
            if not os.path.isdir(os.path.join(self.filepath, dir)):
                os.makedirs(os.path.join(self.filepath, dir))
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.ensure_code_refs_dir",
                   str(e)))
        return True

    def delete_code_refs_dir(self):
        dir = ".git/refs/datmo"
        dir_path = os.path.join(self.filepath, dir)
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            raise FileIOException(
                __("error", "controller.code.driver.git.delete_code_refs_dir",
                   str(e)))
        return True


class GitHostDriver(object):
    def __init__(self, home=os.path.expanduser("~"), host="github"):
        self.home = home
        if host == "github":
            self.host = "github.com"
        else:
            self.host = "unknown"
        self._ssh_enabled = self._check_for_ssh()
        self._https_enabled = self._check_https_enabled()

    @property
    def ssh_enabled(self):
        return self._ssh_enabled

    @property
    def https_enabled(self):
        return self._https_enabled

    def _check_https_enabled(self):
        # TODO: try connecting to github using .netrc
        return self._netrc_exists()

    def _netrc_exists(self):
        netrc_filepath = os.path.join(self.home, ".netrc")
        if os.path.exists(netrc_filepath):
            if self.host in open(netrc_filepath).read():
                return True
        else:
            return False

    def _check_for_ssh(self):
        cmd = "ssh-keyscan %s >> ~/.ssh/known_hosts" % (self.host)
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.home)
        out, err = p.communicate()
        out, err = out.decode(), err.decode()
        if "Error" in out or "Error" in err or "denied" in err:
            self._ssh_enabled = False
        cmd = "ssh -i %s/.ssh/id_rsa -T git@%s" % (self.home, self.host)
        p = subprocess.Popen(
            str(cmd),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.home)
        out, err = p.communicate()
        out, err = out.decode(), err.decode()
        error_strings = [
            "Error", "denied", "Could not resolve hostname", "not accessible"
        ]
        for err_str in error_strings:
            if err_str in err or err_str in out:
                return False
        return True

    def create_git_netrc(self, username, password):
        netrc_filepath = os.path.join(self.home, ".netrc")
        netrc_file = open(netrc_filepath, "w")
        netrc_file.truncate()
        netrc_file.write(to_unicode("machine %s" % (self.host)))
        netrc_file.write(to_unicode("\n"))
        netrc_file.write(to_unicode("login " + str(username)))
        netrc_file.write(to_unicode("\n"))
        netrc_file.write(to_unicode("password " + str(password)))
        netrc_file.write(to_unicode("\n"))
        netrc_file.close()
        return True

    def read_git_netrc(self):
        netrc_filepath = os.path.join(self.home, ".netrc")
        if not os.path.exists(netrc_filepath):
            return {"login": None, "password": None}
        netrc_file = open(netrc_filepath, "r")
        file_content = netrc_file.read()
        lines = file_content.split("\n")
        initial_index = lines.index("machine %s" % (self.host))
        login = lines[initial_index + 1].split(" ")[-1]
        password = lines[initial_index + 2].split(" ")[-1]
        return {
            "login": login if login else None,
            "password": password if password else None
        }
