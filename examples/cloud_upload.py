"""
Example: Generate mockups and upload to cloud storage
Supports AWS S3 and Google Cloud Storage
"""

from mockup_generator import MockupGenerator
from mockup_generator.cloud_storage import CloudStorageManager, create_s3_storage
from pathlib import Path

# Generate mockups first
generator = MockupGenerator(
    design_folder="designs",
    template_folder="templates",
    output_folder="mockup_output",
    template_placements={
        "tshirt.png": (150, 200, 300, 300),
    }
)

print("Generating mockups...")
results = generator.generate_mockups(export_formats=["png", "jpg"])

# Upload to AWS S3
print("\nUploading to AWS S3...")

# Create cloud storage manager
cloud_manager = CloudStorageManager()

# Configure S3 storage
# Note: This uses your AWS credentials from ~/.aws/credentials or environment variables
s3_storage = create_s3_storage(
    bucket_name="my-mockups-bucket",
    region="us-east-1"
)

cloud_manager.add_provider('s3', s3_storage)

# Upload all mockups
upload_results = cloud_manager.upload_mockups(
    local_folder=Path("mockup_output"),
    provider_name='s3',
    remote_folder='mockups',
    file_pattern='*.png'
)

# Print results
successful = sum(1 for success in upload_results.values() if success)
print(f"\nUploaded {successful}/{len(upload_results)} files to S3")

# Get public URLs
for filename, success in upload_results.items():
    if success:
        url = s3_storage.get_public_url(f"mockups/{filename}")
        print(f"  {filename}: {url}")

print("\nDone! Your mockups are now in the cloud ☁️")
