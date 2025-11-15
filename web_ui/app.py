"""
Flask web UI for FastMockups
Provides drag-and-drop interface, real-time progress, and API endpoints
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
import sys
from threading import Thread
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mockup_generator import MockupGenerator
from mockup_generator.cloud_storage import CloudStorageManager, create_s3_storage, create_gcs_storage

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

# Create necessary folders
for folder in ['uploads/designs', 'uploads/templates', 'mockup_output']:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Global storage for generation jobs
generation_jobs = {}

# Cloud storage manager
cloud_manager = CloudStorageManager()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Render main UI"""
    return render_template('index.html')


@app.route('/api/upload/design', methods=['POST'])
def upload_design():
    """Upload design images"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploaded = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = Path('uploads/designs') / filename
            file.save(str(filepath))
            uploaded.append(filename)

    return jsonify({
        'success': True,
        'uploaded': uploaded,
        'count': len(uploaded)
    })


@app.route('/api/upload/template', methods=['POST'])
def upload_template():
    """Upload template images"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploaded = []
    placements = {}

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = Path('uploads/templates') / filename
            file.save(str(filepath))
            uploaded.append(filename)

            # Check if placement info was provided
            placement_key = f"placement_{filename}"
            if placement_key in request.form:
                try:
                    placement_data = json.loads(request.form[placement_key])
                    placements[filename] = tuple(placement_data)
                except:
                    pass

    return jsonify({
        'success': True,
        'uploaded': uploaded,
        'count': len(uploaded),
        'placements': placements
    })


@app.route('/api/generate', methods=['POST'])
def generate_mockups():
    """Generate mockups from uploaded files"""
    data = request.json

    # Extract parameters
    template_placements = data.get('placements', {})
    auto_detect = data.get('auto_detect', False)
    effects = data.get('effects', {})
    export_formats = data.get('formats', ['png'])
    parallel = data.get('parallel', True)
    max_workers = data.get('max_workers', 4)

    # Create unique job ID
    job_id = f"job_{int(time.time() * 1000)}"

    # Initialize generator
    generator = MockupGenerator(
        design_folder='uploads/designs',
        template_folder='uploads/templates',
        output_folder='mockup_output',
        template_placements=template_placements,
        auto_detect=auto_detect
    )

    # Store job info
    generation_jobs[job_id] = {
        'status': 'running',
        'progress': 0,
        'total': 0,
        'results': [],
        'generator': generator
    }

    # Run generation in background thread
    def run_generation():
        try:
            results = generator.generate_mockups(
                effects=effects,
                export_formats=export_formats,
                parallel=parallel,
                max_workers=max_workers,
                progress_bar=False
            )

            generation_jobs[job_id]['status'] = 'completed'
            generation_jobs[job_id]['results'] = results
            generation_jobs[job_id]['stats'] = generator.get_stats()
        except Exception as e:
            generation_jobs[job_id]['status'] = 'failed'
            generation_jobs[job_id]['error'] = str(e)

    thread = Thread(target=run_generation)
    thread.start()

    return jsonify({
        'success': True,
        'job_id': job_id
    })


@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a generation job"""
    if job_id not in generation_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = generation_jobs[job_id]

    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'stats': job.get('stats', {}),
        'results': job.get('results', []),
        'error': job.get('error')
    })


@app.route('/api/mockups', methods=['GET'])
def list_mockups():
    """List all generated mockups"""
    mockup_folder = Path('mockup_output')
    mockups = []

    for file in mockup_folder.glob('*'):
        if file.is_file():
            mockups.append({
                'filename': file.name,
                'size': file.stat().st_size,
                'created': file.stat().st_mtime
            })

    return jsonify({
        'mockups': mockups,
        'count': len(mockups)
    })


@app.route('/api/mockups/<filename>', methods=['GET'])
def download_mockup(filename):
    """Download a generated mockup"""
    return send_from_directory('mockup_output', filename)


@app.route('/api/cloud/upload', methods=['POST'])
def upload_to_cloud():
    """Upload mockups to cloud storage"""
    data = request.json

    provider_type = data.get('provider')  # 's3' or 'gcs'
    bucket_name = data.get('bucket')
    files = data.get('files', [])

    if not provider_type or not bucket_name:
        return jsonify({'error': 'Provider and bucket required'}), 400

    # Initialize cloud provider
    try:
        if provider_type == 's3':
            provider = create_s3_storage(
                bucket_name,
                aws_access_key_id=data.get('access_key'),
                aws_secret_access_key=data.get('secret_key'),
                region=data.get('region', 'us-east-1')
            )
            cloud_manager.add_provider('s3', provider)

        elif provider_type == 'gcs':
            provider = create_gcs_storage(
                bucket_name,
                credentials_path=data.get('credentials_path')
            )
            cloud_manager.add_provider('gcs', provider)
        else:
            return jsonify({'error': 'Invalid provider'}), 400

        # Upload files
        results = {}
        for filename in files:
            local_path = Path('mockup_output') / filename
            if local_path.exists():
                remote_path = f"mockups/{filename}"
                success = provider.upload_file(local_path, remote_path)
                results[filename] = {
                    'success': success,
                    'url': provider.get_public_url(remote_path) if success else None
                }

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    settings_file = Path('config/settings.json')

    if request.method == 'POST':
        data = request.json
        settings_file.parent.mkdir(exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    else:
        if settings_file.exists():
            with open(settings_file) as f:
                data = json.load(f)
        else:
            data = {}
        return jsonify(data)


@app.route('/api/templates/detect', methods=['POST'])
def detect_template_area():
    """Auto-detect design area on a template"""
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'Filename required'}), 400

    template_path = Path('uploads/templates') / filename

    if not template_path.exists():
        return jsonify({'error': 'Template not found'}), 404

    try:
        from PIL import Image
        from mockup_generator.auto_detect import TemplateDetector

        template_img = Image.open(template_path)
        detector = TemplateDetector()

        # Detect area
        area = detector.detect_design_area(template_img)

        if area:
            return jsonify({
                'success': True,
                'area': area,
                'x': area[0],
                'y': area[1],
                'width': area[2],
                'height': area[3]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not detect design area'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
