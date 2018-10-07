"""
Generic tools function
"""
import re
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


def resolve_host(host, port=None):
    """
    Resolve host from given arguments
    :param host: string
    :param port: number
    :return:
    """
    if port and port != 80:
        host += ":" + str(port)
    if not host.startswith("http"):
        host = "http://" + host
    return host

def resolve_token(host):
    """
    Resolve access token from host string
    Format: https://<token>@<url>
    :param host: host as a string
    :return: token or None
    """
    host_re = r"^https?://([a-zA-Z0-9\-_]+?\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+)\@.+$"
    match = re.match(host_re, host)
    return match.group(1) if match else None

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

def requires_logged_in(func):
    """
    Decorator which verify that client are logged in
    if not but env variables are available
    it tries to loggin using them
    :param fn: function to decorated
    :return: wrapper function
    """
    def ret_fn(*args):
        """
        wrapper function
        :param args: argument for decorated function
        :return: return decorated function return values
        """
        self = args[0]
        if not self.is_logged_in:
            self.try_login(raise_if_fail=True)
        return func(*args)
    return ret_fn
