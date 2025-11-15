"""
Layout engine for positioning content in quadrants.
"""
from dataclasses import dataclass
from typing import Optional
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os

from processor import ImageProcessor


@dataclass
class QuadrantConfig:
    """Configuration for a single quadrant."""
    image: Optional[Image.Image] = None
    rotation: int = 0


class LayoutEngine:
    """Handles positioning and rendering of quadrants."""
    
    def __init__(self, margin_inches: float = 0.25, show_grid: bool = True):
        """
        Initialize layout engine.
        
        Args:
            margin_inches: Margin in inches for each quadrant
            show_grid: Whether to draw grid lines between quadrants
        """
        self.margin = margin_inches * 72  # Convert inches to points
        self.show_grid = show_grid
        self.page_width, self.page_height = letter  # 612 x 792 points
        self.quadrant_width = self.page_width / 2
        self.quadrant_height = self.page_height / 2
    
    def generate_pdf(
        self, 
        output_path: str,
        q1: Optional[QuadrantConfig] = None,
        q2: Optional[QuadrantConfig] = None,
        q3: Optional[QuadrantConfig] = None,
        q4: Optional[QuadrantConfig] = None,
    ) -> None:
        """
        Generate the final PDF with specified quadrant configurations.
        
        Args:
            output_path: Path to save the output PDF
            q1: Configuration for top-left quadrant
            q2: Configuration for top-right quadrant
            q3: Configuration for bottom-left quadrant
            q4: Configuration for bottom-right quadrant
        """
        c = canvas.Canvas(output_path, pagesize=letter)
        
        # Draw quadrants
        quadrants = [
            (q1, 0, 1),  # Top-left
            (q2, 1, 1),  # Top-right
            (q3, 0, 0),  # Bottom-left
            (q4, 1, 0),  # Bottom-right
        ]
        
        temp_files = []
        
        for config, quad_x, quad_y in quadrants:
            if config and config.image:
                temp_file = self._draw_quadrant(c, config, quad_x, quad_y)
                if temp_file:
                    temp_files.append(temp_file)
        
        # Draw grid lines if enabled
        if self.show_grid:
            self._draw_grid(c)
        
        c.save()
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
    
    def _draw_quadrant(
        self, 
        c: canvas.Canvas, 
        config: QuadrantConfig, 
        quad_x: int, 
        quad_y: int
    ) -> Optional[str]:
        """
        Draw a single quadrant with the specified image.
        
        Returns:
            Path to temporary file created (for cleanup), or None
        """
        # Apply rotation
        image = ImageProcessor.rotate_image(config.image, config.rotation)
        
        # Calculate available space (minus margins)
        available_width = self.quadrant_width - (2 * self.margin)
        available_height = self.quadrant_height - (2 * self.margin)
        
        # Fit image to available space
        _, draw_width, draw_height = ImageProcessor.fit_to_box(
            image, available_width, available_height
        )
        
        # Calculate position (centered in quadrant with margins)
        x_offset = (
            quad_x * self.quadrant_width + 
            self.margin + 
            (available_width - draw_width) / 2
        )
        y_offset = (
            quad_y * self.quadrant_height + 
            self.margin + 
            (available_height - draw_height) / 2
        )
        
        # Save image to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            suffix='.jpg', delete=False
        ).name
        image.save(temp_file, 'JPEG', quality=95)
        
        # Draw the image
        c.drawImage(
            temp_file, 
            x_offset, 
            y_offset,
            width=draw_width, 
            height=draw_height,
            preserveAspectRatio=True
        )
        
        return temp_file
    
    def _draw_grid(self, c: canvas.Canvas) -> None:
        """Draw grid lines separating quadrants."""
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(1)
        
        # Vertical line
        c.line(
            self.page_width / 2, 0, 
            self.page_width / 2, self.page_height
        )
        
        # Horizontal line
        c.line(
            0, self.page_height / 2, 
            self.page_width, self.page_height / 2
        )