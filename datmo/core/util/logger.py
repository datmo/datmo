import hashlib
import logging
import os
import tempfile
from datmo.core.util.exceptions import LoggingPathDoesNotExist
from datmo.core.util.misc_functions import grep


class DatmoLogger(object):
    instance = None
    class __InternalObj:
        def __init__(self):
            self.logging_level = 20
            self.logging_path = None
            self.loggers = {}

    def __new__(cls): # __new__ always a classmethod
        if not DatmoLogger.instance:
            DatmoLogger.instance = DatmoLogger.__InternalObj()
        return DatmoLogger.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)


    @staticmethod
    def get_logfiles():
        return map(lambda f: os.path.join(DatmoLogger().logging_path,f), os.listdir(DatmoLogger().logging_path))

    @staticmethod
    def find_text_in_logs(text_str):
        results = []
        for logfile in DatmoLogger.get_logfiles():
            with open(logfile,"r") as f:
                for r in grep(text_str, f):
                    results.append({
                      "file": logfile,
                      "line_number": r[0],
                      "line": r[1]
                    })
        return results

    @staticmethod
    def get_logger(name = __name__, file_name="log.txt"):
        """Returns a python logger with logging level set

        Parameters
        ----------
        name : string
          Name of the logger.  eg datmo.core.snapshot or __name__

        file_name : string
          Log file name. default = log.txt

        Returns
        -------
        logging.Logger
          Python logger

        """

        # get or create logging path
        if DatmoLogger().logging_path == None:
            DatmoLogger().logging_path = tempfile.mkdtemp()

        logging_path = DatmoLogger().logging_path
        logfile_path = os.path.join(logging_path, file_name)

        # cache the logger and return it otherwise the handlers will get added multiple times
        # and result in multiple messages to the same file

        logger_hash = hashlib.sha1(name + file_name).hexdigest()

        if logger_hash in DatmoLogger().loggers:
            return DatmoLogger().loggers[logger_hash]

        # create logger based on name
        log = logging.getLogger(logger_hash)

        # cache logger
        DatmoLogger().loggers[logger_hash] = log

        log.setLevel(DatmoLogger().logging_level)

        handler = logging.FileHandler(logfile_path)
        handler.setLevel(DatmoLogger().logging_level)
        formatter = logging.Formatter('%(asctime)s - ' + name + '.%(funcName)s [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)

        log.addHandler(handler)
        return log

    @staticmethod
    def configure(logging_path, logging_level = 0):
        if type(logging_path) == 'string' and not os.path.exists(logging_path):
            raise LoggingPathDoesNotExist(logging_path)
        global_logger = DatmoLogger()
        global_logger.logging_level = logging_level
        global_logger.logging_path = logging_path
        return global_logger








