# Label Sheet Generator

A CLI tool to generate label sheets for UPS 4-quadrant letter-size sheets. Transform your digital PDFs and images into a print-ready format that fits perfectly on peel-and-stick label sheets.

## Features

- 🎯 **Preset Workflows** - Common use cases are one command away
- 📄 **PDF & Image Support** - Works with PDF, JPG, PNG, HEIC, and more
- 🔄 **Rotation Control** - Rotate content to fit your needs
- 📐 **Smart Layout** - Automatic fitting with configurable margins
- 🎨 **Grid Lines** - Optional quadrant separators for easy cutting
- ⚙️ **Flexible** - Mix presets with manual overrides

## Installation

### Prerequisites

- Python 3.12+
- Poppler (for PDF processing)

### Install from PyPI (Recommended)

Once published, install with:

```bash
pip install label-sheet
```

### Install Poppler

**macOS:**
```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install poppler-utils
```

**Linux (Fedora):**
```bash
sudo dnf install poppler-utils
```

### Development Installation

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/him229/label-sheet.git
cd label-sheet
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Use a preset with your input file
label-sheet generate input.pdf --preset standard

# Files in ~/Downloads/ can be referenced by name only
label-sheet generate my-label.pdf --preset label-only-q1-q2

# Custom output location
label-sheet generate input.pdf --preset label-only-q1-q2 -o custom-output.pdf

# Interactive mode - prompts for input file
label-sheet generate --preset standard --interactive
```

### Manual Quadrant Configuration

```bash
# Specify individual quadrants
label-sheet generate \
  --q1 label.pdf:last:0 \
  --q2 label.pdf:last:0 \
  --q3 notes.pdf:second-last:-90

# Mix images and PDFs
label-sheet generate \
  --q1 shipping-label.jpg \
  --q3 notes.pdf:1:90
```

### Preset with Overrides

```bash
# Use preset but override one quadrant
label-sheet generate input.pdf \
  --preset label-only-q1-q2 \
  --q3 additional-notes.pdf:1:-90
```

## Command Reference

### `generate`

Generate a label sheet PDF.

```bash
label-sheet generate [INPUT_FILE] [OPTIONS]
```

#### Arguments

- `INPUT_FILE` - Input file (required when using presets). If not an absolute path, looks in `~/Downloads/`

#### Options

**Presets:**
- `--preset, -p <NAME>` - Use a predefined layout preset

**Quadrant Configuration:**
- `--q1, --quadrant-1 <SPEC>` - Top-left quadrant
- `--q2, --quadrant-2 <SPEC>` - Top-right quadrant
- `--q3, --quadrant-3 <SPEC>` - Bottom-left quadrant
- `--q4, --quadrant-4 <SPEC>` - Bottom-right quadrant

**Input Specification Format:** `file[:page[:rotation]]`
- `file` - Path to PDF or image
- `page` - `last`, `second-last`, or page number (default: `last`)
- `rotation` - Rotation in degrees, positive = counter-clockwise (default: `0`)

**Examples:**
- `label.pdf` - Last page, no rotation
- `label.pdf:1` - Page 1, no rotation
- `notes.pdf:second-last:-90` - Second-to-last page, rotated -90°
- `image.jpg:0:180` - Image rotated 180°

**Output Options:**
- `-o, --output <FILE>` - Output PDF path (default: `output.pdf`)

**Layout Options:**
- `-m, --margin <INCHES>` - Margin for each quadrant in inches (default: `0.25`)
- `--no-grid` - Don't draw grid lines between quadrants
- `--dpi <NUMBER>` - DPI for PDF to image conversion (default: `300`)

**Help:**
- `--help` - Show help message

### `presets`

List all available presets.

```bash
label-sheet presets
```

## Built-in Presets

### `standard`
UPS label (Q1, Q2) + notes (Q3 rotated -90°)

**Use case:** Most common shipping workflow

```bash
label-sheet generate input.pdf --preset standard
```

**Quadrants:**
- Q1: Last page (label)
- Q2: Last page (label, duplicate)
- Q3: Second-to-last page (notes, rotated -90°)

### `label-only-q1-q2`
Just the shipping label in Q1 and Q2

**Use case:** Print labels without notes

```bash
label-sheet generate input.pdf --preset label-only-q1-q2
```

**Quadrants:**
- Q1: Last page (label)
- Q2: Last page (label, duplicate)

### `notes-q4`
Notes in bottom-right quadrant

**Use case:** Print notes to an unused quadrant

```bash
label-sheet generate input.pdf --preset notes-q4
```

**Quadrants:**
- Q4: Second-to-last page (notes)

### `notes-q3`
Notes in bottom-left quadrant, rotated -90°

**Use case:** Print rotated notes to Q3

```bash
label-sheet generate input.pdf --preset notes-q3
```

**Quadrants:**
- Q3: Second-to-last page (notes, rotated -90°)

## Examples

### Example 1: Standard Shipping Workflow
```bash
# Your PDF has a label (last page) and notes (second-to-last page)
label-sheet generate shipping-123.pdf --preset standard
```

### Example 2: Only Print Labels
```bash
# Only need the label, not the notes
label-sheet generate label.pdf --preset label-only-q1-q2
```

### Example 3: Custom Layout
```bash
# Different files for different quadrants
label-sheet generate \
  --q1 label.jpg \
  --q2 label.jpg \
  --q4 instructions.pdf:1:0 \
  -o custom-sheet.pdf
