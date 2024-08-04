# Image Metadata Extractor

This project extracts and formats metadata from images, including EXIF and XMP data. It provides detailed information about camera settings, post-processing adjustments, and other relevant metadata.

## Features

- Extract EXIF and XMP metadata from images
- Format metadata into a human-readable format
- Save formatted metadata to text files
- Support for various image formats
- Detailed extraction of Lightroom-specific editing information

## Supported Image Formats

This tool supports a wide range of image formats, including but not limited to:

- JPEG (.jpg, .jpeg)
- TIFF (.tif, .tiff)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- GIF (.gif)

Note: While the tool can read these formats, the amount and type of metadata available may vary depending on the image format and how it was created or processed. JPEG and TIFF files typically contain the most comprehensive metadata.

## Requirements

- Python 3.7+
- Pillow library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/danielpodrazka/image-metadata-extractor.git
cd image-metadata-extractor
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
## Usage

1. Place your images in the `data/instagram` directory.

2. Run the main script:
```bash
python -m image_metadata_extractor.metadata_extractor
```
3. The formatted metadata for each image will be saved in the `data/output` directory as text files.

## File Structure

* `image_metadata_extractor/`: Main package directory
    * `__init__.py`: Package initialization file
* `constants.py`: Contains constant values and configurations
    * `metadata_extractor.py`: Main script for extracting and formatting metadata
* `tests/`: Directory containing test files
    * `test_main.py`: Test suite for the metadata extractor
* `data/`: Data directory
    * `img/`: Directory for input images
    * `output/`: Directory for output metadata text files
* `README.md`: This file, containing project information and usage instructions
* `requirements.txt`: List of Python dependencies
* `setup.py`: Setup script for packaging and distribution

## Metadata Extraction

The tool extracts two types of metadata:

1. EXIF (Exchangeable Image File Format) data: This includes camera settings, date and time the photo was taken, and other technical details.
2. XMP (Extensible Metadata Platform) data: This often includes post-processing information, especially for images edited in Adobe software.

Note that not all images will contain both types of metadata, and the available information may vary depending on the camera, software, and processing history of the image.

### Lightroom-specific Metadata

This tool is particularly effective at extracting and presenting metadata from images edited in Adobe Lightroom. It can display detailed information about various Lightroom adjustments, including exposure, contrast, highlights, shadows, and color grading.

## Example Output

<details>
<summary>
Click here to see the example output.
</summary>

```
📸 Camera Settings Breakdown 📸
Camera: Canon EOS 200D
Lens: EF85mm f/1.8 USM
📊 Settings
Aperture: f/2.8
Shutter Speed: 1/30 sec
ISO: 400
Focal Length: 85.0 mm
🔍 Tech Details
Shot in Manual mode
White Balance: Auto
✂️ Crop Info
Left: 33.33% cropped
✨ Post-Processing
Edited in Adobe Lightroom 7.4.1 (Windows)
Exposure: +0.28
Contrast: +5
Highlights: -81
Shadows: +54
Whites: -3
Blacks: -12
Texture: +55
Clarity: +42
Vibrance: +15
Saturation: -3
Parametric Shadow Split: 25
Parametric Midtone Split: 50
Parametric Highlight Split: 75
Sharpness: 40
Color Noise Reduction: 25
Color Grade Blending: 50
Defringe Purple Hue Lo: 30
Defringe Purple Hue Hi: 70
Defringe Green Hue Lo: 40
Defringe Green Hue Hi: 60
Perspective Scale: 100
Tone Curve Name: Linear
📅 Capture Date
Captured on 2024-07-30 at 22:12:59
```

</details>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.