"""
Visual effects for mockups: shadows, perspective transforms, etc.
"""

from PIL import Image, ImageFilter, ImageDraw, ImageChops
from typing import Tuple, Optional
import numpy as np
from PIL import ImageTransform


class ShadowEffect:
    """
    Add drop shadows to designs on mockups
    """

    def apply(
        self,
        mockup: Image.Image,
        design: Image.Image,
        position: Tuple[int, int],
        offset: Tuple[int, int] = (5, 5),
        blur_radius: int = 10,
        opacity: float = 0.5,
        color: Tuple[int, int, int] = (0, 0, 0),
    ) -> Image.Image:
        """
        Apply drop shadow effect

        Args:
            mockup: Base mockup image
            design: Design image to create shadow for
            position: Position of design on mockup
            offset: Shadow offset (x, y)
            blur_radius: Shadow blur amount
            opacity: Shadow opacity (0-1)
            color: Shadow color RGB

        Returns:
            Mockup with shadow applied
        """
        # Create shadow layer
        shadow = Image.new("RGBA", mockup.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)

        # Get design bounds
        x, y = position
        w, h = design.size

        # Create shadow shape from design alpha
        shadow_pos = (x + offset[0], y + offset[1])

        # Create a solid color version of the design
        shadow_design = Image.new("RGBA", design.size, color + (int(255 * opacity),))

        # Use design's alpha as mask
        shadow_design.putalpha(design.getchannel("A"))

        # Paste shadow at offset position
        shadow.paste(shadow_design, shadow_pos, shadow_design)

        # Blur the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

        # Composite shadow under the mockup
        result = Image.alpha_composite(shadow, mockup)

        return result


class PerspectiveEffect:
    """
    Apply perspective transforms to mockups for realistic 3D effects
    """

    def apply(
        self,
        image: Image.Image,
        coeffs: Optional[Tuple[float, ...]] = None,
        source_points: Optional[list] = None,
        dest_points: Optional[list] = None,
    ) -> Image.Image:
        """
        Apply perspective transformation

        Args:
            image: Image to transform
            coeffs: Perspective transform coefficients (8 values)
            source_points: Source quadrilateral points [(x,y), ...]
            dest_points: Destination quadrilateral points [(x,y), ...]

        Returns:
            Transformed image
        """
        if coeffs:
            # Use provided coefficients
            return image.transform(
                image.size,
                Image.Transform.PERSPECTIVE,
                coeffs,
                Image.Resampling.BICUBIC,
            )
        elif source_points and dest_points:
            # Calculate coefficients from point correspondence
            coeffs = self._find_coeffs(source_points, dest_points)
            return image.transform(
                image.size,
                Image.Transform.PERSPECTIVE,
                coeffs,
                Image.Resampling.BICUBIC,
            )
        else:
            # No transform, return original
            return image

    def _find_coeffs(self, source_coords, target_coords):
        """
        Find perspective transform coefficients

        Based on: https://stackoverflow.com/questions/14177744/
        """
        matrix = []

        for s, t in zip(source_coords, target_coords):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0] * t[0], -s[0] * t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1] * t[0], -s[1] * t[1]])

        A = np.matrix(matrix, dtype=float)
        B = np.array(source_coords).reshape(8)

        res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
        return np.array(res).reshape(8)

    def create_tilt_effect(
        self, image: Image.Image, tilt_x: float = 0, tilt_y: float = 0
    ) -> Image.Image:
        """
        Create a simple tilt effect

        Args:
            image: Image to tilt
            tilt_x: Horizontal tilt factor (-1 to 1)
            tilt_y: Vertical tilt factor (-1 to 1)

        Returns:
            Tilted image
        """
        w, h = image.size

        # Calculate perspective points based on tilt
        offset_x = int(w * abs(tilt_x) * 0.2)
        offset_y = int(h * abs(tilt_y) * 0.2)

        # Source points (corners of original image)
        source = [(0, 0), (w, 0), (w, h), (0, h)]

        # Destination points (tilted)
        dest = [
            (offset_x if tilt_x > 0 else 0, offset_y if tilt_y > 0 else 0),
            (w - offset_x if tilt_x < 0 else w, offset_y if tilt_y > 0 else 0),
            (w - offset_x if tilt_x < 0 else w, h - offset_y if tilt_y < 0 else h),
            (offset_x if tilt_x > 0 else 0, h - offset_y if tilt_y < 0 else h),
        ]

        return self.apply(image, source_points=source, dest_points=dest)


class FilterEffect:
    """
    Additional filter effects for mockups
    """

    @staticmethod
    def apply_brightness(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """
        Adjust brightness (factor: 0.0 = black, 1.0 = original, 2.0 = double bright)
        """
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_contrast(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """
        Adjust contrast (factor: 0.0 = gray, 1.0 = original, 2.0 = high contrast)
        """
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_saturation(image: Image.Image, factor: float = 1.0) -> Image.Image:
        """
        Adjust color saturation (factor: 0.0 = grayscale, 1.0 = original)
        """
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_sharpen(image: Image.Image, radius: int = 2) -> Image.Image:
        """
        Sharpen image
        """
        return image.filter(ImageFilter.UnsharpMask(radius=radius, percent=150))
