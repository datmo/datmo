import os
import shutil
import subprocess
import semver
import hashlib
from giturlparse import parse

from datmo.util.exceptions import DoesNotExistException,\
    GitUrlArgumentException, GitExecutionException, \
    FileIOException

class GitCodeManager(object):
    """
    TODO: Reimplement functions with robust library: https://github.com/gitpython-developers/GitPython

    Git Code Manager for Project Code
    """

    def __init__(self, filepath, execpath, remote_url=None):
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise DoesNotExistException("exception.code_driver.git", {
                "filepath": filepath,
                "exception": "File path does not exist"
            })
        self.execpath = execpath
        # Check the execpath and the version
        p = subprocess.Popen([self.execpath, 'version'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=self.filepath)
        out, err = p.communicate()
        if err:
            raise GitExecutionException("exception.code_driver.git", {
                "exception": err
            })
        if not semver.match(out.split()[2], ">=1.9.7"):
            raise GitExecutionException("exception.code_driver.git", {
                "git version": out.split()[2],
                "exception": "Git version must be later than 1.9.7"
            })

        # TODO: handle multiple remote urls
        self.git_host_manager = GitHostManager()

        self._is_initialized = self.is_initialized

        if self._is_initialized:
            if remote_url:
                self.remote("set-url", "origin", remote_url)
            self._remote_url = self.remote_url
            self._remote_access = False
        self.type = "git"

    @property
    def is_initialized(self):
        if os.path.isdir(os.path.join(self.filepath, ".git")):
            try:
                git_dir = self.get_absolute_git_dir()
            except:
                git_dir = ""
            if os.path.join(self.filepath, ".git") in git_dir:
                if self.exists_code_refs_dir():
                    if self.check_gitignore_exists():
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
            self._remote_access = self.push('origin', option='--dry-run')
        except Exception as e:
            if '403' in e or 'git pull' in e:
                self._remote_access = False
            elif 'no upstream branch' in e:
                self._remote_access = False
        return self._remote_access

    def init(self):
        try:
            subprocess.check_output([self.execpath, 'init', str(self.filepath)]).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.init", {
                "exception": e
            })
        try:
            self.ensure_code_refs_dir()
            self.ensure_gitignore_exists()
        except Exception as e:
            raise FileIOException("exception.code_driver.git.init", {
                "exception": e
            })
        return True

    def clone(self, original_git_url, repo_name=None, unsecure=False):
        clone_git_url = self._parse_git_url(original_git_url, unsecure)

        if not repo_name:
            repo_name = clone_git_url.split('/')[-1][:-4]

        try:
            subprocess.check_output([self.execpath, 'clone', str(clone_git_url),
                                     os.path.join(self.filepath, repo_name)]).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.clone", {
                "original_git_url": original_git_url,
                "exception": e
            })
        return True

    def _parse_git_url(self, original_git_url, unsecure=False):
        if original_git_url[-4:] != ".git":
            original_git_url = original_git_url + ".git"
        p = parse(original_git_url)

        if not p.valid:
            raise GitUrlArgumentException("exception.code_driver.git._parse_git_url.not_valid", {
                "original_git_url": original_git_url
            })

        if self.git_host_manager.ssh_enabled:
            clone_git_url = p.url2ssh
        elif self.git_host_manager.https_enabled:
            clone_git_url = p.url2https
        else:
            raise GitUrlArgumentException("exception.code_driver.git._parse_git_url.mode_unrecognized", {
                "original_git_url": original_git_url
            })

        if unsecure:
            # If unsecured specified http connection used instead
            clone_git_url = '://'.join(['http', p.url2https.split('://')[1]])

        return clone_git_url

    def add(self, filepath):
        try:
            subprocess.check_output([self.execpath, 'add', filepath],
                                cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.add", {
                "filepath": filepath,
                "execpath": self.execpath,
                "exception": e
            })
        return True

    def commit(self, options):
        """
        Git commit wrapper

        Args:
            options: list of options, e.g. ['-m', 'hello']

        Returns:
            True for success
        """
        try:
            p = subprocess.Popen([self.execpath, 'commit'] + options,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=self.filepath)
            out, err = p.communicate()
            if err:
                raise GitExecutionException("exception.code_driver.git.commit", {
                    "options": options,
                    "exception": err
                })
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.commit", {
                "options": options,
                "exception": e
            })
        return True

    def branch(self, name, option=None):
        try:
            if option:
                subprocess.check_output([self.execpath, 'branch', option, name],
                                                cwd=self.filepath).strip()
            else:
                subprocess.check_output([self.execpath, 'branch', name],
                                                cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.branch", {
                "name": name,
                "exception": e
            })
        return True

    def checkout(self, name, option=None):
        try:
            if option:
                subprocess.check_output([self.execpath, 'checkout', option, name],
                                            cwd=self.filepath).strip()
            else:
                subprocess.check_output([self.execpath, 'checkout', name],
                                            cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.checkout", {
                "name": name,
                "exception": e
            })
        return True

    def stash_save(self, message=None):
        # TODO: Test this function
        try:
            if message:
                subprocess.check_output([self.execpath, 'stash', 'save', message],
                                        cwd=self.filepath).strip()
            else:
                subprocess.check_output([self.execpath, 'stash'],
                                        cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.stash_save", {
                "exception": e
            })
        return True

    def stash_list(self, regex='datmo'):
        # TODO: Test this function
        try:
            git_stash_list = subprocess.check_output([self.execpath, 'stash', 'list', '|',
                                                      'grep', '"' + regex + '"'],
                                                     cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.stash_list", {
                "exception": e
            })
        return git_stash_list

    def stash_pop(self, regex=None):
        # TODO: Test this function
        try:
            if regex:
                git_stash_pop = subprocess.check_output([self.execpath, 'stash', 'pop', 'stash^{/'+regex+'}'],
                                                        cwd=self.filepath).strip()
            else:
                git_stash_pop = subprocess.check_output([self.execpath, 'stash', 'pop'],
                                                        cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.stash_pop", {
                "exception": e
            })
        return git_stash_pop

    def stash_apply(self, regex=None):
        # TODO: Test this function
        try:
            if regex:
                git_stash_apply = subprocess.check_output([self.execpath,'stash', 'apply', 'stash^{/'+regex+'}'],
                                                          cwd=self.filepath).strip()
            else:
                git_stash_apply = subprocess.check_output([self.execpath,'stash', 'apply', 'stash^{0}'],
                                                          cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.stash_apply", {
                "exception": e
            })
        return git_stash_apply

    def hash(self, command, branch):
        try:
            result = subprocess.check_output([self.execpath, command, branch],
                                             cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.hash", {
                "command": command,
                "branch": branch,
                "exception": e
            })
        return result

    def latest_commit(self):
        try:
            git_commit = subprocess.check_output([self.execpath, 'log', '--format=%H', '-n' , '1'],
                                                 cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.latest_commit", {
                "exception": e
            })
        return git_commit

    def reset(self, git_commit):
        try:
            subprocess.check_output([self.execpath,'reset', git_commit],
                                    cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.reset", {
                "exception": e
            })
        return True

    def get_absolute_git_dir(self):
        try:
            git_dir = subprocess.check_output([self.execpath,'rev-parse', '--absolute-git-dir'],
                                                           cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.get_git_dir", {
                "exception": e
            })
        return git_dir

    def check_git_work_tree(self):
        try:
            git_work_tree_exists = subprocess.check_output([self.execpath,'rev-parse', '--is-inside-work-tree'],
                                                           cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.check_git_work_tree", {
                "exception": e
            })
        return True if git_work_tree_exists == "true" else False

    def remote(self, mode, origin, git_url):
        # TODO: handle multiple remote urls
        try:
            if mode == "set-url":
                p = subprocess.Popen([self.execpath, 'remote',  'set-url', origin, git_url],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=self.filepath)
                out, err = p.communicate()
            elif mode == "add":
                p = subprocess.Popen([self.execpath, 'remote', 'add', origin, git_url],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     cwd=self.filepath)
                out, err = p.communicate()
            else:
                raise GitExecutionException("exception.code_driver.git.remote", {
                    "mode": mode,
                    "origin": origin,
                    "git_url": git_url,
                    "exception": "Incorrect mode specified"
                })
            if err:
                raise GitExecutionException("exception.code_driver.git.remote", {
                    "mode": mode,
                    "origin": origin,
                    "git_url": git_url,
                    "exception": err
                })
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.remote", {
                    "mode": mode,
                    "origin": origin,
                    "git_url": git_url,
                    "exception": e
                })
        return True

    def get_remote_url(self):
        try:
            # TODO: handle multiple remote urls
            git_url = subprocess.check_output([self.execpath, 'config', '--get', 'remote.origin.url'],
                                              cwd=self.filepath).strip()
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.get_remote_url", {
                    "exception": e
                })
        return git_url

    def fetch(self, origin, name, option=None):
        try:
            if option:
                subprocess.check_output([self.execpath, 'fetch', option, origin,  name],
                                     cwd=self.filepath).strip()
            else:
                subprocess.check_output([self.execpath, 'fetch', origin, name],
                                     cwd=self.filepath).strip()
        except Exception as e:
            raise Exception("exception.code_driver.git.fetch", {
                    "origin": origin,
                    "name": name,
                    "exception": e
                })
        return True

    def push(self, origin, option=None, name=None):
        try:
            if option:
                if name:
                    p = subprocess.Popen([self.execpath,'push',option,origin,name],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=self.filepath)
                    out, err = p.communicate()
                else:
                    p = subprocess.Popen([self.execpath, 'push', option, origin],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=self.filepath)
                    out, err = p.communicate()
            else:
                if name:
                    p = subprocess.Popen([self.execpath,'push', origin, name],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=self.filepath)
                    out, err = p.communicate()
                else:
                    p = subprocess.Popen([self.execpath, 'push', origin],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         cwd=self.filepath)
                    out, err = p.communicate()
            if err:
                raise GitExecutionException("exception.code_driver.git.push", {
                    "origin": origin,
                    "exception": err
                })
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.push", {
                    "origin": origin,
                    "exception": e
                })
        return True

    def pull(self):
        pass

    # Gitignore file handling
    def check_gitignore_exists(self):
        if not os.path.isfile(os.path.join(self.filepath, ".gitignore")):
            return False
        return True

    def ensure_gitignore_exists(self):
        def __create_filehash(single_filepath):
            BUFF_SIZE = 65536
            sha1 = hashlib.md5()
            with open(single_filepath, 'rb') as f:
                while True:
                    data = f.read(BUFF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
            return sha1.hexdigest()

        try:
            template_gitignore_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       "templates", "gitignore")
            current_gitignore_filepath = os.path.join(self.filepath, ".gitignore")
            # Copy the .gitignore file if none exists
            if not self.check_gitignore_exists():
                shutil.copyfile(template_gitignore_filepath, current_gitignore_filepath)
            # Append current .gitignore to .gitignore template
            elif not 'datmo' in open(current_gitignore_filepath).read():
                current_filehash = __create_filehash(current_gitignore_filepath)
                template_filehash = __create_filehash(template_gitignore_filepath)
                if current_filehash != template_filehash:
                    with open(os.path.join(self.filepath, '.tempgitignore'), 'wb') as f:
                        shutil.copyfileobj(open(current_gitignore_filepath, 'rb'), f)
                        shutil.copyfileobj(open(template_gitignore_filepath, 'rb'), f)
                    shutil.move(os.path.join(self.filepath, '.tempgitignore'),
                                current_gitignore_filepath)
        except Exception as e:
            raise FileIOException("exception.code_driver.git.ensure_gitignore_exists", {
                "exception": e
            })
        return True

    # Datmo Code Refs

    def exists_code_refs_dir(self):
        dir = '.git/refs/datmo'
        if not os.path.isdir(os.path.join(self.filepath, dir)):
            return False
        return True

    def ensure_code_refs_dir(self):
        dir = '.git/refs/datmo'
        try:
            if not os.path.isdir(os.path.join(self.filepath,dir)):
                os.makedirs(os.path.join(self.filepath, dir))
        except Exception as e:
            raise FileIOException("exception.code_driver.git.ensure_code_refs_dir", {
                "exception": e
            })
        return True

    def delete_code_refs_dir(self):
        dir = '.git/refs/datmo'
        dir_path = os.path.join(self.filepath, dir)
        try:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            raise FileIOException("exception.code_driver.git.delete_code_refs_dir", {
                "exception": e
            })
        return True

    def create_code_ref(self, code_id=None):
        self.ensure_code_refs_dir()
        if not code_id:
            # add files and commit changes on current branch
            self.add('-A')
            commit_success = self.commit(options=["-m",
                                                  "auto commit by datmo"])
            code_id = self.latest_commit()
            # revert back to the original commit
            if commit_success:
                self.reset(code_id)
        # writing git commit into ref
        code_ref_path = os.path.join(self.filepath,
                                     '.git/refs/datmo/',
                                     code_id)
        with open(code_ref_path, "w") as f:
            f.write(code_id)
        return code_id

    def exists_code_ref(self, code_id):
        code_ref_path = os.path.join(self.filepath,
                                     '.git/refs/datmo/',
                                     code_id)
        if not os.path.isfile(code_ref_path):
            return False
        return True

    def delete_code_ref(self, code_id):
        self.ensure_code_refs_dir()
        code_ref_path = os.path.join(self.filepath,
                                     '.git/refs/datmo/',
                                     code_id)
        if not self.exists_code_ref(code_id):
            raise FileIOException("exception.code_driver.git.delete_code_ref", {
                "exception": "Code ref file does not exist"
            })
        os.remove(code_ref_path)
        return True

    def list_code_refs(self):
        self.ensure_code_refs_dir()
        code_refs_path = os.path.join(self.filepath,
                                     '.git/refs/datmo/')
        code_refs_list = os.listdir(code_refs_path)
        return code_refs_list

    # Datmo specific remote calls
    def push_code_ref(self, code_id='*'):
        datmo_ref = 'refs/datmo/' + code_id
        datmo_ref_map = '+' + datmo_ref + ':' + datmo_ref
        try:
            self.push('origin', name=datmo_ref_map)
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.push_code_ref", {
                    "exception": e
                })

    def fetch_code_ref(self, code_id):
        try:
            datmo_ref = 'refs/datmo/' + code_id
            datmo_ref_map = '+' + datmo_ref + ':' + datmo_ref
            success, err = self.fetch('origin', datmo_ref_map, option='-fup')
            if not success:
                raise GitExecutionException("exception.code_driver.git.fetch_code_ref", {
                    "code_id": code_id,
                    "exception": err
                })
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.fetch_code_ref", {
                    "code_id": code_id,
                    "exception": e
                })
        return True

    def checkout_code_ref(self, code_id, remote=False):
        try:
            if remote:
                self.fetch_code_ref(code_id)
            datmo_ref = 'refs/datmo/' + code_id
            return self.checkout(datmo_ref)
        except Exception as e:
            raise GitExecutionException("exception.code_driver.git.checkout_code_ref", {
                    "code_id": code_id,
                    "exception": e
                })


