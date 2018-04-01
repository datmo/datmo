import os
import requests

class RemoteDatmoFileManager(object):
    def __init__(self):
        self.type = "remote-datmo"

    @staticmethod
    def upload(src_filepath, s3_presigned_url):
        if not os.path.isfile(src_filepath):
            raise Exception("Can't upload file: %s, validation failed." % src_filepath)
        with open(src_filepath, 'rb') as f:
            data = f.read()
            res = requests.put(s3_presigned_url, data=data)
            if res.status_code == 200:
                pass
            else:
                raise Exception("Upload failed: %s" % res.text)

    @staticmethod
    def download(s3_presigned_url, dst_filepath):
        res = requests.get(s3_presigned_url, stream=True)
        if res.status_code == 200:
            pass
        else:
            raise Exception("Upload failed: %s" % res.text)
        with open(dst_filepath, 'wb') as handle:
            for block in res.iter_content(1024):
                handle.write(block)


# class DatmoFileManager(object):
#     """
#     Usage: ap = DatmoFileManager('main.py', '2', get_presigned_url(), 'snapshot'); ap.push()
#     """
#     def __init__(self, file_path, unique_id, s3_presigned_url):
#         self.file_path = file_path
#         self.unique_id = unique_id
#         self.s3_presigned_url = s3_presigned_url
#
#     def push(self):
#         if not os.path.isfile(self.file_path):
#             raise Exception("Can't upload file: %s, validation failed." % self.file_path)
#         with open(self.file_path, 'rb') as f:
#             data = f.read()
#             res = requests.put(self.s3_presigned_url, data=data)
#             if res.status_code == 200:
#                 pass
#             else:
#                 raise Exception("Upload failed: %s" % res.text)
#
#     def pull(self):
#         res = requests.get(self.s3_presigned_url, stream=True)
#         if res.status_code == 200:
#             pass
#         else:
#             raise Exception("Upload failed: %s" % res.text)
#         with open(self.file_path, 'wb') as handle:
#             for block in res.iter_content(1024):
#                 handle.write(block)