"""
Example: Configuration-based generation
Use a YAML config file for all settings
"""

from mockup_generator import MockupGenerator
from mockup_generator.config import Config

# Load configuration from file
config = Config("config/config.yaml")

# Get settings from config
folders = config.get_folders()
placements = config.get_template_placements()
effects = config.get_effects()
formats = config.get_export_formats()
processing = config.get_processing_settings()

# Create generator from config
generator = MockupGenerator(
    design_folder=folders['designs'],
    template_folder=folders['templates'],
    output_folder=folders['output'],
    template_placements=placements,
    auto_detect=config.is_auto_detection_enabled()
)

# Generate using config settings
print("Generating mockups using config file...")
results = generator.generate_mockups(
    effects=effects,
    export_formats=formats,
    parallel=processing['parallel'],
    max_workers=processing['max_workers'],
    progress_bar=processing['progress_bar']
)

stats = generator.get_stats()
print(f"\n✓ Generated {stats['processed']} mockups!")
print(f"Settings loaded from: {config.config_path}")
