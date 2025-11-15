"""
Example: Basic mockup generation
Simple usage without configuration file
"""

from mockup_generator import MockupGenerator

# Define template placements manually
template_placements = {
    "tshirt.png": (150, 200, 300, 300),
    "mug.png": (100, 150, 250, 250),
}

# Create generator
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    template_placements=template_placements
)

# Generate mockups (PNG only, no effects)
results = generator.generate_mockups(
    export_formats=["png"],
    parallel=True,
    max_workers=4
)

# Print statistics
stats = generator.get_stats()
print(f"Generated {stats['processed']} mockups!")
