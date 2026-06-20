from pathlib import Path
from PIL import Image
import hashlib
import os
import shutil
from app import create_app

root = Path.cwd().resolve()
logos_dir = root / 'uploads' / 'logos'
target = logos_dir / 'logo_6.png'

all_images = []
for p in logos_dir.iterdir():
    if p.is_file() and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}:
        all_images.append(p)

all_images = sorted(all_images, key=lambda x: x.stat().st_mtime, reverse=True)
source = all_images[0] if all_images else None

print('ROOT=' + str(root))
print('LOGOS_DIR=' + str(logos_dir))
print('TARGET=' + str(target))
print('TARGET_EXISTS=' + str(target.exists()))
if target.exists():
    with Image.open(target) as img:
        print('BEFORE_SIZE=' + str(target.stat().st_size))
        print('BEFORE_DIM=' + str(img.size))
        print('BEFORE_FORMAT=' + str(img.format))
        print('BEFORE_SHA256=' + hashlib.sha256(target.read_bytes()).hexdigest())
else:
    print('BEFORE_SIZE=N/A')
    print('BEFORE_DIM=N/A')

print('SOURCE=' + str(source))
if source is not None:
    print('SOURCE_SIZE=' + str(source.stat().st_size))
    with Image.open(source) as img:
        print('SOURCE_DIM=' + str(img.size))
        print('SOURCE_FORMAT=' + str(img.format))
        print('SOURCE_SHA256=' + hashlib.sha256(source.read_bytes()).hexdigest())

if source is not None and source != target:
    shutil.copy2(source, target)
    print('COPIED=YES')
else:
    print('COPIED=NO')

print('AFTER_TARGET_EXISTS=' + str(target.exists()))
if target.exists():
    with Image.open(target) as img:
        print('AFTER_SIZE=' + str(target.stat().st_size))
        print('AFTER_DIM=' + str(img.size))
        print('AFTER_FORMAT=' + str(img.format))
        print('AFTER_SHA256=' + hashlib.sha256(target.read_bytes()).hexdigest())

app = create_app()
client = app.test_client()
response = client.get('/uploads/logos/logo_6.png')
print('ROUTE_STATUS=' + str(response.status_code))
print('ROUTE_CONTENT_TYPE=' + response.content_type)
print('ROUTE_CONTENT_LENGTH=' + str(response.content_length))
print('ROUTE_CACHE_CONTROL=' + response.headers.get('Cache-Control', ''))
print('ROUTE_SHA256=' + hashlib.sha256(response.data).hexdigest())
