import os
import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from gallery.models import ImageGallery

class Command(BaseCommand):
    help = 'Uploads local ImageGallery images to S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-local',
            action='store_true',
            help='Delete local files after successful upload',
        )

    def handle(self, *args, **options):
        if not settings.AWS_ACCESS_KEY_ID:
            self.stdout.write(self.style.ERROR('AWS credentials not found in settings.'))
            return

        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.client('s3', endpoint_url=settings.AWS_S3_ENDPOINT_URL)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        media_root = settings.MEDIA_ROOT

        self.stdout.write(f"Using bucket: {bucket_name}")
        self.stdout.write(f"Media root: {media_root}")

        # Process ImageGallery
        images = ImageGallery.objects.all()
        count = images.count()
        self.stdout.write(f"Found {count} images in ImageGallery")

        for i, item in enumerate(images, 1):
            if not item.image:
                continue
            
            # Ensure relative path doesn't start with /
            relative_path = item.image.name.lstrip('/')
            file_path = os.path.join(media_root, relative_path)
            s3_key = relative_path # standard django S3 storage uses the name as key

            self.stdout.write(f"[{i}/{count}] Processing {s3_key}...")

            # Check if file exists locally
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"File not found locally: {file_path}"))
                continue

            try:
                content_type = 'application/octet-stream'
                # Simple guess for content type based on extension
                if s3_key.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif s3_key.lower().endswith('.png'):
                    content_type = 'image/png'
                elif s3_key.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif s3_key.lower().endswith('.webp'):
                    content_type = 'image/webp'

                with open(file_path, 'rb') as f:
                    s3.upload_fileobj(
                        f, 
                        bucket_name, 
                        s3_key, 
                        ExtraArgs={
                            'ACL': settings.AWS_DEFAULT_ACL or 'public-read',
                            'ContentType': content_type,
                            'CacheControl': 'max-age=86400',
                        }
                    )
                
                self.stdout.write(self.style.SUCCESS(f"Uploaded {s3_key}"))

                if options['delete_local']:
                    os.remove(file_path)
                    self.stdout.write(f"Deleted local file: {file_path}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to upload {s3_key}: {e}"))

        self.stdout.write(self.style.SUCCESS('Done'))

