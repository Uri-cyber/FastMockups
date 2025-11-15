"""
Auto-detection of design areas on templates using computer vision
"""

from PIL import Image, ImageDraw
import numpy as np
from typing import Optional, Tuple, List
import cv2


class TemplateDetector:
    """
    Automatically detect design placement areas on product templates
    Uses edge detection, contour finding, and color analysis
    """

    def __init__(self):
        self.debug_mode = False

    def detect_design_area(
        self,
        template: Image.Image,
        method: str = "contour",
        min_area_ratio: float = 0.05,
        max_area_ratio: float = 0.7,
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the primary design area on a template

        Args:
            template: Template image
            method: Detection method ('contour', 'color', 'edge')
            min_area_ratio: Minimum area as ratio of image (0-1)
            max_area_ratio: Maximum area as ratio of image (0-1)

        Returns:
            Tuple of (x, y, width, height) or None if detection fails
        """
        if method == "contour":
            return self._detect_by_contour(template, min_area_ratio, max_area_ratio)
        elif method == "color":
            return self._detect_by_color(template, min_area_ratio, max_area_ratio)
        elif method == "edge":
            return self._detect_by_edges(template, min_area_ratio, max_area_ratio)
        else:
            # Try all methods and return best result
            for m in ["contour", "color", "edge"]:
                result = self.detect_design_area(template, m, min_area_ratio, max_area_ratio)
                if result:
                    return result
            return None

    def _detect_by_contour(
        self, template: Image.Image, min_ratio: float, max_ratio: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect design area by finding rectangular contours
        """
        # Convert to numpy array
        img_array = np.array(template.convert("RGB"))

        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Calculate total image area
        total_area = template.width * template.height

        # Find largest rectangular contour within size constraints
        best_rect = None
        best_area = 0

        for contour in contours:
            # Approximate to polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # Check if it's roughly rectangular (4 corners)
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                area_ratio = area / total_area

                # Check if area is within acceptable range
                if min_ratio <= area_ratio <= max_ratio:
                    if area > best_area:
                        best_area = area
                        best_rect = (x, y, w, h)

        return best_rect

    def _detect_by_color(
        self, template: Image.Image, min_ratio: float, max_ratio: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect design area by finding uniform color regions (common in mockup templates)
        """
        img_array = np.array(template.convert("RGB"))

        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        # Find regions with low saturation (white/gray areas often indicate design zones)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])

        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Find contours in mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        total_area = template.width * template.height
        best_rect = None
        best_area = 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            area_ratio = area / total_area

            if min_ratio <= area_ratio <= max_ratio:
                # Prefer more square-like rectangles
                aspect_ratio = w / h if h > 0 else 0
                if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio
                    if area > best_area:
                        best_area = area
                        best_rect = (x, y, w, h)

        return best_rect

    def _detect_by_edges(
        self, template: Image.Image, min_ratio: float, max_ratio: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect design area using edge detection
        """
        img_array = np.array(template.convert("RGB"))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Dilate edges to close gaps
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        total_area = template.width * template.height
        best_rect = None
        best_area = 0

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            area_ratio = area / total_area

            if min_ratio <= area_ratio <= max_ratio:
                if area > best_area:
                    best_area = area
                    best_rect = (x, y, w, h)

        return best_rect

    def detect_multiple_areas(
        self, template: Image.Image, max_areas: int = 5
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect multiple design areas on a template (for multi-view mockups)

        Args:
            template: Template image
            max_areas: Maximum number of areas to detect

        Returns:
            List of (x, y, width, height) tuples
        """
        img_array = np.array(template.convert("RGB"))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Sort by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        areas = []
        total_area = template.width * template.height

        for contour in contours[:max_areas]:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            area_ratio = area / total_area

            # Only include significant areas
            if 0.05 <= area_ratio <= 0.7:
                areas.append((x, y, w, h))

        return areas

    def visualize_detection(
        self, template: Image.Image, detected_area: Tuple[int, int, int, int]
    ) -> Image.Image:
        """
        Visualize detected area on template (for debugging)

        Args:
            template: Template image
            detected_area: Detected area (x, y, w, h)

        Returns:
            Template with detected area highlighted
        """
        img = template.copy()
        draw = ImageDraw.Draw(img)

        x, y, w, h = detected_area

        # Draw rectangle
        draw.rectangle([x, y, x + w, y + h], outline="red", width=5)

        # Draw crosshairs at center
        center_x = x + w // 2
        center_y = y + h // 2
        cross_size = 20

        draw.line(
            [center_x - cross_size, center_y, center_x + cross_size, center_y],
            fill="red",
            width=3,
        )
        draw.line(
            [center_x, center_y - cross_size, center_x, center_y + cross_size],
            fill="red",
            width=3,
        )

        return img

    def save_detection_visualization(
        self,
        template: Image.Image,
        detected_area: Tuple[int, int, int, int],
        output_path: str,
    ):
        """
        Save visualization of detected area
        """
        viz = self.visualize_detection(template, detected_area)
        viz.save(output_path)
        print(f"Detection visualization saved to: {output_path}")
