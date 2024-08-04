import os
import pathlib
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

from PIL import Image
from PIL.ExifTags import TAGS

from image_metadata_extractor.constants import (
    DATA_DIR,
    EXPOSURE_PROGRAMS,
    IMG_DIR,
    OUTPUT_DIR,
    POST_PROCESSING_KEYS,
)


def print_metadata(image_path: pathlib.Path) -> None:
    exif = get_exif(image_path)
    xmp = get_xmp_metadata(image_path)
    print(format_image_metadata(xmp, exif))


def save_metadata(image_path: pathlib.Path) -> str:
    exif = get_exif(image_path)
    xmp = get_xmp_metadata(image_path)
    formatted_img_data = format_image_metadata(xmp, exif)
    output_path = str(OUTPUT_DIR / os.path.basename(image_path)) + ".txt"
    with open(output_path, "w") as writer:
        writer.write(formatted_img_data)
    return output_path


def get_exif(image_path: pathlib.Path) -> Optional[Dict[str, Any]]:
    try:
        with Image.open(image_path) as img:
            exif = img._getexif()
            if exif:
                return {TAGS[k]: v for k, v in exif.items() if k in TAGS}
    except Exception as e:
        print(f"Error reading EXIF data from {image_path}: {e}")
    return None


def get_xmp_metadata(image_path: pathlib.Path) -> Optional[Dict[str, str]]:
    with Image.open(image_path) as img:
        xmp_data = None
        for segment, content in img.applist:
            if segment == "APP1" and content.startswith(
                b"http://ns.adobe.com/xap/1.0/"
            ):
                xmp_data = content
                break

        if xmp_data:
            xmp_start = xmp_data.find(b"<x:xmpmeta")
            xmp_end = xmp_data.find(b"</x:xmpmeta")
            xmp_str = xmp_data[xmp_start : xmp_end + 12].decode("utf-8")

            root = ET.fromstring(xmp_str)

            metadata: Dict[str, str] = {}
            for elem in root.iter():
                if "}" in elem.tag:
                    tag = elem.tag.split("}")[1]
                    if elem.text and elem.text.strip():
                        metadata[tag] = elem.text.strip()
                for name, value in elem.attrib.items():
                    if "}" in name:
                        name = name.split("}")[1]
                    metadata[name] = value

            return metadata

    return None


def camel_to_standard(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1 \2", name).title()


def format_image_metadata(
    xmp_data: Optional[Dict[str, str]], exif_data: Optional[Dict[str, Any]]
) -> str:
    if not xmp_data and not exif_data:
        return "No metadata present"

    xmp_data = xmp_data or {}
    exif_data = exif_data or {}

    sections = {
        "📸 Camera Settings Breakdown 📸": format_camera_settings,
        "📊 Settings": format_settings,
        "🔍 Tech Details": format_tech_details,
        "✂️ Crop Info": format_crop_info,
        "✨ Post-Processing": format_post_processing,
        "📅 Capture Date": format_capture_date,
    }

    output = ""
    for section_title, format_function in sections.items():
        section_content = format_function(xmp_data, exif_data)
        if section_content:
            output += f"{section_title}\n{section_content}\n"

    return output.strip()


def format_camera_settings(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    camera = f"{exif_data.get('Make', '')} {exif_data.get('Model', '')}"
    camera = re.sub(r"\b(\w+)(\s+\1)+\b", r"\1", camera)  # Remove duplicates
    lens = exif_data.get("LensModel", "")
    return f"Camera: {camera.strip()}\nLens: {lens}".strip()


def format_settings(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    output = ""
    if "FNumber" in exif_data:
        output += f"Aperture: f/{exif_data['FNumber']}\n"
    if "ExposureTime" in exif_data:
        shutter_speed = exif_data["ExposureTime"]
        output += (
            f"Shutter Speed: 1/{int(1 / shutter_speed)} sec\n"
            if shutter_speed < 1
            else f"Shutter Speed: {shutter_speed} sec\n"
        )
    if "ISOSpeedRatings" in exif_data:
        output += f"ISO: {exif_data['ISOSpeedRatings']}\n"
    if "FocalLength" in exif_data:
        output += f"Focal Length: {exif_data['FocalLength']} mm\n"
    return output.strip()


def format_tech_details(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    output = ""
    if "ExposureProgram" in exif_data:
        output += f"Shot in {EXPOSURE_PROGRAMS.get(exif_data['ExposureProgram'], 'Unknown')} mode\n"
    if "WhiteBalance" in exif_data:
        white_balance = "Auto" if exif_data["WhiteBalance"] == 0 else "Manual"
        output += f"White Balance: {white_balance}\n"
    return output.strip()


def format_crop_info(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    output = ""
    crop_keys = ["CropLeft", "CropRight", "CropTop", "CropBottom"]
    for key in crop_keys:
        if key in xmp_data:
            value = float(xmp_data[key])
            percentage = (
                value * 100 if key in ["CropLeft", "CropTop"] else (1 - value) * 100
            )
            if abs(percentage) > 0.1:
                output += f"{key[4:]}: {percentage:.2f}% cropped\n"
    return output.strip()


def format_post_processing(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    output = ""
    if "CreatorTool" in xmp_data:
        output += f"Edited in {xmp_data['CreatorTool']}\n"

    for key in POST_PROCESSING_KEYS:
        if key in xmp_data:
            value = xmp_data[key]
            try:
                float_value = float(value)
                if key == "PerspectiveScale" and int(float_value) == 100:
                    continue
                if float_value != 0 and float_value != 0.0:
                    display_key = camel_to_standard(key.replace("2012", ""))
                    output += f"{display_key}: {value}\n"
            except ValueError:
                if value.lower() not in ["0", "false", "none", ""]:
                    display_key = camel_to_standard(key.replace("2012", ""))
                    output += f"{display_key}: {value}\n"
    return output.strip()


def format_capture_date(xmp_data: Dict[str, str], exif_data: Dict[str, Any]) -> str:
    if "DateTimeOriginal" in exif_data:
        date, time = exif_data["DateTimeOriginal"].split()
        date = date.replace(":", "-")
        return f"Captured on {date} at {time}"
    return ""


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_paths = [
        IMG_DIR / fp
        for fp in os.listdir(IMG_DIR)
        if pathlib.Path(IMG_DIR / fp).is_file()
    ]
    print(f"Found {len(img_paths)=}")
    for img_path in img_paths:
        output_path = save_metadata(img_path)
        print(f"Saved Metadata from {img_path=} in {output_path=}")
