"""
Example: Auto-detection of design areas
Let the system automatically find where to place designs
"""

from mockup_generator import MockupGenerator
from mockup_generator.auto_detect import TemplateDetector
from PIL import Image

# Enable auto-detection (no need to specify placements)
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    auto_detect=True  # Enable auto-detection
)

# Optional: Test detection on a single template first
detector = TemplateDetector()
template = Image.open("templates/tshirt.png")
detected_area = detector.detect_design_area(template)

if detected_area:
    print(f"Detected area: x={detected_area[0]}, y={detected_area[1]}, "
          f"w={detected_area[2]}, h={detected_area[3]}")

    # Visualize the detection (optional)
    viz = detector.visualize_detection(template, detected_area)
    viz.save("detection_preview.png")
    print("Detection visualization saved to detection_preview.png")

# Generate mockups with auto-detection
results = generator.generate_mockups(
    export_formats=["png"],
    parallel=True
)

stats = generator.get_stats()
print(f"\nGenerated {stats['processed']} mockups using auto-detection!")
