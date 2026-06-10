import os
import re
from pathlib import Path


def extract_section_content(html_content, section_name):
    pattern = rf"<DT><H3[^>]*>{re.escape(section_name)}</H3>"
    match = re.search(pattern, html_content)
    if not match:
        raise ValueError(f"Section '{section_name}' not found")
    start_pos = match.start()

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


def extract_month_sections(github_section):
    month_pattern = r"<DT><H3[^>]*>(20\d{4})</H3>\s*<DL><p>(.*?)</DL><p>"
    matches = re.findall(month_pattern, github_section, re.DOTALL)
    return {month: content for month, content in matches}


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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)


def main():
    script_dir = Path(__file__).parent
    github_favorites_file = script_dir / "github_favorites.html"

    if not github_favorites_file.exists():
        print(f"Error: {github_favorites_file} not found")
        return

    with open(github_favorites_file, "r", encoding="utf-8") as f:
        content = f.read()

    github_section = extract_section_content(content, "Github")
    months = extract_month_sections(github_section)

    if not months:
        print("No months found in Github section")
        return

    print(f"Found months: {sorted(months.keys())}")

    for month, month_content in sorted(months.items()):
        month_dir = script_dir / month
        output_file = month_dir / "bookmarks.html"

        if output_file.exists():
            print(f"Skipping {month} (already extracted)")
            continue

        month_header = f'<DT><H3 ADD_DATE="1773647783" LAST_MODIFIED="0">{month}</H3>\n            <DL><p>'
        month_full_content = f'            <DT><H3 ADD_DATE="1773647783" LAST_MODIFIED="0">{month}</H3>\n            <DL><p>\n                {month_content}\n            </DL><p>'

        create_bookmark_file(month_full_content, output_file)
        print(f"Created: {output_file}")


if __name__ == "__main__":
    main()