class GitHostManager(object):

    def __init__(self, home=os.path.expanduser('~'), host='github'):
        self.home = home
        self.in_host = host
        if host=='github':
            self.host = 'github.com'
        else:
            self.host = 'unknown'
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
        netrc_filepath = os.path.join(self.home, '.netrc')
        if os.path.exists(netrc_filepath):
            if self.host in open(netrc_filepath).read():
                return True
        else:
            return False

    def _check_for_ssh(self):
        cmd = "ssh-keyscan %s >> ~/.ssh/known_hosts" % (self.host)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=self.home)
        out, err = p.communicate()
        if "Error" in out or "Error" in err or 'denied' in err:
            self._ssh_enabled = False
        cmd = "ssh -i %s/.ssh/id_rsa -T git@%s" % (self.home, self.host)
        p = subprocess.Popen(cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=self.home)
        out, err = p.communicate()
        error_strings = [
            "Error",
            "denied",
            "Could not resolve hostname",
            "not accessible"
        ]
        for err_str in error_strings:
            if err_str in err or err_str in out:
                return False
        return True


    def create_git_netrc(self, username, password):
        netrc_filepath = os.path.join(self.home, '.netrc')
        netrc_file = open(netrc_filepath, 'w')
        netrc_file.truncate()
        netrc_file.write('machine %s' % (self.host))
        netrc_file.write('\n')
        netrc_file.write('login ' + str(username))
        netrc_file.write('\n')
        netrc_file.write('password ' + str(password))
        netrc_file.write('\n')
        netrc_file.close()
        return True

    def read_git_netrc(self):
        netrc_filepath = os.path.join(self.home, '.netrc')
        if not os.path.exists(netrc_filepath):
            return {
                "login": None,
                "password": None
            }
        netrc_file = open(netrc_filepath, 'r')
        file_content = netrc_file.read()
        lines = file_content.split('\n')
        initial_index = lines.index("machine %s" % (self.host))
        login = lines[initial_index + 1].split(' ')[-1]
        password = lines[initial_index + 2].split(' ')[-1]
        return {
            "login": login if login else None,
            "password": password if password else None
        }