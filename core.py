"""
Input handler for loading PDF pages and images.
"""
from pathlib import Path
from typing import Optional
from PIL import Image
from pdf2image import convert_from_path


class InputHandler:
    """Handles loading and extracting pages from PDFs and images."""
    
    @staticmethod
    def load_pdf_page(pdf_path: Path, page_spec: str = "last", dpi: int = 300) -> Image.Image:
        """
        Load a specific page from a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            page_spec: Page specifier ("last", "second-last", or numeric string where
                1/0 = first page, -1 = last page, -2 = second-last, etc.)
            dpi: DPI for rendering the PDF page
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If page specification is invalid
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Convert entire PDF to images
        images = convert_from_path(str(pdf_path), dpi=dpi)
        
        if not images:
            raise ValueError(f"PDF has no pages: {pdf_path}")
        
        # Parse page specification
        if page_spec == "last":
            return images[-1]
        elif page_spec == "second-last":
            if len(images) < 2:
                raise ValueError(f"PDF doesn't have a second-last page: {pdf_path}")
            return images[-2]
        else:
            # Try to parse as page number (0-indexed)
            try:
                page_num = int(page_spec)
                if page_num == 0:
                    page_index = 0
                elif page_num > 0:
                    page_index = page_num - 1
                else:
                    page_index = len(images) + page_num
                if page_index < 0 or page_index >= len(images):
                    raise ValueError(
                        f"Page number {page_num} out of range (PDF has {len(images)} pages)"
                    )
                return images[page_index]
            except ValueError:
                raise ValueError(
                    f"Invalid page specification: {page_spec}. "
                    f"Use 'last', 'second-last', or a page number (1-{len(images)})"
                )
    
    @staticmethod
    def load_image(image_path: Path) -> Image.Image:
        """
        Load an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If file is not a valid image
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            img = Image.open(image_path)
            # Convert to RGB if necessary (e.g., HEIC, PNG with transparency)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            return img
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {e}")
    
    @staticmethod
    def load_input(file_path: Path, page_spec: str = "last", dpi: int = 300) -> Image.Image:
        """
        Load input from either PDF or image file.
        
        Args:
            file_path: Path to the file
            page_spec: Page specification (only used for PDFs)
            dpi: DPI for PDF rendering
            
        Returns:
            PIL Image object
        """
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return InputHandler.load_pdf_page(file_path, page_spec, dpi)
        elif suffix in ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.bmp', '.gif']:
            return InputHandler.load_image(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported: .pdf, .jpg, .jpeg, .png, .heic, .heif, .bmp, .gif"
            )