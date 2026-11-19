import importlib.util
from pathlib import Path
import sys
import types
import unittest

# Test pure validation without installing HA, by parsing only its function.
import ast
path = Path(__file__).parents[2] / 'custom_components/pironman5/infrared.py'
module = ast.parse(path.read_text())
func = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'valid_timings')
namespace = {}
exec(compile(ast.Module(body=[func], type_ignores=[]), str(path), 'exec'), namespace)
valid = namespace['valid_timings']

class TestTimings(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(valid([900,-900]*4))
    def test_invalid(self):
        for case in ([900,-900]*3, [900,-900]*257, [900,-900,100,100]*2,
                     [True,-2]*4, [0,-2]*4, [900,-1_000_001]*4):
            self.assertFalse(valid(case), case)

if __name__ == '__main__':
    unittest.main()
