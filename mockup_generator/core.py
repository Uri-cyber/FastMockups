"""
Core mockup generation engine with advanced features
"""

from PIL import Image, ImageFilter
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from tqdm import tqdm
import concurrent.futures
from .effects import ShadowEffect, PerspectiveEffect
from .formats import ExportManager
from .auto_detect import TemplateDetector


class MockupGenerator:
    """
    Advanced mockup generator with support for:
    - Batch processing with progress bars
    - Drop shadows and perspective transforms
    - Multi-format export
    - Auto-detection of design areas
    - Cloud storage integration
    """

    def __init__(
        self,
        design_folder: str = "designs",
        template_folder: str = "templates",
        output_folder: str = "mockup_output",
        template_placements: Optional[Dict[str, Tuple[int, int, int, int]]] = None,
        auto_detect: bool = False,
    ):
        self.design_folder = Path(design_folder)
        self.template_folder = Path(template_folder)
        self.output_folder = Path(output_folder)
        self.template_placements = template_placements or {}
        self.auto_detect = auto_detect

        # Create output folder
        self.output_folder.mkdir(exist_ok=True)

        # Initialize components
        self.shadow_effect = ShadowEffect()
        self.perspective_effect = PerspectiveEffect()
        self.export_manager = ExportManager()
        self.template_detector = TemplateDetector()

        # Statistics
        self.stats = {
            "processed": 0,
            "failed": 0,
            "total": 0,
        }

    def resize_and_fit(
        self, design_img: Image.Image, target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Resize design image to fit target size with high-quality resampling
        """
        return design_img.resize(target_size, Image.LANCZOS)

    def composite_image(
        self,
        template_img: Image.Image,
        design_img: Image.Image,
        position: Tuple[int, int],
    ) -> Image.Image:
        """
        Composite design onto template with alpha blending
        """
        template_img.paste(design_img, position, design_img)
        return template_img

    def apply_effects(
        self,
        mockup: Image.Image,
        design_img: Image.Image,
        position: Tuple[int, int],
        effects: Optional[Dict] = None,
    ) -> Image.Image:
        """
        Apply visual effects to the mockup

        Effects can include:
        - shadow: Drop shadow parameters
        - perspective: Perspective transform parameters
        - blur: Blur radius
        """
        if not effects:
            return mockup

        # Apply shadow effect
        if "shadow" in effects and effects["shadow"]:
            shadow_params = effects["shadow"]
            mockup = self.shadow_effect.apply(
                mockup,
                design_img,
                position,
                offset=shadow_params.get("offset", (5, 5)),
                blur_radius=shadow_params.get("blur", 10),
                opacity=shadow_params.get("opacity", 0.5),
            )

        # Apply perspective transform
        if "perspective" in effects and effects["perspective"]:
            perspective_params = effects["perspective"]
            mockup = self.perspective_effect.apply(
                mockup, perspective_params.get("coeffs")
            )

        # Apply blur
        if "blur" in effects and effects["blur"]:
            mockup = mockup.filter(ImageFilter.GaussianBlur(effects["blur"]))

        return mockup

    def get_placement_info(
        self, template_file: Path
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Get placement info for a template, either from config or auto-detection
        """
        template_name = template_file.name

        # Check manual placements first
        if template_name in self.template_placements:
            return self.template_placements[template_name]

        # Auto-detect if enabled
        if self.auto_detect:
            try:
                template_img = Image.open(template_file)
                placement = self.template_detector.detect_design_area(template_img)
                if placement:
                    return placement
            except Exception as e:
                print(f"Auto-detection failed for {template_name}: {e}")

        return None

    def process_single_mockup(
        self,
        design_file: Path,
        template_file: Path,
        effects: Optional[Dict] = None,
        export_formats: Optional[List[str]] = None,
        output_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict:
        """
        Process a single design-template combination

        Returns dict with status and output paths
        """
        result = {"status": "failed", "outputs": [], "error": None}

        try:
            # Load images
            design_img = Image.open(design_file).convert("RGBA")
            template_img = Image.open(template_file).convert("RGBA")

            # Get placement info
            placement = self.get_placement_info(template_file)
            if not placement:
                result["error"] = f"No placement info for {template_file.name}"
                return result

            x, y, w, h = placement

            # Resize design
            resized_design = self.resize_and_fit(design_img, (w, h))

            # Create base mockup
            mockup = self.composite_image(
                template_img.copy(), resized_design, (x, y)
            )

            # Apply effects
            if effects:
                mockup = self.apply_effects(mockup, resized_design, (x, y), effects)

            # Generate output filename
            if not output_name:
                output_name = (
                    f"{design_file.stem}_{template_file.stem}_mockup"
                )

            # Export in multiple formats
            export_formats = export_formats or ["png"]
            for fmt in export_formats:
                output_path = self.output_folder / f"{output_name}.{fmt}"
                self.export_manager.export(mockup, output_path, fmt)
                result["outputs"].append(str(output_path))

            result["status"] = "success"
            self.stats["processed"] += 1

            if progress_callback:
                progress_callback()

        except Exception as e:
            result["error"] = str(e)
            self.stats["failed"] += 1
            print(f"Error processing {design_file.name} + {template_file.name}: {e}")

        return result

    def generate_mockups(
        self,
        effects: Optional[Dict] = None,
        export_formats: Optional[List[str]] = None,
        parallel: bool = True,
        max_workers: int = 4,
        progress_bar: bool = True,
    ) -> List[Dict]:
        """
        Generate all mockups with batch processing and progress tracking

        Args:
            effects: Visual effects to apply
            export_formats: List of export formats (png, jpg, webp, pdf)
            parallel: Use parallel processing
            max_workers: Number of parallel workers
            progress_bar: Show progress bar

        Returns:
            List of result dictionaries
        """
        # Get all design and template files
        design_files = list(self.design_folder.glob("*.png")) + \
                      list(self.design_folder.glob("*.jpg")) + \
                      list(self.design_folder.glob("*.jpeg"))

        template_files = list(self.template_folder.glob("*.png"))

        # Calculate total combinations
        total = len(design_files) * len(template_files)
        self.stats["total"] = total

        if total == 0:
            print("No designs or templates found!")
            return []

        print(f"Generating {total} mockups from {len(design_files)} designs and {len(template_files)} templates...")

        results = []

        # Create progress bar
        pbar = tqdm(total=total, desc="Generating mockups", disable=not progress_bar)

        def update_progress():
            pbar.update(1)

        # Generate all combinations
        tasks = [
            (design, template)
            for design in design_files
            for template in template_files
        ]

        if parallel and len(tasks) > 1:
            # Parallel processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for design, template in tasks:
                    future = executor.submit(
                        self.process_single_mockup,
                        design,
                        template,
                        effects,
                        export_formats,
                        None,
                        update_progress,
                    )
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
        else:
            # Sequential processing
            for design, template in tasks:
                result = self.process_single_mockup(
                    design, template, effects, export_formats, None, update_progress
                )
                results.append(result)

        pbar.close()

        # Print summary
        print(f"\n✓ Successfully processed: {self.stats['processed']}/{total}")
        if self.stats["failed"] > 0:
            print(f"✗ Failed: {self.stats['failed']}/{total}")

        return results

    def get_stats(self) -> Dict:
        """Get generation statistics"""
        return self.stats.copy()
