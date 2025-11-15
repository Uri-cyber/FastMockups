#!/usr/bin/env python3
"""
Advanced mockup generation script with all features enabled
Uses configuration file and supports all advanced features
"""

from mockup_generator import MockupGenerator
from mockup_generator.config import Config
from mockup_generator.cloud_storage import CloudStorageManager, create_s3_storage, create_gcs_storage
from pathlib import Path
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="FastMockups - Advanced Bulk Product Mockup Generator"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--designs",
        type=str,
        help="Override designs folder path"
    )
    parser.add_argument(
        "--templates",
        type=str,
        help="Override templates folder path"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Override output folder path"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        help="Export formats (png, jpg, webp, pdf)"
    )
    parser.add_argument(
        "--no-shadow",
        action="store_true",
        help="Disable shadow effects"
    )
    parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="Disable auto-detection"
    )
    parser.add_argument(
        "--upload-cloud",
        action="store_true",
        help="Upload results to cloud storage"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Use sequential processing instead of parallel"
    )

    args = parser.parse_args()

    # Load configuration
    print("Loading configuration...")
    config = Config(Path(args.config))

    # Get folder paths
    folders = config.get_folders()
    design_folder = args.designs or folders.get('designs', 'designs')
    template_folder = args.templates or folders.get('templates', 'templates')
    output_folder = args.output or folders.get('output', 'mockup_output')

    # Get template placements
    placements = config.get_template_placements()

    # Auto-detection
    auto_detect = config.is_auto_detection_enabled() and not args.no_auto_detect

    print(f"\nConfiguration:")
    print(f"  Designs: {design_folder}")
    print(f"  Templates: {template_folder}")
    print(f"  Output: {output_folder}")
    print(f"  Auto-detect: {auto_detect}")
    print(f"  Template placements: {len(placements)} configured")

    # Initialize generator
    generator = MockupGenerator(
        design_folder=design_folder,
        template_folder=template_folder,
        output_folder=output_folder,
        template_placements=placements,
        auto_detect=auto_detect
    )

    # Get effects
    effects = config.get_effects() if not args.no_shadow else {}

    # Get export formats
    export_formats = args.formats or config.get_export_formats()

    # Get processing settings
    processing = config.get_processing_settings()
    parallel = processing['parallel'] and not args.sequential

    print(f"\nGeneration settings:")
    print(f"  Export formats: {', '.join(export_formats)}")
    print(f"  Effects: {list(effects.keys()) if effects else 'None'}")
    print(f"  Processing: {'Parallel' if parallel else 'Sequential'}")
    if parallel:
        print(f"  Max workers: {processing['max_workers']}")

    # Generate mockups
    print("\nStarting mockup generation...\n")

    results = generator.generate_mockups(
        effects=effects,
        export_formats=export_formats,
        parallel=parallel,
        max_workers=processing['max_workers'],
        progress_bar=processing['progress_bar']
    )

    # Print results
    stats = generator.get_stats()
    print(f"\n{'='*60}")
    print(f"Generation Complete!")
    print(f"{'='*60}")
    print(f"Total processed: {stats['processed']}/{stats['total']}")
    print(f"Success rate: {stats['processed']/stats['total']*100:.1f}%")

    if stats['failed'] > 0:
        print(f"Failed: {stats['failed']}")

    # Upload to cloud if requested
    if args.upload_cloud:
        cloud_config = config.get_cloud_storage_config()

        if cloud_config:
            print(f"\nUploading to {cloud_config['provider']}...")

            cloud_manager = CloudStorageManager()

            if cloud_config['provider'] == 's3':
                provider = create_s3_storage(
                    cloud_config['bucket_name'],
                    region=cloud_config.get('region', 'us-east-1')
                )
                cloud_manager.add_provider('s3', provider)

                upload_results = cloud_manager.upload_mockups(
                    Path(output_folder),
                    's3',
                    remote_folder='mockups'
                )

                successful = sum(1 for v in upload_results.values() if v)
                print(f"Uploaded {successful}/{len(upload_results)} files to S3")

            elif cloud_config['provider'] == 'gcs':
                provider = create_gcs_storage(
                    cloud_config['bucket_name'],
                    project_id=cloud_config.get('project_id')
                )
                cloud_manager.add_provider('gcs', provider)

                upload_results = cloud_manager.upload_mockups(
                    Path(output_folder),
                    'gcs',
                    remote_folder='mockups'
                )

                successful = sum(1 for v in upload_results.values() if v)
                print(f"Uploaded {successful}/{len(upload_results)} files to GCS")

        else:
            print("\nCloud storage not configured. Skipping upload.")

    print(f"\nMockups saved to: {output_folder}")
    print("\nDone! ✨")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
