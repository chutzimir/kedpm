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
# $Id: test_figaro.py,v 1.6 2003/08/15 20:43:22 kedder Exp $

import os
import unittest
from kedpm.plugins.pdb_figaro import PDBFigaro, FPM_PASSWORD_LEN
from Crypto.Cipher import Blowfish

class PDBFigaroTestCase(unittest.TestCase):
    password = 'password'
    def setUp(self):
        self.pdb = PDBFigaro()
        self.pdb.open(self.password, fname='test/fpm.sample')

    def test_create(self):
        assert isinstance(self.pdb, PDBFigaro)

    def test_tree(self):
        'Tree should be formed correctly'
        ptree = self.pdb.getTree()
        branches = ptree.getBranches()
        bkeys = branches.keys()
        bkeys.sort()
        self.assertEqual(bkeys, ['Kedder', 'Test'])
        tree_test = ptree['Test']
        assert tree_test
        self.assertEqual(len(tree_test.getNodes()), 2)
        tree_kedder = ptree['Kedder']
        assert tree_kedder
        self.assertEqual(len(tree_kedder.getNodes()), 1)

    def test_fpmCompatibilty(self):
        ptree = self.pdb.getTree()
        pwd = ptree['Test'].locate('test2')[0]
        self.assertEqual(pwd.default, 1)
        pwd = ptree['Test'].locate('test1')[0]
        self.assertEqual(pwd.default, 0)
        pwd = ptree['Kedder'].locate('kedder1')[0]
        self.assertEqual(pwd.launcher, 'ssh')
        
    def test_decryption(self):
        'Test how passwords are decrypted'
        tree_test = self.pdb.getTree()['Test']
        pwds = tree_test.locate('url')
        self.assertEqual(len(pwds), 2)
        pwd_test2 = tree_test.locate('test2')
        self.assertEqual(pwd_test2[0].password, 'test2 password')

    def test_encriptionUtils(self):
        str = "FIGARO ENCRYPTION TEST"
        noised = self.pdb._addNoise(str)
        self.assertEqual(len(noised) % Blowfish.block_size, 0)
        rotated = self.pdb._rotate(noised)
        self.assertEqual(len(rotated) % Blowfish.block_size, 0)

        hex = self.pdb._bin_to_hex(rotated)
        bin = self.pdb._hex_to_bin(hex)
        self.assertEqual(bin, rotated)
        
        unrotated = self.pdb._unrotate(bin)
        self.assertEqual(str, unrotated)

    def test_encription(self):
        strings = ["FIGARO ENCRYPTION TEST", "small"]
        for str in strings:
            encrypted = self.pdb.encrypt(str)
            decrypted = self.pdb.decrypt(encrypted)
            self.assertEqual(str, decrypted)

    def test_passwordEncryption(self):
        'Encrypted password should be 48 character long'
        pwdstr = 'shortpass'
        encrypted = self.pdb.encrypt(pwdstr, 1)
        self.assertEqual(len(encrypted), FPM_PASSWORD_LEN*2)
        decrypted = self.pdb.decrypt(encrypted)
        self.assertEqual(pwdstr, decrypted)


class SavedFigaroTestCase(PDBFigaroTestCase):
    def setUp(self):
        pdb = PDBFigaro()
        pdb.open(self.password, fname='test/fpm.sample')
        pdb.save(fname="fpm.saved")
        self.pdb = PDBFigaro()
        self.pdb.open(self.password, fname='fpm.saved')

    def tearDown(self):
        os.remove('fpm.saved')
        

class FigaroCryptoTestCase(unittest.TestCase):
    def test_unrotate(self):
        pdb = PDBFigaro()
        unrotated = pdb._unrotate('FIGARO\x00\xe3')
        self.assertEqual(unrotated, 'FIGARO')

def suite():
    l = [
        unittest.makeSuite(PDBFigaroTestCase, 'test'),
        unittest.makeSuite(SavedFigaroTestCase, 'test'),
        unittest.makeSuite(FigaroCryptoTestCase, 'test')
    ]
    return unittest.TestSuite(l)

if __name__ == "__main__":
    unittest.main()

