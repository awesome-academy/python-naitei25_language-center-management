from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()

def _extract_id(url):
    u = urlparse(url)
    if u.netloc in ("youtu.be",):
        return u.path.lstrip("/")
    if "youtube" in u.netloc:
        qs = parse_qs(u.query)
        if "v" in qs: return qs["v"][0]
        # dạng /embed/<id>
        parts = u.path.split("/")
        if "embed" in parts and len(parts) > parts.index("embed")+1:
            return parts[parts.index("embed")+1]
    return url  # fallback

@register.filter
def yt_embed(url):
    vid = _extract_id(url)
    return f"https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1"
