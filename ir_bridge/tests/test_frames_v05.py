import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'host'))
import unittest
from pironman_ir_raw_v06 import Frames, PULSE, SPACE, TIMEOUT, OVERFLOW

class FrameTests(unittest.TestCase):
    def test_frame(self):
        f = Frames(min_edges=4)
        words = [PULSE | 900, SPACE | 900, PULSE | 1800, SPACE | 800,
                 PULSE | 900, SPACE | 900, PULSE | 900, TIMEOUT | 130000]
        out = [o for w in words for o in f.ingest(w)]
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]['timings'], [900, -900, 1800, -800, 900, -900, 900])

    def test_gap_split(self):
        f = Frames(min_edges=4)
        words = [PULSE | 900, SPACE | 900, PULSE | 900, SPACE | 900,
                 PULSE | 900, SPACE | 900, PULSE | 900, SPACE | 90000]
        out = [o for w in words for o in f.ingest(w)]
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]['timings'][-1],900)

    def test_overflow(self):
        f = Frames(min_edges=2)
        for w in [PULSE | 900, SPACE | 900, OVERFLOW, TIMEOUT | 100000]:
            self.assertEqual(f.ingest(w),[])

if __name__ == '__main__':
    unittest.main()
