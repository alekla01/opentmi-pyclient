"""
Generic tools function
"""
import re
import socket
import zipfile
import os
import six


def is_object_id(value):
    """
    Check if value is mongodb ObjectId
    :param value:
    :return: Boolean
    """
    if not isinstance(value, six.string_types):
        return False

    objectid_re = r"^[0-9a-fA-F]{24}$"
    match = re.match(objectid_re, value)
    return True if match else False


def resolve_host(host="localhost", port=None):
    """
    Resolve host from given arguments
    :param host: string
    :param port: number
    :return:
    """
    ip_addr = None
    _host = None
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{2,5})?$", host):
        ip_addr = host
    elif re.match(r"^https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d{2,5})?$", host):
        _host = host
    else:
        ip_addr = socket.gethostbyname(host)
    if ip_addr:
        # 'http://1.2.3.4:3000'
        _host = 'http://' + ip_addr
    if port and port != 80:
        _host += ":" + str(port)
    return _host


def archive_files(files, zip_filename, base_path=""):
    """
    Archive given files
    :param files: list of file names
    :param zip_filename: target zip filename
    :param base_path: base path for files
    :return:
    """
    zip_file = zipfile.ZipFile(zip_filename, "w")
    for filename in files:
        zip_file.write(os.path.join(base_path, filename), filename)
    zip_file.close()
    return zip_filename
