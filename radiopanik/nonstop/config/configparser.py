# encoding: utf-8
"""
configparser.py

Created by David Convent on 2010-12-14.
Copyright (c) 2010 radiopanik.org. All rights reserved.
"""

import sys
import os
import re
import UserDict
import ConfigParser


default_parser = ConfigParser.RawConfigParser()
default_parser.optionxform = lambda s: s

class UserError(Exception):
    """Errors made by a user 
    """

    def __str__(self):
        return " ".join(map(str, self))

class MissingOption(UserError, KeyError):
    """A required option was missing.
    """


def getConfig(filename):
    """Open a configuration file and return the result as a dictionary.
    """
    
    if not os.path.isabs(filename):
        filename = os.path.join(os.curdir, filename)
    parser = ConfigParser.RawConfigParser()
    parser.optionxform = lambda s: s
    parser.readfp(open(filename))
    
    result = {}
    for section in parser.sections():
        options = dict(parser.items(section))
        result[section] = Options(parser, section, options)
        result[section]._initialize()
    
    usernames, slicenames = [], []
    for username in result['nonstop'].pop('users', '').split():
        if username not in usernames:
            usernames.append(username)
    for slicename in result['nonstop'].pop('slices', '').split():
        if slicename not in slicenames:
            slicenames.append(slicename)
    config = dict(result.pop('nonstop'))
    config.update(users={}, slices={})
    for username in usernames:
        userdata = result.pop(username, None)
        if userdata:
            userdata = dict(userdata)
            userdata['slices'] = []
            config['users'][username] = userdata
    for slicename in slicenames:
        slicedata = result.pop(slicename, None)
        if slicedata:
            slicedata = dict(slicedata)
            slicedata['users'] = slicedata.get('users', '').split()
            sliceusers = []
            for username in slicedata['users']:
                if username not in sliceusers:
                    sliceusers.append(username)
            slicedata['users'] = sliceusers
            for username in slicedata['users']:
                user = config['users'].get(username)
                if user is not None:
                    user['slices'].append(slicename)
                else:
                    print >> sys.stdout, ("Could not find user definition "
                                          "for %s" % username)
                    slicedata['users'].remove(username)
            config['slices'][slicename] = slicedata
    return config


class Options(UserDict.DictMixin):
    """ Most of this code was taken from zc.buildout.buildout
    """
    
    def __init__(self, parser, section, data):
        self.parser = parser
        self.name = section
        self._raw = data
        self._cooked = {}
        self._data = {}
    
    def _initialize(self):
        # force substitutions
        for k, v in self._raw.items():
            if '${' in v:
                self._dosub(k, v)
    
    def _dosub(self, option, v):
        seen = [(self.name, option)]
        v = '$$'.join([self._sub(s, seen) for s in v.split('$$')])
        self._cooked[option] = v
    
    def get(self, option, default=None, seen=None):
        try:
            return self._data[option]
        except KeyError:
            pass
        
        v = self._cooked.get(option)
        if v is None:
            v = self._raw.get(option)
            if v is None:
                return default
        
        if '${' in v:
            key = self.name, option
            if seen is None:
                seen = [key]
            elif key in seen:
                raise UserError(
                    "Circular reference in substitutions.\n"
                    )
            else:
                seen.append(key)
            v = '$$'.join([self._sub(s, seen) for s in v.split('$$')])
            seen.pop()
        
        self._data[option] = v
        return v
    
    _template_split = re.compile('([$]{[^}]*})').split
    _simple = re.compile('[-a-zA-Z0-9 ._]+$').match
    _valid = re.compile('\${[-a-zA-Z0-9 ._]*:[-a-zA-Z0-9 ._]+}$').match
    def _sub(self, template, seen):
        value = self._template_split(template)
        subs = []
        for ref in value[1::2]:
            s = tuple(ref[2:-1].split(':'))
            if not self._valid(ref):
                if len(s) < 2:
                    raise UserError("The substitution, %s,\n"
                                                "doesn't contain a colon."
                                                % ref)
                if len(s) > 2:
                    raise UserError("The substitution, %s,\n"
                                                "has too many colons."
                                                % ref)
                if not self._simple(s[0]):
                    raise UserError(
                        "The section name in substitution, %s,\n"
                        "has invalid characters."
                        % ref)
                if not self._simple(s[1]):
                    raise UserError(
                        "The option name in substitution, %s,\n"
                        "has invalid characters."
                        % ref)
            
            section, option = s
            if not section:
                section = self.name
            v = self.parser.get(section, option)
            if v is None:
                raise MissingOption("Referenced option does not exist:",
                                    section, option)
            subs.append(v)
        subs.append('')
        
        return ''.join([''.join(v) for v in zip(value[::2], subs)])
    
    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            pass
        
        v = self.get(key)
        if v is None:
            raise MissingOption("Missing option: %s:%s" % (self.name, key))
        return v
    
    def __setitem__(self, option, value):
        if not isinstance(value, str):
            raise TypeError('Option values must be strings', value)
        self._data[option] = value
    
    def __delitem__(self, key):
        if key in self._raw:
            del self._raw[key]
            if key in self._data:
                del self._data[key]
            if key in self._cooked:
                del self._cooked[key]
        elif key in self._data:
            del self._data[key]
        else:
            raise KeyError, key
    
    def keys(self):
        raw = self._raw
        return list(self._raw) + [k for k in self._data if k not in raw]
    
    def copy(self):
        result = self._raw.copy()
        result.update(self._cooked)
        result.update(self._data)
        return result

