import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ManagedCopyTests(unittest.TestCase):
    def test_installed_runtime_and_schema_copies_match_core_sources(self):
        pairs = (
            ("runtime/contracts.py", ".context/tools/contracts.py"),
            ("runtime/capsule_runtime.py", ".context/tools/capsule_runtime.py"),
            ("schemas/capsule.schema.json", ".context/tools/schemas/capsule.schema.json"),
            ("schemas/manifest.schema.json", ".context/tools/schemas/manifest.schema.json"),
            ("schemas/index.schema.json", ".context/tools/schemas/index.schema.json"),
            ("schemas/resume.schema.json", ".context/tools/schemas/resume.schema.json"),
        )
        for source, installed in pairs:
            with self.subTest(source=source):
                self.assertEqual(
                    (ROOT / source).read_bytes(),
                    (ROOT / installed).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
