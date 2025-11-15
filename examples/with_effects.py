"""
Example: Mockup generation with visual effects
Add drop shadows and export to multiple formats
"""

from mockup_generator import MockupGenerator

# Template placements
template_placements = {
    "tshirt.png": (150, 200, 300, 300),
    "phone_case.png": (80, 120, 200, 400),
}

# Create generator
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    template_placements=template_placements
)

# Define effects
effects = {
    "shadow": {
        "offset": (8, 8),      # Shadow offset (x, y)
        "blur": 15,            # Blur radius
        "opacity": 0.6,        # Shadow opacity (0-1)
    }
}

# Generate with effects and multiple formats
results = generator.generate_mockups(
    effects=effects,
    export_formats=["png", "jpg", "webp"],
    parallel=True,
    progress_bar=True
)

print(f"Generated mockups in 3 formats with drop shadows!")
print(f"Check the {generator.output_folder} folder")
