import os
import re
from pathlib import Path


def get_latest_bookmark_file(parent_dir):
    html_files = list(Path(parent_dir).glob("*.html"))
    if not html_files:
        raise FileNotFoundError("No HTML bookmark files found")
    return max(html_files, key=lambda f: f.stat().st_ctime)


def find_section_start(content, section_name):
    pattern = rf"<DT><H3[^>]*>{re.escape(section_name)}</H3>"
    match = re.search(pattern, content)
    if not match:
        raise ValueError(f"Section '{section_name}' not found")
    return match.start()


def extract_section_content(html_content, section_name):
    start_pos = find_section_start(html_content, section_name)

    dl_tag_pattern = r"<DL><p>"
    dl_close_pattern = r"</DL><p>"

    search_from = html_content.find("<DL><p>", start_pos)
    if search_from == -1:
        raise ValueError(f"Could not find section content for '{section_name}'")

    dl_count = 0
    pos = search_from
    while pos < len(html_content):
        dl_open_match = re.match(dl_tag_pattern, html_content[pos:])
        dl_close_match = re.match(dl_close_pattern, html_content[pos:])

        if dl_open_match and (
            dl_close_match is None or dl_open_match.start() <= dl_close_match.start()
        ):
            dl_count += 1
            pos += dl_open_match.end()
        elif dl_close_match:
            dl_count -= 1
            if dl_count == 0:
                end_pos = pos + dl_close_match.end()
                return html_content[start_pos:end_pos]
            pos += dl_close_match.end()
        else:
            pos += 1

    raise ValueError(f"Could not find end of section '{section_name}'")


def create_bookmark_file(section_content, output_path):
    template = f"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
{section_content}
</DL><p>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)


def main():
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent

    latest_file = get_latest_bookmark_file(parent_dir)
    print(f"Reading from: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()

    section_content = extract_section_content(content, "项目收藏")

    output_file = script_dir / "github_favorites.html"
    create_bookmark_file(section_content, output_file)
    print(f"Created: {output_file}")


if __name__ == "__main__":
    main()
