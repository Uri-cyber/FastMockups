# FastMockups - Bulk Product Mockup Generator

A Python-based tool for automatically generating product mockups by compositing design images onto template backgrounds. Perfect for e-commerce, marketing materials, and product presentations.

## Features

- **Bulk Processing**: Generate multiple mockups from multiple designs and templates automatically
- **High-Quality Output**: Uses Pillow with LANCZOS resampling for professional results
- **Transparency Support**: Full RGBA support for designs with transparent backgrounds
- **Configurable Placement**: Precise control over design positioning on each template
- **Easy to Use**: Simple configuration and execution

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd FastMockups
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Folder Structure

```
FastMockups/
├── bulk_mockup_generator.py  # Main script
├── designs/                   # Place your design images here (PNG, JPG, JPEG)
├── templates/                 # Place your product templates here (PNG)
├── mockup_output/            # Generated mockups will be saved here
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Quick Start

### 1. Prepare Your Files

**Add Design Images** to the `designs/` folder:
- Supported formats: PNG, JPG, JPEG
- RGBA/transparent designs recommended
- Any resolution (will be resized to fit templates)

**Add Template Images** to the `templates/` folder:
- Format: PNG (with transparency if needed)
- Examples: t-shirt mockups, mug templates, phone case backgrounds, etc.

### 2. Configure Template Placements

Edit `bulk_mockup_generator.py` and update the `template_placements` dictionary with your template coordinates:

```python
template_placements = {
    "template1.png": (100, 150, 400, 400),  # (x, y, width, height)
    "template2.png": (50, 100, 350, 350),
}
```

**How to find coordinates:**
- x, y: Top-left corner position where design should start
- width, height: Size the design should be resized to
- Use an image editor to measure your template's design area

### 3. Run the Generator

```bash
python bulk_mockup_generator.py
```

The script will:
1. Load all designs from `designs/` folder
2. Load all templates from `templates/` folder
3. Generate a mockup for each design × template combination
4. Save results to `mockup_output/` with descriptive filenames

## Output

Mockups are saved with the naming pattern:
```
{design_name}_{template_name}_mockup.png
```

Example:
- Design: `logo.png`
- Template: `tshirt.png`
- Output: `logo_tshirt_mockup.png`

## Customization

### Adding New Templates

1. Add template PNG to `templates/` folder
2. Update `template_placements` with coordinates:

```python
template_placements = {
    "template1.png": (100, 150, 400, 400),
    "your_new_template.png": (75, 200, 500, 500),  # Add this line
}
```

### Advanced Features (Future Extensions)

The script can be extended with:
- **Shadows & Effects**: Add drop shadows or perspective transforms
- **Batch Processing UI**: Web interface for easier usage
- **Cloud Integration**: Upload directly to cloud storage
- **Multiple Export Formats**: Support for JPG, WebP, etc.
- **Smart Fitting**: Auto-detect design areas on templates
- **Watermarking**: Add branding to generated mockups

## Troubleshooting

**"No placement info for template X"**
- Add the template filename and coordinates to `template_placements` dictionary

**Images look pixelated**
- Ensure your design images are high-resolution
- Check that width/height in `template_placements` match your template's design area

**Script can't find designs/templates**
- Verify files are in correct folders (`designs/` and `templates/`)
- Check file extensions are supported (.png, .jpg, .jpeg for designs; .png for templates)

## Requirements

- Python 3.7+
- Pillow (PIL) library

## License

This project is open source and available for use in your projects.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

---

**Built with Claude Code** - Fast, automated mockup generation for your products.
