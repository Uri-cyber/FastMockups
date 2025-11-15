# FastMockups - Advanced Bulk Product Mockup Generator

<div align="center">

**Professional-grade mockup generation with AI-powered auto-detection, visual effects, and cloud integration**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Web UI](#web-ui) • [Examples](#examples) • [Documentation](#documentation)

</div>

---

## Features

### Core Capabilities
- **Bulk Processing**: Generate thousands of mockups from multiple designs and templates
- **Multi-Format Export**: PNG, JPG, WebP, PDF with optimized quality settings
- **High Performance**: Parallel processing with configurable worker threads
- **Progress Tracking**: Real-time progress bars and statistics

### Visual Effects
- **Drop Shadows**: Customizable shadow effects with blur and opacity control
- **Perspective Transforms**: Apply 3D perspective effects to mockups
- **Image Filters**: Brightness, contrast, saturation, and sharpening

### Smart Automation
- **Auto-Detection**: AI-powered detection of design placement areas using computer vision
- **Smart Fitting**: Automatic image scaling and positioning
- **Batch Operations**: Process hundreds of files with a single command

### Cloud Integration
- **AWS S3 Support**: Direct upload to Amazon S3 buckets
- **Google Cloud Storage**: Seamless GCS integration
- **Public URL Generation**: Automatic public URL generation for uploaded mockups

### User Interfaces
- **Web UI**: Modern drag-and-drop web interface with real-time progress
- **CLI**: Powerful command-line interface with full feature access
- **API**: RESTful API for programmatic integration
- **Python Library**: Import and use in your own Python projects

---

## Installation

### Basic Installation

```bash
git clone <repository-url>
cd FastMockups
pip install -r requirements.txt
```

### Optional Dependencies

For cloud storage support:
```bash
# AWS S3
pip install boto3

# Google Cloud Storage
pip install google-cloud-storage
```

For auto-detection (already included in requirements.txt):
```bash
pip install opencv-python numpy
```

---

## Quick Start

### Method 1: Simple Script (Beginner-Friendly)

```python
from mockup_generator import MockupGenerator

# Define where designs should be placed on templates
template_placements = {
    "tshirt.png": (150, 200, 300, 300),  # (x, y, width, height)
    "mug.png": (100, 150, 250, 250),
}

# Create generator
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    template_placements=template_placements
)

# Generate mockups
generator.generate_mockups()
```

### Method 2: With Auto-Detection (No Manual Placement)

```python
# Auto-detect design areas - no placement configuration needed!
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    auto_detect=True  # Let AI find the placement areas
)

generator.generate_mockups()
```

### Method 3: Advanced CLI

```bash
python generate_mockups_advanced.py \
    --config config/config.yaml \
    --formats png jpg webp \
    --upload-cloud
```

### Method 4: Web UI

```bash
cd web_ui
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## Web UI

The web interface provides a modern, intuitive experience:

### Features
- Drag-and-drop file upload for designs and templates
- Visual configuration of effects and settings
- Real-time progress tracking
- Preview and download generated mockups
- Auto-detection toggle
- Multi-format export selection
- Cloud upload integration

### Starting the Web UI

```bash
cd web_ui
python app.py
```

Access at: `http://localhost:5000`

---

## Project Structure

```
FastMockups/
├── mockup_generator/          # Core library
│   ├── __init__.py
│   ├── core.py               # Main generator
│   ├── effects.py            # Visual effects (shadows, perspective)
│   ├── formats.py            # Multi-format export
│   ├── auto_detect.py        # AI-powered detection
│   ├── cloud_storage.py      # S3, GCS integration
│   └── config.py             # Configuration management
├── web_ui/                    # Web interface
│   ├── app.py                # Flask application
│   └── templates/
│       └── index.html        # UI template
├── examples/                  # Example scripts
│   ├── basic_usage.py
│   ├── with_effects.py
│   ├── auto_detection.py
│   ├── cloud_upload.py
│   └── config_based.py
├── config/
│   └── config.yaml           # Configuration file
├── designs/                   # Your design images
├── templates/                 # Your product templates
├── mockup_output/            # Generated mockups
├── bulk_mockup_generator.py  # Original simple script
├── generate_mockups_advanced.py  # Advanced CLI script
├── requirements.txt
└── README.md
```

---

## Examples

### Basic Usage

```python
from mockup_generator import MockupGenerator

generator = MockupGenerator(
    template_placements={
        "tshirt.png": (150, 200, 300, 300),
    }
)
generator.generate_mockups()
```

See: `examples/basic_usage.py`

### With Visual Effects

```python
effects = {
    "shadow": {
        "offset": (8, 8),
        "blur": 15,
        "opacity": 0.6,
    }
}

generator.generate_mockups(
    effects=effects,
    export_formats=["png", "jpg", "webp"]
)
```

See: `examples/with_effects.py`

### Auto-Detection

```python
from mockup_generator import MockupGenerator
from mockup_generator.auto_detect import TemplateDetector
from PIL import Image

# Test detection on a template
detector = TemplateDetector()
template = Image.open("templates/tshirt.png")
area = detector.detect_design_area(template)

# Visualize detection
viz = detector.visualize_detection(template, area)
viz.save("detection_preview.png")

# Generate with auto-detection
generator = MockupGenerator(auto_detect=True)
generator.generate_mockups()
```

See: `examples/auto_detection.py`

### Cloud Upload

```python
from mockup_generator.cloud_storage import CloudStorageManager, create_s3_storage

# Generate mockups
generator.generate_mockups()

# Upload to S3
cloud_manager = CloudStorageManager()
s3 = create_s3_storage("my-bucket", region="us-east-1")
cloud_manager.add_provider('s3', s3)

results = cloud_manager.upload_mockups(
    Path("mockup_output"),
    's3',
    remote_folder='mockups'
)
```

See: `examples/cloud_upload.py`

### Configuration-Based

```python
from mockup_generator.config import Config

config = Config("config/config.yaml")
generator = MockupGenerator(
    design_folder=config.get('folders.designs'),
    template_placements=config.get_template_placements(),
    auto_detect=config.is_auto_detection_enabled()
)

generator.generate_mockups(
    effects=config.get_effects(),
    export_formats=config.get_export_formats()
)
```

See: `examples/config_based.py`

---

## Configuration

### YAML Configuration File

Edit `config/config.yaml`:

```yaml
folders:
  designs: "designs"
  templates: "templates"
  output: "mockup_output"

template_placements:
  tshirt.png: [150, 200, 300, 300]

auto_detection:
  enabled: true
  method: "contour"

effects:
  shadow:
    enabled: true
    offset: [5, 5]
    blur_radius: 10
    opacity: 0.5

export:
  formats: ["png", "jpg", "webp"]

processing:
  parallel: true
  max_workers: 4

cloud_storage:
  enabled: false
  provider: "s3"
  s3:
    bucket_name: "my-mockups"
    region: "us-east-1"
```

---

## API Reference

### MockupGenerator

```python
from mockup_generator import MockupGenerator

generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    template_placements={},
    auto_detect=False
)

results = generator.generate_mockups(
    effects=None,
    export_formats=["png"],
    parallel=True,
    max_workers=4,
    progress_bar=True
)
```

### Effects

```python
effects = {
    "shadow": {
        "offset": (x, y),
        "blur": radius,
        "opacity": 0.0-1.0
    }
}
```

### Export Formats

Supported formats: `png`, `jpg`, `jpeg`, `webp`, `pdf`, `bmp`, `tiff`

### Auto-Detection

```python
from mockup_generator.auto_detect import TemplateDetector

detector = TemplateDetector()
area = detector.detect_design_area(template_image)
# Returns: (x, y, width, height)
```

---

## Web API Endpoints

When running the web UI, these endpoints are available:

- `POST /api/upload/design` - Upload design images
- `POST /api/upload/template` - Upload template images
- `POST /api/generate` - Start mockup generation
- `GET /api/job/<job_id>` - Check generation status
- `GET /api/mockups` - List all generated mockups
- `GET /api/mockups/<filename>` - Download a mockup
- `POST /api/cloud/upload` - Upload to cloud storage
- `POST /api/templates/detect` - Auto-detect design area

---

## Advanced Features

### Parallel Processing

Process mockups faster using multiple CPU cores:

```python
generator.generate_mockups(
    parallel=True,
    max_workers=8  # Use 8 CPU cores
)
```

### Custom Effects

```python
from mockup_generator.effects import ShadowEffect, FilterEffect

# Apply custom brightness/contrast
effects = {
    "shadow": {"blur": 20, "opacity": 0.7},
}
```

### Cloud Storage

#### AWS S3

```python
from mockup_generator.cloud_storage import create_s3_storage

s3 = create_s3_storage(
    bucket_name="my-bucket",
    aws_access_key_id="...",
    aws_secret_access_key="...",
    region="us-east-1"
)

s3.upload_file(local_path, remote_path)
```

#### Google Cloud Storage

```python
from mockup_generator.cloud_storage import create_gcs_storage

gcs = create_gcs_storage(
    bucket_name="my-bucket",
    credentials_path="service-account.json"
)

gcs.upload_file(local_path, remote_path)
```

---

## Performance Tips

1. **Use Parallel Processing**: Enable `parallel=True` for large batches
2. **Optimize Workers**: Set `max_workers` to your CPU core count
3. **Format Selection**: Only export formats you need
4. **Auto-Detection**: Trades computation for convenience - use manual placement for production
5. **Image Size**: Use appropriately sized templates (4K templates can slow processing)

---

## Troubleshooting

### No Placement Info Error

**Problem**: "No placement info for template X"

**Solution**: Either:
- Add manual placement to config: `template_placements = {"X": (x, y, w, h)}`
- Enable auto-detection: `auto_detect=True`

### Auto-Detection Not Working

**Problem**: Detection fails or incorrect areas found

**Solutions**:
- Ensure template has clear design area
- Try different detection methods: `method="color"` or `method="edge"`
- Adjust area ratio: `min_area_ratio=0.1, max_area_ratio=0.5`
- Use manual placement as fallback

### Low Quality Output

**Problem**: Mockups look pixelated

**Solutions**:
- Use high-resolution design images (2000px+)
- Check template placement size matches template design area
- Increase export quality in config
- Use lossless formats (PNG, TIFF)

### Slow Processing

**Problem**: Generation takes too long

**Solutions**:
- Enable parallel processing
- Increase `max_workers`
- Reduce export formats
- Use smaller template images
- Disable expensive effects

### Cloud Upload Fails

**Problem**: Can't upload to S3/GCS

**Solutions**:
- Check credentials are configured
- Verify bucket name and permissions
- Test connection with AWS CLI / gcloud CLI
- Check internet connectivity

---

## Requirements

- Python 3.7+
- Pillow >= 10.0.0
- OpenCV >= 4.8.0 (for auto-detection)
- NumPy >= 1.24.0
- tqdm >= 4.66.0 (progress bars)
- Flask >= 3.0.0 (web UI)
- PyYAML >= 6.0.0 (configuration)

Optional:
- boto3 >= 1.28.0 (AWS S3)
- google-cloud-storage >= 2.10.0 (GCS)

---

## License

MIT License - free for commercial and personal use.

---

## Contributing

Contributions welcome! Areas for improvement:

- Additional cloud providers (Azure, DigitalOcean Spaces)
- More visual effects (gradients, patterns)
- Video mockup support
- GUI desktop application
- Batch API for enterprise use

---

## Support

- Documentation: This README
- Examples: See `examples/` directory
- Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**Built with Claude Code** - Professional mockup generation made simple.

