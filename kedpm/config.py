# Copyright (C) 2003  Andrey Lebedev <andrey@micro.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: config.py,v 1.2 2003/10/09 21:12:05 kedder Exp $

"""Configuration for Ked Password Manager"""
from xml.dom import minidom
from UserDict import UserDict

# Configuration version
__version__ = "0.1"

class Option:
    """Base class for all option types"""

    __value = None
    doc = ""
    def __init__(self, default=None, doc=""):
        self.__value == default
        self.doc = doc

    def __str__(self):
        return str(self.__value)

    def get(self):
        return self.__value

    def set(self, value):
        self.__value = value

#class Options (UserDict):
#    available_options = {
#        "save-mode": """One of three values:
#    "ask": Ask user whether save or not when database changes;
#    "no": Do not save modified database automatically;
#    "auto": Save database automatically after every change."""
#    }
#    """Self-validationg options"""
#    pass

class Configuration:
    """Configuration file interface"""

    # Configuration file name
    filename = "doc/sample_config.xml"

    _options = {
        "save-mode": "ask"
    }

    options = {
        "save-mode": Option('ask', """One of three values:
    "ask": Ask user whether save or not when database changes;
    "no": Do not save modified database automatically;
    "auto": Save database automatically after every change."""),
    }

    patterns = {}

    def __init__(self):
        #self.options = Options()
        pass
    
    def open(self, fname = ""):
        """Open and parse configuration xml file"""

        filename = fname or self.filename
        xml = minidom.parse(filename)
        doc = xml.documentElement

        sections = [
            ("options", "option", self.options),
            ("patterns", "pattern", self.patterns),
        ]
        
        # Read options
        tag = doc.getElementsByTagName('options')[0]
        items = tag.getElementsByTagName('option')
        for item in items:
            item_id = item.getAttribute("name")
            item_value = ""
            for child in item.childNodes:
                item_value += child.data
            try:
                self.options[item_id].set(item_value)
            except KeyError:
                # Ignore unrecognized options
                pass
        # Read patterns
        tag = doc.getElementsByTagName('patterns')[0]
        items = tag.getElementsByTagName('pattern')
        for item in items:
            item_id = item.getAttribute("name")
            item_value = ""
            for child in item.childNodes:
                item_value += child.data
            self.patterns[item_id] = item_value

    def save(self):
        """Save configuration to xml file"""
        pass
