import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_project import validate

class SkillStructureTests(unittest.TestCase):
    def test_skill_metadata_and_references(self):
        self.assertEqual(validate(), [])

if __name__=="__main__":
    unittest.main()
