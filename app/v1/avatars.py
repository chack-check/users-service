from hashlib import sha1


def generate_avatar(metadata: str, title: str) -> str:
    metadata_hash = sha1(metadata.encode()).hexdigest()
    font_color = f"#{metadata_hash[:6]}"
    background = f"{font_color}55"
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100" height="100" viewBox="0 0 100 100" fill="none">'  # noqa: E501
        '<style>.title {font: 500 30px sans-serif;}</style>'
        f'<rect width="100px" height="100px" fill="{background}"></rect>'
        f'<text class="title" fill="{font_color}" x="50%" y="50%" dominant-baseline="middle" text-anchor="middle">{title}</text>'  # noqa: E501
        '</svg>'
    )
    return svg
