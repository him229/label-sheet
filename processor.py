"""
Image processor for rotation and transformation.
"""
from PIL import Image


class ImageProcessor:
    """Handles image transformations like rotation."""
    
    @staticmethod
    def rotate_image(image: Image.Image, rotation: int) -> Image.Image:
        """
        Rotate an image by the specified degrees.
        
        Args:
            image: PIL Image to rotate
            rotation: Rotation angle in degrees (positive = counter-clockwise)
            
        Returns:
            Rotated PIL Image
        """
        if rotation == 0:
            return image
        
        # Rotate counter-clockwise (PIL's default)
        # Expand to fit the rotated image without cropping
        return image.rotate(rotation, expand=True)
    
    @staticmethod
    def fit_to_box(
        image: Image.Image, 
        max_width: float, 
        max_height: float
    ) -> tuple[Image.Image, float, float]:
        """
        Resize image to fit within a bounding box while maintaining aspect ratio.
        
        Args:
            image: PIL Image to resize
            max_width: Maximum width in points
            max_height: Maximum height in points
            
        Returns:
            Tuple of (resized_image, final_width, final_height)
        """
        img_width, img_height = image.size
        img_aspect = img_width / img_height
        box_aspect = max_width / max_height
        
        if img_aspect > box_aspect:
            # Image is wider - fit to width
            new_width = max_width
            new_height = max_width / img_aspect
        else:
            # Image is taller - fit to height
            new_height = max_height
            new_width = max_height * img_aspect
        
        return image, new_width, new_height