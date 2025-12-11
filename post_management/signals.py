import os
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from .models import NewsPost

THUMBNAIL_SIZE = (400, 400)
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif")


@receiver(post_save, sender=NewsPost)
def run_thumbnail_logic_on_new_post(sender, instance, created, **kwargs):
    """
    Run thumbnail generation ONLY when a new NewsPost is created.
    """

    if not created:
        return   # <-- UPDATE par run nahi hoga, sirf CREATE par

    if not instance.post_image:
        return   # No image uploaded, skip

    original_path = instance.post_image.path
    root = os.path.dirname(original_path)
    filename = os.path.basename(original_path)

    # Thumbnail folder
    thumb_dir = os.path.join(root, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    thumb_path = os.path.join(thumb_dir, filename)

    # Skip if thumb exists
    if os.path.exists(thumb_path):
        return

    try:
        with Image.open(original_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumb_path, "JPEG", quality=85)

            print("Thumbnail Created:", thumb_path)

    except Exception as e:
        print("Thumbnail Error:", e)
