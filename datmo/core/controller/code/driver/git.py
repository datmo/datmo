import os
import shutil
import subprocess
import semver
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")
from giturlparse import parse

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (
    PathDoesNotExist, GitUrlArgumentError, GitExecutionError, FileIOError,
    CommitDoesNotExist, CommitFailed, DatmoFolderInWorkTree, UnstagedChanges)
from datmo.core.controller.code.driver import CodeDriver
from datmo.config import Config


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
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.__init__.giterror",
                       err))
            version = str(out.split()[2].split(".windows")[0])
            if not semver.match(version, ">=1.9.7"):
                raise GitExecutionError(
                    __("error",
                       "controller.code.driver.git.__init__.gitversion",
                       out.split()[2]))
        except Exception as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.__init__.giterror",
                   str(e)))

        # TODO: handle multiple remote urls
        # self.git_host_driver = GitHostDriver()
        self.remote_url = remote_url

        self._is_initialized = self.is_initialized

        if self._is_initialized:
            # If initialized ensure .datmo is not in working tree else error
            if self.exists_datmo_files_in_worktree():
                raise DatmoFolderInWorkTree(
                    __("error", "controller.code.driver.git.__init__.datmo"))
            # If initialized ensure .datmo is ignored (in .git/info/exclude)
            self.ensure_datmo_files_ignored()
            # If initialized update remote information
            # if remote_url:
            #     self.remote("set-url", "origin", remote_url)
            # self._remote_url = self.remote_url
            # self._remote_access = False
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

    # @property
    # def remote_url(self):
    #     try:
    #         self._remote_url = self.get_remote_url()
    #     except GitExecutionError:
    #         self._remote_url = None
    #     return self._remote_url

    # @property
    # def remote_access(self):
    #     try:
    #         self._remote_access = self.push("origin", option="--dry-run")
    #     except Exception as e:
    #         if "403" in e or "git pull" in e:
    #             self._remote_access = False
    #         elif "no upstream branch" in e:
    #             self._remote_access = False
    #     return self._remote_access

    def init(self):
        try:
            process = subprocess.Popen(
                [self.execpath, "init",
                 str(self.filepath)],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.init",
                       str(stderr)))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.init", str(e)))
        try:
            code_refs_success = self.ensure_code_refs_dir()
        except Exception as e:
            raise FileIOError(
                __("error", "controller.code.driver.git.init.file", str(e)))
        try:
            datmo_files_ignored_success = self.ensure_datmo_files_ignored()
        except Exception as e:
            raise FileIOError(
                __("error", "controller.code.driver.git.init.file", str(e)))
        return code_refs_success and datmo_files_ignored_success

    # Implemented functions for every CodeDriver

    def current_hash(self):
        self.check_unstaged_changes()
        return self.latest_commit()

    def create_ref(self, commit_id=None):
        """Add remaining files, make a commit and add it to a datmo code ref

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is given, it will not add files and not create a commit

        Returns
        -------
        commit_id : str
            commit id for the ref created

        Raises
        ------
        CommitDoesNotExist
            commit id specified does not match a valid commit within the tree
        CommitFailed
            commit could not be created
        """
        self.ensure_code_refs_dir()
        if not commit_id:
            try:
                _ = self.latest_commit()
                message = "auto commit by datmo"
            except Exception:
                message = "auto initial commit by datmo"
            # add files and commit changes on current branch
            self.add("-A")
            _ = self.commit(options=["-m", message])
            try:
                commit_id = self.latest_commit()
            except GitExecutionError as e:
                raise CommitFailed(
                    __("error",
                       "controller.code.driver.git.create_ref.cannot_commit",
                       str(e)))
        # writing git commit into ref if exists
        if not self.exists_commit(commit_id):
            raise CommitDoesNotExist(
                __("error", "controller.code.driver.git.create_ref.no_commit",
                   commit_id))
        # git refs for datmo for the latest commit id is created
        code_ref_path = os.path.join(self.filepath, ".git/refs/datmo/",
                                     commit_id)
        with open(code_ref_path, "wb") as f:
            f.write(to_bytes(commit_id))
        return commit_id

    def latest_ref(self):
        def getmtime(absolute_filepath):
            # Keeping it granular as timestaps in git
            return int(os.path.getmtime(absolute_filepath))

        code_refs_path = os.path.join(self.filepath, ".git/refs/datmo/")
        sorted_code_refs = sorted(
            [
                os.path.join(code_refs_path, filename)
                for filename in os.listdir(code_refs_path)
            ],
            key=getmtime,
            reverse=True)
        _, filename = os.path.split(sorted_code_refs[0])
        return filename

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
            raise FileIOError(
                __("error", "controller.code.driver.git.delete_ref"))
        os.remove(code_ref_path)
        return True

    def list_refs(self):
        self.ensure_code_refs_dir()
        code_refs_path = os.path.join(self.filepath, ".git/refs/datmo/")
        code_refs_list = os.listdir(code_refs_path)
        return code_refs_list

    # Datmo specific remote calls
    # def push_ref(self, commit_id="*"):
    #     datmo_ref = "refs/datmo/" + commit_id
    #     datmo_ref_map = "+" + datmo_ref + ":" + datmo_ref
    #     try:
    #         return self.push("origin", name=datmo_ref_map)
    #     except Exception as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.push_ref", str(e)))
    #
    # def fetch_ref(self, commit_id):
    #     try:
    #         datmo_ref = "refs/datmo/" + commit_id
    #         datmo_ref_map = "+" + datmo_ref + ":" + datmo_ref
    #         success, err = self.fetch("origin", datmo_ref_map, option="-fup")
    #         if not success:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.fetch_ref",
    #                    (commit_id, err)))
    #     except Exception as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.fetch_ref",
    #                (commit_id, str(e))))
    #     return True

    def checkout_ref(self, commit_id):
        try:
            # Run checkout for the specific ref as usual
            datmo_ref = "refs/datmo/" + commit_id
            checkout_result = self.checkout(datmo_ref)
            return checkout_result
        except Exception as e:
            raise GitExecutionError(
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
            raise FileIOError(
                __("error", "controller.code.driver.git.ensure_code_refs_dir",
                   str(e)))

    def ensure_datmo_files_ignored(self):
        exclude_file = os.path.join(self.filepath, ".git/info/exclude")
        try:
            if not self.exists_datmo_files_ignored():
                with open(exclude_file, "ab") as f:
                    f.write(
                        to_bytes("%s.datmo/*%s" % (os.linesep, os.linesep)))
        except Exception as e:
            raise FileIOError(
                __("error", "controller.code.driver.git.ensure_code_refs_dir",
                   str(e)))
        return True

    def exists_datmo_files_in_worktree(self):
        try:
            process = subprocess.Popen(
                [self.execpath, "ls-files", "|", "grep", ".datmo"],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.init",
                       str(stderr)))
            result = stdout.decode().strip()
            return True if result else False
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.init", str(e)))

    # def clone(self, original_git_url, repo_name=None, mode="https"):
    #     clone_git_url = self._parse_git_url(original_git_url, mode=mode)
    #
    #     if not repo_name:
    #         repo_name = clone_git_url.split("/")[-1][:-4]
    #
    #     try:
    #         process = subprocess.Popen(
    #             [
    #                 self.execpath, "clone",
    #                 str(clone_git_url),
    #                 os.path.join(self.filepath, repo_name)
    #             ],
    #             cwd=self.filepath,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.clone",
    #                    (original_git_url, str(stderr))))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.clone",
    #                (original_git_url, str(e))))
    #     return True

    def _parse_git_url(self, original_git_url, mode="https"):
        if original_git_url[-4:] != ".git":
            original_git_url = original_git_url + ".git"
        p = parse(original_git_url)

        if not p.valid:
            raise GitUrlArgumentError(
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
            raise GitUrlArgumentError(
                __("error", "controller.code.driver.git._parse_git_url.access",
                   original_git_url))
        return clone_git_url

    def add(self, filepath, option=None):
        try:
            if option:
                process = subprocess.Popen(
                    [self.execpath, "add", option, filepath],
                    cwd=self.filepath,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    [self.execpath, "add", filepath],
                    cwd=self.filepath,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.add",
                       (filepath, str(stderr))))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
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
        GitExecutionError
            If any errors occur in running git
        """
        try:
            process = subprocess.Popen(
                [self.execpath, "commit"] + options,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.filepath)
            stdout, stderr = process.communicate()
            stdout, stderr = stdout.decode(), stderr.decode()
            if "nothing" in stdout:
                return False
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.commit",
                       (options, stderr)))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.commit",
                   (options, str(e))))
        return True

    def exists_commit(self, commit_id):
        try:
            process = subprocess.Popen(
                [self.execpath, "show", commit_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.filepath)
            stdout, stderr = process.communicate()
            if process.returncode > 0 or "fatal" in str(stdout):
                return False
        except subprocess.CalledProcessError:
            return False
        return True

    # def branch(self, name, option=None):
    #     try:
    #         if option:
    #             process = subprocess.Popen(
    #                 [self.execpath, "branch", option, name],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         else:
    #             process = subprocess.Popen(
    #                 [self.execpath, "branch", name],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.branch",
    #                    (name, str(stderr))))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.branch",
    #                (name, str(e))))
    #     return True

    def check_unstaged_changes(self):
        """Checks if there exists any unstaged changes for code

        Raises
        ------
        UnstagedChanges
            error if not there exists unstaged changes in environment

        GitExecutionError
            error if there exists any error while using git

        """
        try:
            process = subprocess.Popen(
                [self.execpath, "status"],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.status",
                       str(stderr)))
            stdout = stdout.decode().strip()
            if "clean" not in stdout:
                raise UnstagedChanges()
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.status", str(e)))
        return False

    def checkout(self, name, option=None):
        try:
            if option:
                process = subprocess.Popen(
                    [self.execpath, "checkout", option, name],
                    cwd=self.filepath,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            else:
                process = subprocess.Popen(
                    [self.execpath, "checkout", name],
                    cwd=self.filepath,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.checkout",
                       (name, str(stderr))))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.checkout",
                   (name, str(e))))
        return True

    # def stash_save(self, message=None):
    #     # TODO: Test this function
    #     try:
    #         if message:
    #             process = subprocess.Popen(
    #                 [self.execpath, "stash", "save", message],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         else:
    #             process = subprocess.Popen(
    #                 [self.execpath, "stash"],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.stash_save",
    #                    str(stderr)))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.stash_save", str(e)))
    #     return True
    #
    # def stash_list(self, regex="datmo"):
    #     # TODO: Test this function
    #     try:
    #         process = subprocess.Popen(
    #             [
    #                 self.execpath, "stash", "list", "|", "grep",
    #                 """ + regex + """
    #             ],
    #             cwd=self.filepath,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.stash_list",
    #                    str(stderr)))
    #         git_stash_list = stdout.decode().strip()
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.stash_list", str(e)))
    #     return git_stash_list
    #
    # def stash_pop(self, regex=None):
    #     # TODO: Test this function
    #     try:
    #         if regex:
    #             process = subprocess.Popen(
    #                 [self.execpath, "stash", "pop", "stash^{/" + regex + "}"],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         else:
    #             process = subprocess.Popen(
    #                 [self.execpath, "stash", "pop"],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.stash_pop",
    #                    str(stderr)))
    #         git_stash_pop = stdout.decode().strip()
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.stash_pop", str(e)))
    #     return git_stash_pop
    #
    # def stash_apply(self, regex=None):
    #     # TODO: Test this function
    #     try:
    #         if regex:
    #             process = subprocess.Popen(
    #                 [
    #                     self.execpath, "stash", "apply",
    #                     "stash^{/" + regex + "}"
    #                 ],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         else:
    #             process = subprocess.Popen(
    #                 [self.execpath, "stash", "apply", "stash^{0}"],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.stash_apply",
    #                    str(stderr)))
    #         git_stash_apply = stdout.decode().strip()
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.stash_apply", str(e)))
    #     return git_stash_apply

    def latest_commit(self):
        try:
            process = subprocess.Popen(
                [self.execpath, "log", "--format=%H", "-n", "1"],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.latest_commit",
                       str(stderr)))
            git_commit = stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.latest_commit",
                   str(e)))
        return git_commit

    def reset(self, git_commit):
        try:
            process = subprocess.Popen(
                [self.execpath, "reset", git_commit],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            _ = stdout.decode().strip()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error", "controller.code.driver.git.reset",
                       str(stderr)))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.reset", str(e)))
        return True

    def check_git_work_tree(self):
        try:
            process = subprocess.Popen(
                [self.execpath, "rev-parse", "--is-inside-work-tree"],
                cwd=self.filepath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            git_work_tree_exists = stdout.decode().strip()
            if process.returncode > 0:
                raise GitExecutionError(
                    __("error",
                       "controller.code.driver.git.check_git_work_tree",
                       str(stderr)))
        except subprocess.CalledProcessError as e:
            raise GitExecutionError(
                __("error", "controller.code.driver.git.check_git_work_tree",
                   str(e)))
        return True if git_work_tree_exists == "true" else False

    # def remote(self, mode, origin, git_url):
    #     # TODO: handle multiple remote urls
    #     try:
    #         if mode == "set-url":
    #             process = subprocess.Popen(
    #                 [self.execpath, "remote", "set-url", origin, git_url],
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 cwd=self.filepath)
    #             stdout, stderr = process.communicate()
    #             stdout, stderr = stdout.decode(), stderr.decode()
    #         elif mode == "add":
    #             process = subprocess.Popen(
    #                 [self.execpath, "remote", "add", origin, git_url],
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 cwd=self.filepath)
    #             stdout, stderr = process.communicate()
    #             stdout, stderr = stdout.decode(), stderr.decode()
    #         else:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.remote",
    #                    (mode, origin, git_url, "Incorrect mode specified")))
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.remote",
    #                    (mode, origin, git_url, stderr)))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.remote",
    #                (mode, origin, git_url, str(e))))
    #     return True

    # def get_remote_url(self):
    #     try:
    #         # TODO: handle multiple remote urls
    #         process = subprocess.Popen(
    #             [self.execpath, "config", "--get", "remote.origin.url"],
    #             cwd=self.filepath,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             return None
    #             # raise GitExecutionError(__("error",
    #             #                                 "controller.code.driver.git.get_remote_url",
    #             #                                 str(stderr)))
    #         git_url = stdout.decode().strip()
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.get_remote_url",
    #                str(e)))
    #     return git_url

    # def fetch(self, origin, name, option=None):
    #     try:
    #         if option:
    #             process = subprocess.Popen(
    #                 [self.execpath, "fetch", option, origin, name],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         else:
    #             process = subprocess.Popen(
    #                 [self.execpath, "fetch", origin, name],
    #                 cwd=self.filepath,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE)
    #         stdout, stderr = process.communicate()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.fetch",
    #                    (origin, name, str(stderr))))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.fetch",
    #                (origin, name, str(e))))
    #     return True
    #
    # def push(self, origin, option=None, name=None):
    #     try:
    #         if option:
    #             if name:
    #                 process = subprocess.Popen(
    #                     [self.execpath, "push", option, origin, name],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE,
    #                     cwd=self.filepath)
    #             else:
    #                 process = subprocess.Popen(
    #                     [self.execpath, "push", option, origin],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE,
    #                     cwd=self.filepath)
    #         else:
    #             if name:
    #                 process = subprocess.Popen(
    #                     [self.execpath, "push", origin, name],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE,
    #                     cwd=self.filepath)
    #             else:
    #                 process = subprocess.Popen(
    #                     [self.execpath, "push", origin],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE,
    #                     cwd=self.filepath)
    #         stdout, stderr = process.communicate()
    #         stdout, stderr = stdout.decode(), stderr.decode()
    #         if process.returncode > 0:
    #             raise GitExecutionError(
    #                 __("error", "controller.code.driver.git.push",
    #                    (origin, stderr)))
    #     except subprocess.CalledProcessError as e:
    #         raise GitExecutionError(
    #             __("error", "controller.code.driver.git.push",
    #                (origin, str(e))))
    #     return True
    #
    # def pull(self):
    #     pass

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
            raise FileIOError(
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
            raise FileIOError(
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

    @Config.cache_setting(
        key="git.ssh_enabled", expires_min=1440, ignore_values=[False])
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
        netrc_file = open(netrc_filepath, "wb")
        netrc_file.truncate()
        netrc_file.write(to_bytes("machine %s" % (self.host)))
        netrc_file.write(to_bytes(os.linesep))
        netrc_file.write(to_bytes("login " + str(username)))
        netrc_file.write(to_bytes(os.linesep))
        netrc_file.write(to_bytes("password " + str(password)))
        netrc_file.write(to_bytes(os.linesep))
        netrc_file.close()
        return True

    def read_git_netrc(self):
        netrc_filepath = os.path.join(self.home, ".netrc")
        if not os.path.exists(netrc_filepath):
            return {"login": None, "password": None}
        netrc_file = open(netrc_filepath, "r")
        file_content = netrc_file.read()
        lines = file_content.split(os.linesep)
        initial_index = lines.index("machine %s" % (self.host))
        login = lines[initial_index + 1].split(" ")[-1]
        password = lines[initial_index + 2].split(" ")[-1]
        return {
            "login": login if login else None,
            "password": password if password else None
        }
