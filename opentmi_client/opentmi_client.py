import requests
import json
import os
import socket
import jsonmerge
import zipfile
import re
import logging
from requests import Response

# Appliaction modules
from tools import isObjectId


REQUEST_TIMEOUT = 30

def _is_success(response):
    assert isinstance(response, Response)
    code = response.status_code
    return code >= 200 and code < 300

# Generic API to construct Client Object
def create(host='localhost', port=3000, result_converter=None, testcase_converter=None):
    return OpenTmiClient(host, port, result_converter, testcase_converter)

class OpenTmiClient(object):

    __version = 0
    __api = "/api/v"

    def __init__(self,
                host='localhost',
                port=3000,
                result_converter=None,
                testcase_converter=None):
        """Used host
        @param host: host name or IP address
        """
        self.set_logger()
        self.resultConverter = result_converter
        self._tcConverter = testcase_converter
        self.set_host(host, port)
        self.__headers = {
            'content-type': 'application/json',
            "Connection": "close"
        }

    def set_logger(self, logger = None):
        if not logger:
            # use default logger
            logger = logging.getLogger('OpenTMI')
            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            logger.addHandler(ch)

        self.logger = logger

    def set_host(self, host='localhost', port=3000):
        """Set OpenTMI host
        """
        #TODO find tool for this.
        ip = None
        if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
            ip = host
        if re.match("^https?\:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
            self.__host = host + ":" + str(port)
        else:
            ip = socket.gethostbyname(host)

        if ip:
            # 'http://1.2.3.4:3000'
            self.__host = 'http://'+ip+':'+str(port)

        self.logger.info("Set OpenTMI host: %s" % (self.__host))

    def get_version(self):
        """get API version number
        """
        return self.__version

    def get_opentmi_apiversion(self):
        # todo
        pass

    # API's

    # Build
    def upload_build(self, build):
        payload = build
        url = self.__url("/duts/builds")
        try:
            response = requests.post(url, data=json.dumps(payload), headers=self.__headers, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                # self.logger.debug(data)
                self.logger.debug("build uploaded successfully")
                return data
            else:
                self.logger.warning("result uploaded failed, status_code: ", response.status_code)
                self.logger.warning(response.text)
        except requests.exceptions.RequestException as e:
            self.logger.warning(e)
        except Exception as e:
            self.logger.warning(e)
    # Suite
    def get_suite(self, suite, options=''):
        """get single suite informations
        """
        suite = self.__get_suite( self.get_campaign_id(suite), options )
        return suite

    # Campaign
    def get_campaign_id(self, campaignName):
        """get campaign id from name
        """
        if(isObjectId(campaignName)):
            return campaignName

        try:
          for c in self.__get_campaigns():
              if c['name'] == campaignName:
                return c['_id']
        except KeyError:
            return KeyError(campaignName)

    def get_campaigns(self):
        return self.__get_campaigns()

    def get_campaign_names(self):
        campaigns = self.__get_campaigns()
        campaignNames = []
        for campaign in campaigns:
            campaignNames.append(campaign['name'])
        return campaignNames

    # Testcase
    def get_testcases(self, filters=''):
        return self.__get_testcases()

    def update_testcase(self, metadata):
        tc = self.__lookup_testcase(metadata['name'])
        if tc:
            self.logger.debug("Update existing TC")
            self.__update_testcase(tc['id'], metadata)
        else:
            self.logger.debug("Create new TC")
            self.__create_testcase(metadata)

    # Result
    def upload_results(self, result):
        """send result to the server
        """
        tc_meta = self._tcConverter(result.tc_metadata) if self._tcConverter else result
        tc = self.__lookup_testcase(tc_meta['tcid'])
        if not tc:
            tc = self.__create_testcase(tc_meta)
            if not tc:
                self.logger.warning("TC creation failed")
                return None

        payload = self.resultConverter(result) if self.resultConverter else result
        url = self.__url("/results")
        try:
            files = None
            #hasLogs, logFiles = result.hasLogs()
            #if hasLogs:
            #    zipFile = self.__archiveLogs(logFiles)
            #    self.logger.debug(zipFile)
            #    files = {"file": ("logs.zip", open(zipFile), 'rb') }
            #    self.logger.debug(files)
            response = requests.post(url, data=json.dumps(payload), headers=self.__headers, files=files, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                #self.logger.debug(data)
                self.logger.debug("result uploaded successfully")
                return data
            else:
                self.logger.warning("result uploaded failed. status_code: ", response.status_code)
                self.logger.warning(response.text)

        except requests.exceptions.RequestException as e:
            self.logger.warning(e)
        except Exception as e:
            self.logger.warning(e)

        self.logger.warning("result upload failed")
        return None

    # Private members
    def __url(self, path):
        return self.__host+self.__api+str(self.__version)+path

    def __get_testcases(self, filters=''):
        url = self.__url("/testcases?" + filters)
        return self.__get_JSON(url)

    def __get_campaigns(self):
        url = self.__url("/campaigns?f=name")
        return self.__get_JSON(url)

    def __get_suite(self, suite, options=''):
        url = self.__url("/campaigns/" + suite + "/suite" + options)
        return self.__get_JSON(url)

    def __lookup_testcase(self, tcid):
        url = self.__url("/testcases?tcid=" + tcid)
        try:
            self.logger.debug("Search TC: %s (%s)" % (tcid, url))
            response = requests.get(url, headers=self.__headers, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                if len(data) == 1:
                    self.logger.debug("testcase '%s' exists in DB" % tcid)
                    #self.logger.debug(data[0])
                    return data[0]
            elif(response.status_code == 404):
                self.logger.warning("testcase '%s' not found form DB" % tcid)
        except requests.exceptions.RequestException as e:
            self.logger.warning(e)
        except Exception as e:
            self.logger.warning(e)

        return None

    def __update_testcase(self, id, metadata):
        url = self.__url("/testcases/" + id)
        try:
            self.logger.debug("Update TC: %s" % url)
            payload = metadata
            response = requests.put(url, data=json.dumps( payload ), headers=self.__headers, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                self.logger.debug("testcase metadata uploaded successfully")
                return data
            self.logger.debug( response.content )
        except requests.exceptions.RequestException as e:
            self.logger.debug(e)
        except Exception as e:
            self.logger.debug(e)

        self.logger.warning("testcase metadata upload failed")
        return None

    def __create_testcase(self, metadata):
        url = self.__host + "/api/v0/testcases"
        try:
            self.logger.debug("Create TC: %s" % url)
            payload = metadata
            response = requests.post(url, data=json.dumps( payload ), headers=self.__headers, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                self.logger.debug("new testcase metadata uploaded successfully with id: %s" % json.dumps(data))
                return data
            else:
                self.logger.warning( response.content )
        except requests.exceptions.RequestException as e:
            self.logger.warning(e)
        except KeyError as e:
            self.logger.warning('missing meta-information: %s'%e)
        except Exception as e:
            self.logger.warning('createTestcase throw exception:')
            self.logger.warning(e)

        self.logger.warning("new testcase metadata upload failed")
        return None

    def __archive_logs(self, files, zipFilename="logFiles.zip"):
        zf = zipfile.ZipFile(zipFilename, "w")
        dirname = ""
        for filename in files:
            zf.write(os.path.join(dirname, filename))
        zf.close()
        return zipFilename

    def __get_JSON(self, url):
        try:
            self.logger.debug("GET: %s" % url)
            response = requests.get(url, headers=self.__headers, timeout=REQUEST_TIMEOUT)
            if _is_success(response):
                data = json.loads(response.text)
                return data
            elif(response.status_code == 404):
                self.logger.warning('not found')
        except requests.exceptions.RequestException as e:
            self.logger.warning('Connection error %s', e.message)
            raise e

        return None
