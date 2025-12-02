import os
import re
import base64
from urllib.parse import unquote
from bs4 import BeautifulSoup

def refactor_project():
    input_file = "biotensão gluteos.html"
    output_html = "index.html"
    css_dir = "css"
    js_dir = "js"
    img_dir = "assets/images"
    
    # Ensure directories exist
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    print(f"Reading {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # 1. Extract CSS
    print("Extracting CSS...")
    styles = soup.find_all("style")
    css_content = ""
    for i, style in enumerate(styles):
        if style.string:
            css_content += f"/* Extracted Style {i+1} */\n{style.string}\n\n"
        style.decompose() # Remove from HTML

    with open(os.path.join(css_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)
    
    # Add link to new CSS
    new_link = soup.new_tag("link", rel="stylesheet", href=f"{css_dir}/style.css")
    if soup.head:
        soup.head.append(new_link)
    else:
        # Create head if missing (unlikely but safe)
        head = soup.new_tag("head")
        soup.insert(0, head)
        head.append(new_link)

    # 2. Extract JS
    print("Extracting JS...")
    scripts = soup.find_all("script")
    js_content = ""
    # Filter out scripts that might be external or have src (keep them?)
    # For this task, we assume we want to extract inline scripts.
    # We will append them all to one file for simplicity, preserving order.
    
    for i, script in enumerate(scripts):
        if script.get("src"):
            continue # Skip external scripts
        
        if script.string:
            js_content += f"/* Extracted Script {i+1} */\n{script.string}\n\n"
            script.decompose()
    
    with open(os.path.join(js_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content)

    # Add script tag to new JS
    new_script = soup.new_tag("script", src=f"{js_dir}/script.js")
    if soup.body:
        soup.body.append(new_script)
    else:
        soup.append(new_script)

    # 3. Extract Images (Base64)
    print("Extracting Images...")
    images = soup.find_all("img")
    img_count = 0
    for img in images:
        src = img.get("src")
        if src and src.startswith("data:image"):
            try:
                src = unquote(src)
                # Parse base64
                header, encoded = src.split(",", 1)
                # Remove fragment if present
                if '#' in encoded:
                    encoded = encoded.split('#')[0]
                
                encoded = "".join(encoded.split())
                file_ext = "png" # Default
                if "jpeg" in header or "jpg" in header:
                    file_ext = "jpg"
                elif "gif" in header:
                    file_ext = "gif"
                elif "svg" in header:
                    file_ext = "svg"
                elif "webp" in header:
                    file_ext = "webp"
                
                img_filename = f"image_{img_count}.{file_ext}"
                img_path = os.path.join(img_dir, img_filename)
                
                # Fix padding
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += '=' * (4 - missing_padding)
                
                # Debug
                print(f"Image {img_count}: Length {len(encoded)}, Last chars: {encoded[-10:]}")

                with open(img_path, "wb") as f:
                    f.write(base64.b64decode(encoded))
                
                # Update src
                img["src"] = f"{img_dir}/{img_filename}"
                img_count += 1
            except Exception as e:
                print(f"Failed to extract image {img_count}: {e}")

    # Also check for link icons
    links = soup.find_all("link", rel="icon")
    for link in links:
        href = link.get("href")
        if href and href.startswith("data:image"):
             try:
                href = unquote(href)
                header, encoded = href.split(",", 1)
                if '#' in encoded:
                    encoded = encoded.split('#')[0]
                encoded = "".join(encoded.split())
                file_ext = "png"
                if "jpeg" in header or "jpg" in header: file_ext = "jpg"
                elif "gif" in header: file_ext = "gif"
                elif "svg" in header: file_ext = "svg"
                
                icon_filename = f"favicon.{file_ext}"
                icon_path = os.path.join(img_dir, icon_filename)
                
                # Fix padding
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += '=' * (4 - missing_padding)

                with open(icon_path, "wb") as f:
                    f.write(base64.b64decode(encoded))
                
                link["href"] = f"{img_dir}/{icon_filename}"
             except Exception as e:
                print(f"Failed to extract favicon: {e}")


    # 4. Save HTML
    print(f"Saving {output_html}...")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("Done!")

if __name__ == "__main__":
    refactor_project()
