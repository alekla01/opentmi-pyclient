import requests
import json
import os
import socket
import jsonmerge
import zipfile
import re
import logging

def create(host='localhost', port=3000, result_converter=None, testcase_converter=None):
    return OpenTmiClient(host, port, result_converter, testcase_converter)

class OpenTmiClient(object):
  
    __version = 0
    __api = "/api/v"

    def __init__(self, host='localhost', port=3000, result_converter=None, testcase_converter=None):
        """Used host
        @param host: host name or IP address
        """
        self.logger = logging.getLogger('OpenTMI')
        self.resultConverter = result_converter
        self.tcConverter = testcase_converter
        self.set_host(host, port)
        self.__headers = {
            'content-type': 'application/json',
            "Connection": "close"
        }


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

    def get_suite(self, suite, options=''):
        """get single suite informations
        """
        suite = self.__get_suite( self.get_campaign_id(suite), options )
        return suite

    def get_campaign_id(self, campaignName):
        """get campaign id from name
        """
        if(self.__isObjectId(campaignName)):
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

    def get_testcases(self, filters=''):
      return self.__get_testcases()

    def update_testcase(self, metadata):
      tc = self.__lookup_testcase(metadata['name'])
      if tc:
          print("Update existing TC")
          self.__update_testcase(tc['id'], metadata)
      else:
          print("Create new TC")
          self.__create_testcase(metadata)

    def upload_results(self, result):
        """send result to the server
        """
        if(self.tcConverter):
            result_meta = self.tcConverter(result.tc_metadata)
        print("Uploading results to DB")
        tc = self.__lookup_testcase(result_meta['tcid'])
        if not tc:
            tc = self.__create_testcase(result_meta)
            if not tc:
                print("TC creation failed")
                return None

        payload = self.resultConverter(result) if self.resultConverter else result
        url = self.__get_url("/results")
        try:
            files = None
            #hasLogs, logFiles = result.hasLogs()
            #if hasLogs:
            #    zipFile = self.__archiveLogs(logFiles)
            #    print(zipFile)
            #     files = {"file": ("logs.zip", open(zipFile), 'rb') }
            #    print(files)
            response = requests.post(url, data=json.dumps(payload), headers=self.__headers, files=files, timeout=2.0)
            if(response.status_code == 200):
                data = json.loads(response.text)
                #print(data)
                print("result uploaded successfully")
                return data
            elif response.status_code == 300:
                print("result uploaded failed")
                print(response.text)

        except requests.exceptions.RequestException as e:
            print(e)
        except Exception as e:
            print(e)

        print("result upload failed")
        return None

    def __get_url(self, path):
      return self.__host+self.__api+str(self.__version)+path

    def __get_testcases(self, filters=''):
      url = self.__get_url("/testcases?"+filters)
      return self.__get_JSON(url)

    def __get_campaigns(self):
      url = self.__get_url("/campaigns?f=name")
      return self.__get_JSON(url)

    def __get_suite(self, suite, options=''):
      url = self.__get_url("/campaigns/"+suite+"/suite"+options)
      return self.__get_JSON(url)

    def __lookup_testcase(self, tcid):
      url = self.__get_url("/testcases?tcid="+tcid)
      try:
          self.logger.debug("Search TC: %s" % url)
          response = requests.get(url, headers=self.__headers, timeout=2.0)
          if(response.status_code == 200):
              data = json.loads(response.text)
              if len(data) == 1:
                  print("testcase '%s' exists in DB" % tcid)
                  #print(data[0])
                  return data[0]
          elif(response.status_code == 404):
              print("testcase '%s' not found form DB" % tcid)
      except requests.exceptions.RequestException as e:
          print(e)
      except Exception as e:
          print(e)

      return None

    def __update_testcase(self, id, metadata):
      url = self.__get_url("/testcases/"+id)
      try:
          self.logger.debug("Update TC: %s" % url)
          payload = metadata
          response = requests.put(url, data=json.dumps( payload ), headers=self.__headers, timeout=2.0)
          if(response.status_code == 200):
              data = json.loads(response.text)
              #print(data)
              print("testcase metadata uploaded successfully")
              return data
          print( response.content )
      except requests.exceptions.RequestException as e:
          print(e)
      except Exception as e:
          print(e)

      print("testcase metadata upload failed")
      return None

    def __create_testcase(self, metadata):
      url = self.__host + "/api/v0/testcases"
      try:
          self.logger.debug("Create TC: %s" % url)
          payload = metadata
          response = requests.post(url, data=json.dumps( payload ), headers=self.__headers, timeout=2.0)
          if(response.status_code == 200):
              data = json.loads(response.text)
              print("new testcase metadata uploaded successfully with id: %s" % json.dumps(data))
              return data
          else:
              print( response.content )
      except requests.exceptions.RequestException as e:
          print(e)
      except KeyError as e:
          print('missing meta-information: %s'%e)
      except Exception as e:
          print('createTestcase throw exception:')
          print(e)

      print("new testcase metadata upload failed")
      return None

    def __archive_logs(self, files, zipFilename="logFiles.zip"):
      zf = zipfile.ZipFile(zipFilename, "w")
      dirname = ""
      for filename in files:
          zf.write(os.path.join(dirname, filename))
      zf.close()
      return zipFilename

    def __get_JSON(self, url, timeout=20.0):
       try:
          self.logger.debug("GET: %s" % url)
          response = requests.get(url, headers=self.__headers, timeout=timeout)
          if(response.status_code == 200):
              data = json.loads(response.text)
              return data
          elif(response.status_code == 404):
              print('not found')
       except requests.exceptions.RequestException as e:
           print('Connection error')

       return None

    def __isObjectId(value):
      objectidRe = "^[0-9a-fA-F]{24}$"
      return re.match(objectidRe, value)
