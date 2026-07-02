import tempfile
import unittest
from pathlib import Path

from ether_ocr_core.preparer import prepare_document


class PreparerTest(unittest.TestCase):
    def test_prepares_text_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "raw.txt"
            target = tmp / "clean.txt"
            source.write_text(
                "1\nArticulo 1    Texto legal.\n\n\n2\nArticulo 2    Mas texto.",
                encoding="utf-8",
            )

            result = prepare_document(source, target)

            self.assertTrue(target.exists())
            self.assertEqual(result.output_path, target)
            self.assertGreaterEqual(result.paragraphs, 2)
            self.assertIn("Articulo 1 Texto legal.", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
