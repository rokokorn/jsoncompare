# import httplib2
import json
import sys
# import types

TYPE = 'TYPE'
PATH = 'PATH'
VALUE = 'VALUE'

# Borrowed from http://djangosnippets.org/snippets/2247/
# with some modifications.
class Diff(object):
  def __init__(self, first, second, with_values=False, caseSensitive=True):
    self.difference = []
    # self.seen = []
    not_with_values = not with_values
    self.check(first, second, with_values=with_values, caseSensitive=caseSensitive)

  def check(self, first, second, path='', with_values=False, caseSensitive=True):
    if with_values and second != None:
      if not isinstance(first, type(second)):
        # message = '%s | %s | %s' % (path, type(first).__name__, type(second).__name__)
        message = {'path': path, 'old': type(first).__name__, 'new': type(second).__name__}
        self.save_diff(message, TYPE)

    if isinstance(first, dict):
      for key in first:
        # the first part of path must not have trailing dot.
        if len(path) == 0:
          new_path = key
        else:
          new_path = "%s.%s" % (path, key)

        if isinstance(second, dict):
          # if second.has_key(key):
          if key in second:
            sec = second[key]
          else:
            #  there are key in the first, that is not presented in the second
            # self.save_diff(new_path, PATH)
            message = {'path': new_path, 'old': None, 'new': None}
            self.save_diff(message, PATH)

            # prevent further values checking.
            sec = None

          # recursive call
          if sec != None:
            self.check(first[key], sec, path=new_path, with_values=with_values, caseSensitive=caseSensitive)
        else:
          # second is not dict. every key from first goes to the difference
          # self.save_diff(new_path, PATH)
          message = {'path': new_path, 'old': None, 'new': None}
          self.save_diff(message, PATH)
          self.check(first[key], second, path=new_path, with_values=with_values, caseSensitive=caseSensitive)

    # if object is list, loop over it and check.
    elif isinstance(first, list):
      for (index, item) in enumerate(first):
        new_path = "%s[%s]" % (path, index)
        # try to get the same index from second
        sec = None
        if second != None:
          try:
            sec = second[index]
          except (IndexError, KeyError):
            # goes to difference
            # self.save_diff('%s | %s' % (new_path, type(item).__name__), TYPE)
            message = {'path': new_path, 'old': type(item).__name__, 'new': None}
            self.save_diff(message, TYPE)

        # recursive call
        self.check(first[index], sec, path=new_path, with_values=with_values, caseSensitive=caseSensitive)

    # not list, not dict. check for equality (only if with_values is True) and return.
    else:
      if with_values and second != None:
        if (not caseSensitive):
          try:
            firstUpper = first.upper()
            secondUpper = second.upper()
          except:
            firstUpper = first
            secondUpper = second
        else:
            firstUpper = first
            secondUpper = second         

        if firstUpper != secondUpper:
          message = {'path': path, 'old': first, 'new': second}
          self.save_diff(message, VALUE)
      return

  def save_diff(self, diff_message, type_):
    if diff_message not in self.difference:
      # self.seen.append(diff_message)
      self.difference.append((type_, diff_message))

# def getContentFromUri(uri):
#   h = httplib2.Http()
#   resp, content = h.request(uri, "GET")
#   return content

def getContentFromFile(filePath):
  return open(filePath, 'r').read()

def getContent(location):
  content = None
  # if type(location) is types.DictType:
  if isinstance(location, dict) | isinstance(location, list):
    return location
  # if location.startswith("http"):
  #   content = getContentFromUri(location)
  else:
    content = getContentFromFile(location)
  if content is None:
    raise Error("Could not load content for " + location)
  return json.loads(content)

def compare(location1, location2, caseSensitive=True):
  json1 = getContent(location1)
  json2 = getContent(location2)
  diff1 = Diff(json1, json2, True, caseSensitive).difference
  diff2 = Diff(json2, json1, False, caseSensitive).difference
  diffs = []
  for type, message in diff1:
    newType = 'CHANGED'
    if type == PATH:
      newType = 'REMOVED'
    diffs.append({'type': newType, 'message': message})
  for type, message in diff2:
    diffs.append({'type': 'ADDED', 'message': message})
  return diffs

# if __name__ == '__main__':
#   if len(sys.argv) != 3:
#     sys.exit('Error')
#   location1 = sys.argv[1]
#   location2 = sys.argv[2]
#   diffs = compare(location1, location2)
#   if len(diffs) > 0:
#     print '\r\nFound differences comparing ' + location1 + ' and ' + location2
#   for diff in diffs:
#     print diff['type'] + ': ' + diff['message']
