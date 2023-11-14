import tempfile
from os import path
import unittest

from dblp_service.lib.predef.inplace_filewriter import inplace

class InplaceFilewriteTest(unittest.TestCase):
    def test_inplace(self):
        linetext = 'line 1'
        with tempfile.TemporaryDirectory() as tmpdirname:
            myfile = path.join(tmpdirname, 'myfile.txt')
            with open(myfile, "w") as f:
                f.write(linetext)

            with inplace(myfile) as (fin, fout):
                line = fin.readline()
                self.assertEqual(line, linetext)
                fout.write(f"inplace> {line}")

            with inplace(myfile) as (fin, fout):
                line = fin.readline()
                self.assertEqual(line, f"inplace> {linetext}")
                fout.write(f"inplace> {line}")
