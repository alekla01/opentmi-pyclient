"""
OpenTmiClient module
"""
import json


# Application modules
from opentmi_client.utils import is_object_id, get_logger, OpentmiException, TransportException
from opentmi_client.transport import Transport

REQUEST_TIMEOUT = 30


#pylint: disable-msg=too-many-arguments
def create(host='localhost', port=None, result_converter=None, testcase_converter=None):
    """
    Generic create -api for Client
    :param host:
    :param port:
    :param result_converter:
    :param testcase_converter:
    :return: OpenTmiClient
    """
    return OpenTmiClient(host, port, result_converter, testcase_converter)


class OpenTmiClient(object):
    """
    OpenTmiClient object
    """
    __version = 0
    __api = "/api/v"

    # pylint: disable-msg=too-many-arguments
    def __init__(self,
                 host='127.0.0.1',
                 port=None,
                 result_converter=None,
                 testcase_converter=None,
                 transport=None):
        """
        Constructor for OpenTMI client
        :param host: opentmi host address (default="localhost")
        :param port: opentmi server port (default=3000)
        :param result_converter:
        :param testcase_converter: function
        :param transport: optional Transport layer. Mostly for testing purpose
        """
        self.__logger = get_logger()
        self.__result_converter = result_converter
        self.__tc_converter = testcase_converter
        self.__transport = Transport(host, port) if not transport else transport

    def login(self, username, password):
        """
        Login to OpenTMI server
        :param username: username for OpenTMI
        :param password: password for OpenTMI
        :return: OpenTmiClient
        """
        payload = {
            "username": username,
            "password": password
        }
        url = self.__transport.host + "/login"
        response = self.__transport.post_json(url, payload)
        token = response.get("token")
        self.logger.info("Login success. Token: %s", token)
        self.set_token(token)
        return self

    def set_logger(self, logger):
        """
        Set custom logger
        :param logger: logging.Logger instance
        :return: OpenTmiClient
        """
        self.__logger = logger
        return self

    @property
    def logger(self):
        """
        getter for logger
        :return: Logger
        """
        return self.__logger

    def logout(self):
        """
        Logout
        :return: OpenTmiClient
        """
        self.__transport.set_token(None)
        return self

    def set_token(self, token):
        """
        Set authentication token for transport layer
        :param token:
        :return: OpenTmiClient
        """
        self.__transport.set_token(token)
        return self

    def get_version(self):
        """
        Get Client version
        :return:
        """
        return self.__version

    def upload_build(self, build):
        """
        Upload build
        :param build:
        :return:
        """
        payload = build
        url = self.__resolve_apiuri("/duts/builds")
        try:
            data = self.__transport.post_json(url, payload)
            self.logger.debug("build uploaded successfully")
            return data
        except TransportException as error:
            self.logger.warning("Result upload failed: %s (status: %s)", error.message, error.code)
        except OpentmiException as error:
            self.logger.warning(error)
        return None

    # Suite
    def get_suite(self, suite, options=''):
        """
        get single suite informations
        :param suite:
        :param options:
        :return:
        """
        try:
            campaign_id = self.get_campaign_id(suite)
        except OpentmiException as error:
            self.logger.warning("exception happened while resolving suite: %s, %s",
                                suite, error)
            return None

        if campaign_id is None:
            self.logger.warning("could not resolve campaign id for suite: %s",
                                suite)
            return None

        suite = self.__get_suite(campaign_id, options)
        return suite

    # Campaign
    def get_campaign_id(self, campaign_name):
        """
        get campaign id from name
        :param campaign_name:
        :return: string
        """
        if is_object_id(campaign_name):
            return campaign_name

        for campaign in self.__get_campaigns():
            if campaign['name'] == campaign_name:
                return campaign['_id']
        return None

    def get_campaigns(self):
        """
        Get campaigns
        :return:
        """
        return self.__get_campaigns()

    def get_campaign_names(self):
        """
        Get campaign names
        :return:
        """
        campaigns = self.__get_campaigns()
        campaign_names = []
        for campaign in campaigns:
            campaign_names.append(campaign['name'])
        return campaign_names

    def get_testcases(self, filters=None):
        """
        Get testcases
        :param filters:
        :return:
        """
        return self.__get_testcases(filters)

    def update_testcase(self, metadata):
        """
        update test case
        :param metadata:
        :return:
        """
        testcase = self.__lookup_testcase(metadata['tcid'])
        if testcase:
            test_id = testcase.get('_id')
            self.logger.info("Update existing TC (%s)", test_id)
            self.__update_testcase(test_id, metadata)
        else:
            self.logger.info("Create new TC")
            self.__create_testcase(metadata)
        return self

    def upload_results(self, result):
        """
        Upload result
        :param result:
        :return:
        """
        tc_meta = self.__tc_converter(result.tc_metadata) if self.__tc_converter else result
        test_case = self.__lookup_testcase(tc_meta['tcid'])
        if not test_case:
            test_case = self.__create_testcase(tc_meta)
            if not test_case:
                self.logger.warning("TC creation failed")
                return None

        payload = self.__result_converter(result) if self.__result_converter else result
        url = self.__resolve_apiuri("/results")
        try:
            files = None
            # hasLogs, logFiles = result.hasLogs()
            # if hasLogs:
            #    zipFile = self.__archiveLogs(logFiles)
            #    self.logger.debug(zipFile)
            #    files = {"file": ("logs.zip", open(zipFile), 'rb') }
            #    self.logger.debug(files)
            data = self.__transport.post_json(url, payload, files=files)
            self.logger.debug("result uploaded successfully")
            return data
        except TransportException as error:
            self.logger.warning("result uploaded failed: %s. status_code: %d",
                                error.message, error.code)
        except OpentmiException as error:
            self.logger.warning(error)
        return None

    # Private members

    def __get_testcases(self, filters=None):
        url = self.__resolve_apiuri("/testcases")
        return self.__transport.get_json(url, params=filters if filters else None)

    def __get_campaigns(self):
        url = self.__resolve_apiuri("/campaigns")
        return self.__transport.get_json(url, params={"f": "name"})

    def __get_suite(self, suite, options=''):
        url = self.__resolve_apiuri("/campaigns/" + suite + "/suite" + options)
        return self.__transport.get_json(url)

    def __lookup_testcase(self, tcid):
        url = self.__resolve_apiuri("/testcases")
        self.logger.debug("Search TC: %s", tcid)
        try:
            data = self.__transport.get_json(url, params={"tcid": tcid})
            if len(data) == 1:
                doc = data[0]
                self.logger.debug("testcase '%s' exists in DB (%s)", tcid, doc.get('_id'))
                return doc
        except TransportException as error:
            if error.code == 404:
                self.logger.warning("testcase '%s' not found form DB", tcid)
            else:
                self.logger.warning("Test case find failed: %s", error.message)
        except OpentmiException as error:
            self.logger.warning(error)

        return None

    def __update_testcase(self, test_id, metadata):
        url = self.__resolve_apiuri("/testcases/" + test_id)
        try:
            self.logger.debug("Update TC: %s", url)
            payload = metadata
            data = self.__transport.put_json(url, payload)
            self.logger.debug("testcase metadata uploaded successfully")
            return data
        except TransportException as error:
            self.logger.debug(error)
        except OpentmiException as error:
            self.logger.debug(error)

        self.logger.warning("testcase metadata upload failed")
        return None

    def __create_testcase(self, metadata):
        url = self.__resolve_apiuri("/testcases")
        try:
            self.logger.debug("Create TC: %s", url)
            payload = metadata
            data = self.__transport.post_json(url, payload)
            self.logger.debug("new testcase metadata uploaded successfully with id: %s",
                              json.dumps(data))
            return data
        except TransportException as error:
            self.logger.warning(error)
        except OpentmiException as error:
            self.logger.warning('createTestcase throw exception:')
            self.logger.warning(error)

        self.logger.warning("new testcase metadata upload failed")
        return None

    def __resolve_apiuri(self, path):
        return self.__transport.host + self.__api + str(self.__version) + path
