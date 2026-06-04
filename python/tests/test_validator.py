import unittest

from ether_ocr.validator import validate_plain_text


class ValidatorTest(unittest.TestCase):
    def test_plain_text_passes(self):
        text = (
            "Articulo 1 Este reglamento regula la circulacion.\n\n"
            "Pregunta: Que debe hacer el conductor?\n"
            "Respuesta: Debe respetar las senales de transito."
        )

        self.assertTrue(validate_plain_text(text).valid)

    def test_markdown_link_fails(self):
        result = validate_plain_text("Consulta la [guia](./guia.md) para mas detalle.")

        self.assertFalse(result.valid)
        self.assertTrue(any("Markdown" in issue for issue in result.issues))

    def test_html_fails(self):
        result = validate_plain_text("<p>Texto</p><div>Mas texto</div>")

        self.assertFalse(result.valid)

    def test_control_chars_fail(self):
        result = validate_plain_text("Texto valido\x00texto roto")

        self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()
