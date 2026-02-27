from urllib.parse import urlparse, parse_qs

from django import template

register = template.Library()


def _youtube_embed(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    base_params = "?rel=0&modestbranding=1&playsinline=1"
    if "youtube.com" in host:
        if parsed.path.startswith("/embed/"):
            return url if "youtube-nocookie" in host else url.replace("https://www.youtube.com", "https://www.youtube-nocookie.com")
        if parsed.path.startswith("/watch"):
            query = parse_qs(parsed.query)
            video_id = query.get("v", [""])[0]
            if video_id:
                return f"https://www.youtube-nocookie.com/embed/{video_id}{base_params}"
        if parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[-1].split("/")[0]
            if video_id:
                return f"https://www.youtube-nocookie.com/embed/{video_id}{base_params}"
    if "youtu.be" in host:
        video_id = parsed.path.lstrip("/")
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}{base_params}"
    return url


@register.filter(name="to_embed_url")
def to_embed_url(url: str) -> str:
    if not url:
        return ""
    try:
        return _youtube_embed(url)
    except Exception:
        return url
