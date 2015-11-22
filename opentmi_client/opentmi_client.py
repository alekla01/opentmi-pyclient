import requests
import json
import os
import socket
import jsonmerge
import zipfile
import re 

class OpenTmiClient(object):
  
  __version = 0
  __api = "/api/v"

  def __init__(self, host='localhost', port=3000):
    """Used host
    @param host: host name or IP address
    """
    ip = None
    if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        ip = host
    if re.match("^https?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
        self.__host = host
    else:
        ip = socket.gethostbyname(host)

    if host:
        # 'http://10.45.0.138:3000'
        self.__host = 'http://'+ip+':'+str(port)

    self.__headers = {
        'content-type': 'application/json',
        "Connection": "close"
    }

  def get_version(self):
    """get API version number
    """
    return self.__version
    
  def get_suite(self, suite, options=''):
    """get single suite informations
    """
    suite = self.__get_suite( self.get_campaign_id(suite), options )
    return suite

  def get_campaign_id(self, campaignName):
    """get campaign id from name
    """  
    if( __isObjectId(campaignName)):
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

  def updateTestcase(self, metadata):
      tc = self.__lookupTestcase(metadata['name'])
      if tc:
          print("Update existing TC")
          self.__updateTestcase(tc['id'], metadata)
      else:
          print("Create new TC")
          self.__createTestcase(metadata)

  def sendResult(self, result):
      """send result to the server
      """
      print("Uploading results to DB")
      tc_metadata = result.tc_metadata
      tc = self.__lookupTestcase(tc_metadata['name'])
      if not tc:
          tc = self.__createTestcase(tc_metadata)
          if not tc:
              print("TC creation failed")
              return None

      payload = CloudResult(result).getResultObject()
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
      return self.getJSON(url)

  def __get_campaigns(self):
      url = self.__get_url("/campaigns?f=name")
      return self.getJSON(url)

  def __get_suite(self, suite, options=''):
      url = self.__get_url("/campaigns/"+suite+"/suite"+options)
      return self.getJSON(url)

  def __lookupTestcase(self, tcid):
      url = self.__get_url("/testcases?tcid="+tcid)
      try:
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

  def __updateTestcase(self, id, metadata):
      url = self.__get_url("/testcases/"+id)
      try:
          response = requests.put(url, data=json.dumps( self.__convert_to_db_tc_metadata(metadata) ), headers=self.__headers, timeout=2.0)
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

  def __createTestcase(self, metadata):
      url = self.__host + "/api/v0/testcases"
      try:
          response = requests.post(url, data=json.dumps( self.__convert_to_db_tc_metadata(metadata) ), headers=self.__headers, timeout=2.0)
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

  def __archiveLogs(self, files, zipFilename="logFiles.zip"):
      zf = zipfile.ZipFile(zipFilename, "w")
      dirname = ""
      for filename in files:
          zf.write(os.path.join(dirname, filename))
      zf.close()
      return zipFilename

  def getJSON(self, url, timeout=2.0):
       try:
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
