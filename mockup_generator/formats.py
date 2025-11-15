"""
Multi-format export manager for mockups
Supports PNG, JPG, WebP, PDF, and more
"""

from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any
import io


class ExportManager:
    """
    Handle exporting mockups to multiple formats with optimized settings
    """

    # Default quality settings per format
    DEFAULT_QUALITY = {
        "png": {"optimize": True, "compress_level": 6},
        "jpg": {"quality": 95, "optimize": True, "progressive": True},
        "jpeg": {"quality": 95, "optimize": True, "progressive": True},
        "webp": {"quality": 90, "method": 6},
        "pdf": {"resolution": 100.0, "quality": 95},
        "bmp": {},
        "tiff": {"compression": "tiff_lzw"},
    }

    def export(
        self,
        image: Image.Image,
        output_path: Path,
        format: str = "png",
        custom_settings: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Export image to specified format

        Args:
            image: PIL Image to export
            output_path: Output file path
            format: Export format (png, jpg, webp, pdf, etc.)
            custom_settings: Override default export settings

        Returns:
            True if successful, False otherwise
        """
        format = format.lower()

        try:
            # Get export settings
            settings = self.DEFAULT_QUALITY.get(format, {}).copy()
            if custom_settings:
                settings.update(custom_settings)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle format-specific conversions
            export_image = self._prepare_image_for_format(image, format)

            # Export based on format
            if format == "pdf":
                self._export_pdf(export_image, output_path, settings)
            else:
                export_image.save(str(output_path), format=format.upper(), **settings)

            print(f"Exported: {output_path}")
            return True

        except Exception as e:
            print(f"Export failed for {output_path}: {e}")
            return False

    def _prepare_image_for_format(self, image: Image.Image, format: str) -> Image.Image:
        """
        Prepare image for specific format (handle transparency, color modes, etc.)
        """
        if format in ["jpg", "jpeg", "bmp"]:
            # These formats don't support transparency
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                return background
            elif image.mode != "RGB":
                return image.convert("RGB")
            return image

        elif format == "webp":
            # WebP supports both RGB and RGBA
            if image.mode not in ("RGB", "RGBA"):
                return image.convert("RGBA" if "A" in image.mode else "RGB")
            return image

        elif format == "png":
            # PNG supports RGBA
            if image.mode not in ("RGB", "RGBA", "P", "L"):
                return image.convert("RGBA")
            return image

        elif format == "pdf":
            # PDF works best with RGB
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                return background
            elif image.mode != "RGB":
                return image.convert("RGB")
            return image

        return image

    def _export_pdf(self, image: Image.Image, output_path: Path, settings: Dict):
        """
        Export image as PDF with proper settings
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Save as PDF
        image.save(
            str(output_path),
            "PDF",
            resolution=settings.get("resolution", 100.0),
            quality=settings.get("quality", 95),
        )

    def export_multiple_formats(
        self,
        image: Image.Image,
        base_path: Path,
        formats: list = None,
    ) -> Dict[str, bool]:
        """
        Export image to multiple formats at once

        Args:
            image: Image to export
            base_path: Base path without extension
            formats: List of formats to export (default: ["png", "jpg", "webp"])

        Returns:
            Dict mapping format to success status
        """
        if formats is None:
            formats = ["png", "jpg", "webp"]

        results = {}

        for fmt in formats:
            output_path = base_path.parent / f"{base_path.stem}.{fmt}"
            results[fmt] = self.export(image, output_path, fmt)

        return results

    def get_supported_formats(self) -> list:
        """
        Get list of supported export formats
        """
        return list(self.DEFAULT_QUALITY.keys())

    def get_format_info(self, format: str) -> Dict:
        """
        Get information about a specific format
        """
        format_info = {
            "png": {
                "name": "PNG",
                "supports_transparency": True,
                "lossless": True,
                "description": "Portable Network Graphics - lossless with transparency",
            },
            "jpg": {
                "name": "JPEG",
                "supports_transparency": False,
                "lossless": False,
                "description": "Joint Photographic Experts Group - lossy compression",
            },
            "jpeg": {
                "name": "JPEG",
                "supports_transparency": False,
                "lossless": False,
                "description": "Joint Photographic Experts Group - lossy compression",
            },
            "webp": {
                "name": "WebP",
                "supports_transparency": True,
                "lossless": False,
                "description": "Modern web format with good compression",
            },
            "pdf": {
                "name": "PDF",
                "supports_transparency": False,
                "lossless": False,
                "description": "Portable Document Format",
            },
            "bmp": {
                "name": "BMP",
                "supports_transparency": False,
                "lossless": True,
                "description": "Bitmap - uncompressed raster format",
            },
            "tiff": {
                "name": "TIFF",
                "supports_transparency": True,
                "lossless": True,
                "description": "Tagged Image File Format - professional format",
            },
        }

        return format_info.get(format.lower(), {})
