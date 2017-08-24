import re

def isObjectId(value):
  if value is None:
    return False

  objectidRe = "^[0-9a-fA-F]{24}$"
  return re.match(objectidRe, value)