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

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager
- Poppler (for PDF processing)

### Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Poppler** (required for PDF processing):
   ```bash
   brew install poppler
   ```

3. **Clone and setup the project**:
   ```bash
   mkdir label-sheet
   cd label-sheet
   
   # Initialize project
   uv init
   
   # Add dependencies
   uv add pdf2image pillow reportlab typer rich pyyaml
   ```

4. **Copy the source files** into your project:
   ```
   label-sheet/
   ├── core/
   │   ├── __init__.py
   │   ├── input_handler.py
   │   ├── processor.py
   │   ├── layout.py
   │   └── config.py
   └── cli.py
   ```

5. **Create `core/__init__.py`**:
   ```python
   # Empty file to make core a package
   ```

## Quick Start

### Basic Usage

```bash
# Use a preset with your input file
uv run python cli.py input.pdf --preset shipping-label-with-notes

# Files in ~/Downloads/ can be referenced by name only
uv run python cli.py my-label.pdf --preset label-only

# Custom output location
uv run python cli.py input.pdf --preset label-only -o custom-output.pdf
```

### Manual Quadrant Configuration

```bash
# Specify individual quadrants
uv run python cli.py \
  --q1 label.pdf:last:0 \
  --q2 label.pdf:last:0 \
  --q3 notes.pdf:second-last:-90

# Mix images and PDFs
uv run python cli.py \
  --q1 shipping-label.jpg \
  --q3 notes.pdf:1:90
```

### Preset with Overrides

```bash
# Use preset but override one quadrant
uv run python cli.py input.pdf \
  --preset label-only \
  --q3 additional-notes.pdf:1:-90
```

## Command Reference

### `generate` (default command)

Generate a label sheet PDF.

```bash
uv run python cli.py [INPUT_FILE] [OPTIONS]
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
uv run python cli.py presets
```

## Built-in Presets

### `shipping-label-with-notes`
UPS label in Q1 and Q2, notes in Q3 (rotated -90°)

**Use case:** Most common shipping workflow

```bash
uv run python cli.py input.pdf --preset shipping-label-with-notes
```

**Quadrants:**
- Q1: Last page (label)
- Q2: Last page (label, duplicate)
- Q3: Second-to-last page (notes, rotated -90°)

### `label-only`
Just the shipping label in Q1 and Q2

**Use case:** Print labels without notes

```bash
uv run python cli.py input.pdf --preset label-only
```

**Quadrants:**
- Q1: Last page (label)
- Q2: Last page (label, duplicate)

### `notes-q4`
Notes in bottom-right quadrant

**Use case:** Print notes to an unused quadrant

```bash
uv run python cli.py input.pdf --preset notes-q4
```

**Quadrants:**
- Q4: Second-to-last page (notes)

### `notes-q3`
Notes in bottom-left quadrant, rotated -90°

**Use case:** Print rotated notes to Q3

```bash
uv run python cli.py input.pdf --preset notes-q3
```

**Quadrants:**
- Q3: Second-to-last page (notes, rotated -90°)

## Examples

### Example 1: Standard Shipping Workflow
```bash
# Your PDF has a label (last page) and notes (second-to-last page)
uv run python cli.py shipping-123.pdf --preset shipping-label-with-notes
```

### Example 2: Only Print Labels
```bash
# Only need the label, not the notes
uv run python cli.py label.pdf --preset label-only
```

### Example 3: Custom Layout
```bash
# Different files for different quadrants
uv run python cli.py \
  --q1 label.jpg \
  --q2 label.jpg \
  --q4 instructions.pdf:1:0 \
  -o custom-sheet.pdf
```

### Example 4: Preset with Override
```bash
# Use preset but add custom content to Q4
uv run python cli.py input.pdf \
  --preset label-only \
  --q4 extra-info.pdf:1:0
```

### Example 5: Rotate Content
```bash
# Rotate label 180 degrees
uv run python cli.py \
  --q1 label.pdf:last:180 \
  --q2 label.pdf:last:180
```

### Example 6: Work with Images
```bash
# Use image files directly
uv run python cli.py \
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
uv run python cli.py label.pdf --preset label-only
uv run python cli.py ~/Downloads/label.pdf --preset label-only
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
├── core/
│   ├── __init__.py
│   ├── input_handler.py    # PDF/image loading
│   ├── processor.py         # Image transformations
│   ├── layout.py           # Quadrant layout engine
│   └── config.py           # Configuration & presets
├── cli.py                  # CLI interface
├── pyproject.toml          # Project dependencies
└── README.md              # This file
```

### Running Tests
```bash
# Test basic functionality
uv run python cli.py test-input.pdf --preset label-only

# Test with verbose output
uv run python cli.py --help
```

### Adding New Presets
Edit `core/config.py` and add to `BUILTIN_PRESETS` dictionary.

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