from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from image_metadata_extractor.metadata_extractor import (
    camel_to_standard,
    format_camera_settings,
    format_capture_date,
    format_crop_info,
    format_image_metadata,
    format_post_processing,
    format_settings,
    format_tech_details,
    get_exif,
    get_xmp_metadata,
    print_metadata,
    save_metadata,
)


@pytest.fixture
def sample_exif_data():
    return {
        "Make": "Canon",
        "Model": "EOS 200D",
        "LensModel": "EF85mm f/1.8 USM",
        "FNumber": 2.8,
        "ExposureTime": 1 / 30,
        "ISOSpeedRatings": 400,
        "FocalLength": 85.0,
        "ExposureProgram": 1,
        "WhiteBalance": 0,
        "DateTimeOriginal": "2024:07:30 22:12:59",
    }


@pytest.fixture
def sample_xmp_data():
    return {
        "CreatorTool": "Adobe Lightroom 7.4.1 (Windows)",
        "CropLeft": "0.3333",
        "Exposure": "+0.28",
        "Contrast": "+5",
        "Highlights": "-81",
        "Shadows": "+54",
        "Whites": "-3",
        "Blacks": "-12",
        "Texture": "+55",
        "Clarity2012": "+42",
        "Vibrance": "+15",
        "Saturation": "-3",
        "ParametricShadowSplit": "25",
        "ParametricMidtoneSplit": "50",
        "ParametricHighlightSplit": "75",
        "Sharpness": "40",
        "ColorNoiseReduction": "25",
        "ColorGradeBlending": "50",
        "DefringePurpleHueLo": "30",
        "DefringePurpleHueHi": "70",
        "DefringeGreenHueLo": "40",
        "DefringeGreenHueHi": "60",
        "PerspectiveScale": "100",
        "ToneCurveName2012": "Linear",
    }


def test_print_metadata(capsys, sample_exif_data, sample_xmp_data):
    with patch(
        "image_metadata_extractor.metadata_extractor.get_exif",
        return_value=sample_exif_data,
    ), patch(
        "image_metadata_extractor.metadata_extractor.get_xmp_metadata",
        return_value=sample_xmp_data,
    ):
        print_metadata(Path("test.jpg"))
        captured = capsys.readouterr()
        assert "Camera: Canon EOS 200D" in captured.out
        assert "Edited in Adobe Lightroom 7.4.1 (Windows)" in captured.out


def test_save_metadata(sample_exif_data, sample_xmp_data):
    with patch(
        "image_metadata_extractor.metadata_extractor.get_exif",
        return_value=sample_exif_data,
    ), patch(
        "image_metadata_extractor.metadata_extractor.get_xmp_metadata",
        return_value=sample_xmp_data,
    ), patch(
        "builtins.open", mock_open()
    ) as mock_file:
        output_path = save_metadata(Path("test.jpg"))
        assert output_path.endswith("test.jpg.txt")
        mock_file.assert_called_once_with(output_path, "w")


def test_get_exif():
    with patch("PIL.Image.open") as mock_open:
        mock_image = mock_open.return_value.__enter__.return_value
        mock_image._getexif.return_value = {
            271: "Canon",
            272: "EOS 200D",
        }  # Corrected the tag numbers
        exif_data = get_exif(Path("test.jpg"))
        assert exif_data == {"Make": "Canon", "Model": "EOS 200D"}


def test_get_xmp_metadata():
    with patch("PIL.Image.open") as mock_open:
        mock_image = mock_open.return_value.__enter__.return_value
        mock_image.applist = [
            (
                "APP1",
                b"http://ns.adobe.com/xap/1.0/"
                b'<x:xmpmeta xmlns:x="http://ns.adobe.com/xap/1.0/" '
                b'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                b"<rdf:RDF>"
                b'<rdf:Description rdf:about="" '
                b'xmlns:xmp="http://ns.adobe.com/xap/1.0/" '
                b'xmp:CreatorTool="Adobe Lightroom"/>'
                b"</rdf:RDF>"
                b"</x:xmpmeta>",
            )
        ]
        xmp_data = get_xmp_metadata(Path("test.jpg"))
        assert xmp_data == {"CreatorTool": "Adobe Lightroom", "about": ""}


def test_camel_to_standard():
    assert camel_to_standard("camelCaseString") == "Camel Case String"
    assert camel_to_standard("PascalCaseString") == "Pascal Case String"


def test_format_image_metadata(sample_exif_data, sample_xmp_data):
    formatted = format_image_metadata(sample_xmp_data, sample_exif_data)
    assert "Camera: Canon EOS 200D" in formatted
    assert "Aperture: f/2.8" in formatted
    assert "Edited in Adobe Lightroom 7.4.1 (Windows)" in formatted


def test_format_camera_settings(sample_exif_data, sample_xmp_data):
    formatted = format_camera_settings(sample_xmp_data, sample_exif_data)
    assert "Camera: Canon EOS 200D" in formatted
    assert "Lens: EF85mm f/1.8 USM" in formatted


def test_format_settings(sample_exif_data, sample_xmp_data):
    formatted = format_settings(sample_xmp_data, sample_exif_data)
    assert "Aperture: f/2.8" in formatted
    assert "Shutter Speed: 1/30 sec" in formatted
    assert "ISO: 400" in formatted
    assert "Focal Length: 85.0 mm" in formatted


def test_format_tech_details(sample_exif_data, sample_xmp_data):
    formatted = format_tech_details(sample_xmp_data, sample_exif_data)
    assert "Shot in Manual mode" in formatted
    assert "White Balance: Auto" in formatted


def test_format_crop_info(sample_exif_data, sample_xmp_data):
    formatted = format_crop_info(sample_xmp_data, sample_exif_data)
    assert "Left: 33.33% cropped" in formatted


def test_format_post_processing(sample_exif_data, sample_xmp_data):
    formatted = format_post_processing(sample_xmp_data, sample_exif_data)
    print(formatted)  # Add this line to see the actual output
    assert "Edited in Adobe Lightroom 7.4.1 (Windows)" in formatted
    assert "Shadows: +54" in formatted
    assert "Contrast: +5" in formatted
    assert "Texture: +55" in formatted
    assert "Clarity: +42" in formatted
    assert "Vibrance: +15" in formatted
    assert "Perspective Scale: 100" not in formatted


def test_format_capture_date(sample_exif_data, sample_xmp_data):
    formatted = format_capture_date(sample_xmp_data, sample_exif_data)
    assert "Captured on 2024-07-30 at 22:12:59" in formatted
