import shutil
from pathlib import Path


def on_post_build(config):
    site_dir = Path(config["site_dir"])
    src = site_dir / "sitemap.xml"
    dst = site_dir / "sitemap_index.xml"
    if src.exists():
        shutil.copy2(src, dst)