```

### Example 4: Preset with Override
```bash
# Use preset but add custom content to Q4
label-sheet generate input.pdf \
  --preset label-only-q1-q2 \
  --q4 extra-info.pdf:1:0
```

### Example 5: Rotate Content
```bash
# Rotate label 180 degrees
label-sheet generate \
  --q1 label.pdf:last:180 \
  --q2 label.pdf:last:180
```

### Example 6: Work with Images
```bash
# Use image files directly
label-sheet generate \
  --q1 photo-label.jpg \
  --q3 barcode.png
```

## File Path Resolution

The CLI automatically looks for files in `~/Downloads/` if:
1. The path is not absolute
2. The file doesn't exist in the current directory

**Example:**
```bash
# These are equivalent if the file is in Downloads
label-sheet generate label.pdf --preset label-only-q1-q2
label-sheet generate ~/Downloads/label.pdf --preset label-only-q1-q2
```

## Quadrant Layout

```
┌─────────────┬─────────────┐
│             │             │
│     Q1      │     Q2      │
│  (Top-Left) │ (Top-Right) │
│             │             │
├─────────────┼─────────────┤
│             │             │
│     Q3      │     Q4      │
│(Bottom-Left)│(Bottom-Right│
│             │             │
└─────────────┴─────────────┘

Letter size: 8.5" × 11"
Each quadrant: 4.25" × 5.5"
```

## Configuration (Advanced)

Create custom presets in `~/.label-sheet/presets.yaml`:

```yaml
my-custom-preset:
  description: "My custom layout"
  quadrants:
    1:
      source: "{input}"
      page: "last"
      rotation: 0
    3:
      source: "{input}"
      page: "1"
      rotation: 90
```

Set defaults in `~/.label-sheet/config.yaml`:

```yaml
defaults:
  margin: 0.25
  dpi: 300
  output: output.pdf
  show_grid: true
```

## Supported File Formats

**Input:**
- PDF (`.pdf`)
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- HEIC/HEIF (`.heic`, `.heif`)
- BMP (`.bmp`)
- GIF (`.gif`)

**Output:**
- PDF only

## Troubleshooting

### "File not found" error
- Check that the file exists in `~/Downloads/` or provide an absolute path
- Verify the filename is correct (case-sensitive on Mac)

### "PDF has no pages" error
- Ensure the PDF is not corrupted
- Try opening the PDF in Preview to verify it's valid

### "Page number X out of range" error
- Check how many pages are in your PDF
- Use `last` or `second-last` instead of specific page numbers

### Low-quality output
- Increase DPI: `--dpi 600` (default is 300)
- Note: Higher DPI increases processing time

### Content is cut off
- Increase margins: `--margin 0.5` (default is 0.25)
- Check that your content fits in a quadrant (4.25" × 5.5")

## Development

### Project Structure
```
label-sheet/
├── cli.py                  # CLI interface
├── config.py               # Configuration & presets
├── core.py                 # PDF/image loading
├── layout.py               # Quadrant layout engine
├── processor.py            # Image transformations
├── pyproject.toml          # Project dependencies
└── README.md              # This file
```

### Running Tests
```bash
# Test basic functionality
label-sheet generate test-input.pdf --preset label-only-q1-q2

# Test with verbose output
label-sheet --help
label-sheet generate --help
```

### Adding New Presets
Edit `config.py` and add to `BUILTIN_PRESETS` dictionary.

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Roadmap

- [ ] Web UI interface
- [ ] Batch processing multiple files
- [ ] Preview mode before generating
- [ ] Label sheet inventory tracking
- [ ] More built-in presets
- [ ] PDF metadata preservation

## Support

For issues, questions, or feature requests, please open an issue on GitHub.