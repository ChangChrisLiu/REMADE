import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.build_code_index import python_files


class InventoryTests(unittest.TestCase):
    def test_index_order_does_not_depend_on_host_path_case_rules(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'a.py').write_text('')
            (root / 'B.py').write_text('')
            with patch('tools.build_code_index.ROOT', root):
                self.assertEqual([p.name for p in python_files()], ['B.py', 'a.py'])
