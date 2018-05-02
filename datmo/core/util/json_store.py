import os
import json
import yaml
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.exceptions import SaveSettingException, \
    FileIOException


class JSONStore():
    # TODO:  add file locking
    # https://stackoverflow.com/questions/186202/what-is-the-best-way-to-open-a-file-for-exclusive-access-in-python
    # Alternatives to JSON??
    # https://martin-thoma.com/configuration-files-in-python/
    def __init__(self, filepath, initial_dict={}):
        self.filepath = filepath
        # Ensure filepath directories exist
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        # save initial dictionary
        if initial_dict:
            self.to_file(initial_dict)
        # keep file in memory until a write occurs
        self.in_memory_settings = False

    def to_file(self, dictionary):
        with open(self.filepath, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(
                dictionary,
                indent=4,
                sort_keys=True,
                separators=(',', ': '),
                ensure_ascii=False)
            outfile.write(to_unicode(str_))
        return

    def save(self, key, value):
        self.in_memory_settings = False
        settings_dict = {}
        if not os.path.exists(self.filepath):
            open(self.filepath, 'w').close()
        else:
            settings_dict = json.load(open(self.filepath, 'r'))
        settings_dict[key] = value
        with open(self.filepath, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(
                settings_dict,
                indent=4,
                sort_keys=True,
                separators=(',', ': '),
                ensure_ascii=False)
            outfile.write(to_unicode(str_))
        return

    def get(self, name):
        if self.in_memory_settings and name in self.in_memory_settings:
            return self.in_memory_settings[name]

        if not os.path.exists(self.filepath):
            return None

        with open(self.filepath) as settings_file:
            try:
                settings = json.load(settings_file)
                # save in memory
                self.in_memory_settings = settings
            except Exception as err:
                raise SaveSettingException(err)
            if name in settings:
                return settings[name]
            else:
                return None

    def to_dict(self):
        output_dict = dict()
        # reading json file to stats
        if os.path.exists(self.filepath):
            with open(self.filepath) as data_file:
                meta_data_string = data_file.read()
            try:
                output_dict = json.loads(meta_data_string)
                output_dict = yaml.safe_load(json.dumps(output_dict))
            except Exception as err:
                raise FileIOException(err)
        return output_dict
