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
# $Id: password_tree.py,v 1.3 2003/08/13 22:01:59 kedder Exp $

""" Password items organized in recursive tree """

import re

from kedpm.password import Password

class PasswordTreeIterator:
    def __init__(self, tree, parent=None):
        self.parent = None
        self.pass_index = 0
        self.branch_index = 0
        self.branches = tree.getBranches().keys()
        self.branches.sort()
        self.br_iterator = None
        self.stopped = 0
        self.tree = tree

    def getCurrentCategory(self):
        return self.branches[self.branch_index]
        
    def next(self):

        '''This will iterate through whole password tree. next() method will
        consequently return every item in password tree.'''
        
        if len(self.branches) > self.branch_index:
            if self.br_iterator:
                nxt = self.br_iterator.next()
                if nxt:
                    return nxt
                self.branch_index += 1
                self.br_iterator = None
                return self.next()
            else:
                self.br_iterator = self.tree[self.branches[self.branch_index]].getIterator()
                return self.next()

        else:
            # iterate on passwords
            nodes = self.tree.getNodes()
            if len(nodes) > self.pass_index:
                pwd = nodes[self.pass_index]
                self.pass_index += 1
                return pwd
            else:
                return None
                

class PasswordTree:
    _nodes = []
    _branches = {}
    
    def __init__(self):
        " Create named tree instance """
        self._nodes = []
        self._branches = {}

    def addNode(self, node):
        """ add node to the tree """
        self._nodes.append(node)

    def addBranch(self, name):
        """ add new branch to the tree """
        if self._branches.has_key(name):
            raise AttributeError, "Branch already exists"
        branch = PasswordTree()
        self._branches[name] = branch
        return branch

    def getNodes(self):
        """ return all non-tree nodes of the tree """
        return self._nodes

    def getBranches(self):
        """ return all branch nodes of the tree """
        return self._branches
   
    def get(self, branch, default=None):
        return self._branches.get(branch, default)
   
    def __getitem__(self, key):
        return self._branches[key]

    def locate(self, pattern):
        '''returns list of passwords, matching pattern'''
        re_search = re.compile(".*"+pattern+".*")
        results = []
        for password in self._nodes:
            for field in password.getSearhableFields():
                fval = getattr(password, field)
                if re_search.match(fval):
                    results.append(password)
                    break
        return results

    def getTreeFromPath(self, path):
        '''Return password tree from given path
        path is list of path items'''
        path = self.normalizePath(path)
        tree = self
        if path == []:
            return tree
        for pathitem in path:
            tree = tree[pathitem]
        return tree

    def normalizePath(self, path):
        '''reduce .. and . items from path
        path is list of path items'''
        normal = []
        for pathitem in path:
            if pathitem == ".":
                continue
            if pathitem == "..":
                normal = normal[:-1]
                continue
            normal.append(pathitem)
        return normal
    
    def getIterator(self):
        return PasswordTreeIterator(self)
    
    def asString(self, indent = 0):
        output = ""
        indstr = " " * (indent*4)
        for (bname, branch) in self._branches.items():
            output = output + indstr + bname+"\n"
            output = output + branch.asString(indent+1)
        for password in self._nodes:
            output = output + indstr + str(password) + "\n"
        return output

    def __str__(self):
        return self.asString()
