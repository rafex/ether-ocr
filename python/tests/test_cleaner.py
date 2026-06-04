import unittest

from ether_ocr.cleaner import clean_extracted_text, count_paragraphs


class CleanerTest(unittest.TestCase):
    def test_removes_page_numbers_and_normalizes_layout(self):
        raw = """
        1
        TITULO PRIMERO



        Articulo 1    Este reglamento regula la circulacion.
        25
        CAPITULO I    Disposiciones generales
        """

        cleaned = clean_extracted_text(raw)

        self.assertNotIn("\n1\n", cleaned)
        self.assertNotIn("\n25\n", cleaned)
        self.assertIn("Articulo 1 Este reglamento", cleaned)
        self.assertNotIn("    ", cleaned)
        self.assertGreaterEqual(count_paragraphs(cleaned), 2)

    def test_separates_accented_legal_headings(self):
        raw = "TÍTULO PRIMERO\nArtículo 1    Texto.\nCAPÍTULO I\nSECCIÓN A"

        cleaned = clean_extracted_text(raw)

        self.assertIn("\n\nArtículo 1 Texto.", cleaned)
        self.assertIn("\n\nCAPÍTULO I", cleaned)
        self.assertIn("\n\nSECCIÓN A", cleaned)


if __name__ == "__main__":
    unittest.main()
