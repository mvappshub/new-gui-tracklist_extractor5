from __future__ import annotations
import io
from pathlib import Path
from typing import List

try:
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError as e:
    raise ImportError(f"Missing PDF processing libraries: {e}. Please run 'pip install PyMuPDF Pillow'")

class PdfImageRenderer:
    """Adapter for rendering PDF pages into PIL Images using PyMuPDF."""

    def render(self, pdf_path: Path, dpi: int = 300) -> List[Image.Image]:
        """
        Renders each page of a PDF file into a list of PIL Image objects.

        Args:
            pdf_path: The path to the PDF file.
            dpi: The resolution (dots per inch) for rendering.

        Returns:
            A list of PIL Image objects, one for each page.
        """
        images = []
        doc = fitz.open(str(pdf_path))
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
            images.append(img)
        return images
