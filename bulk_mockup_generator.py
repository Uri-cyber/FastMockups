# Bulk Product Mockup Generator with Claude Code
# Uses Pillow for image processing and mockup compositing

from PIL import Image
import os

# === Configuration Section ===
# Folder paths for designs, templates, and output mockups
design_folder = "designs"
template_folder = "templates"
output_folder = "mockup_output"

# Template placement info: filename => (x, y, width, height)
# Adjust coordinates based on your template design area
template_placements = {
    "template1.png": (100, 150, 400, 400),
    "template2.png": (50, 100, 350, 350),
}

# Ensure output folder exists to save mockups
os.makedirs(output_folder, exist_ok=True)

# === Utility Functions ===

def resize_and_fit(design_img, target_size):
    """
    Resize design image to fit the target size with anti-aliasing.
    Maintains image quality when scaling.
    """
    return design_img.resize(target_size, Image.LANCZOS)

def composite_image(template_img, design_img, position):
    """
    Paste the design image onto the template at the given position
    using the design's alpha channel for transparency.
    """
    template_img.paste(design_img, position, design_img)
    return template_img

def save_image(img, folder, filename):
    """
    Save the final composited mockup PNG image to output folder.
    """
    output_path = os.path.join(folder, filename)
    img.save(output_path, "PNG")
    print(f"Saved mockup: {output_path}")

# === Main Function ===

def generate_mockups():
    """
    Generate bulk mockups by compositing each design image with each template.
    Supports multiple designs and templates with configurable placement.
    """
    # Load all design images from the design folder
    designs = [f for f in os.listdir(design_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
    # Load all template images from the template folder
    templates = [f for f in os.listdir(template_folder) if f.endswith(".png")]

    for design_file in designs:
        design_path = os.path.join(design_folder, design_file)
        design_img = Image.open(design_path).convert("RGBA")  # Use RGBA to support transparency

        for template_file in templates:
            template_path = os.path.join(template_folder, template_file)
            template_img = Image.open(template_path).convert("RGBA")

            # Skip if no placement info available for this template
            if template_file not in template_placements:
                print(f"No placement info for template {template_file}, skipping.")
                continue

            # Extract placement position and size for design
            x, y, w, h = template_placements[template_file]
            resized_design = resize_and_fit(design_img, (w, h))

            # Composite design onto the template at specified position
            final_mockup = composite_image(template_img.copy(), resized_design, (x, y))

            # Generate output filename
            output_filename = f"{os.path.splitext(design_file)[0]}_{os.path.splitext(template_file)[0]}_mockup.png"
            # Save result
            save_image(final_mockup, output_folder, output_filename)

# Entry point
if __name__ == "__main__":
    generate_mockups()
