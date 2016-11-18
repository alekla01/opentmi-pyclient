import re

def isObjectId(value):
  objectidRe = "^[0-9a-fA-F]{24}$"
  return re.match(objectidRe, value)