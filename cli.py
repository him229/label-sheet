"""
Command-line interface for label-sheet.
"""
import typer
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from core import InputHandler
from layout import LayoutEngine, QuadrantConfig
from config import ConfigManager

app = typer.Typer(
    name="label-sheet",
    help="Generate label sheets for UPS 4-quadrant letter-size sheets.\n\n"
         "This tool creates letter-size PDFs divided into 4 quadrants:\n"
         "  • Q1: Top-left\n"
         "  • Q2: Top-right\n"
         "  • Q3: Bottom-left\n"
         "  • Q4: Bottom-right\n\n"
         "You can use presets or manually configure each quadrant with PDF pages or images.\n\n"
         "Commands:\n"
         "  • generate: Create a label sheet PDF\n"
         "  • presets:  List available presets\n\n"
         "Example: label-sheet generate input.pdf --preset shipping-label-with-notes",
    add_completion=False,
)
console = Console()
config_manager = ConfigManager()

# Default Downloads folder for Mac
DEFAULT_DOWNLOADS = Path.home() / "Downloads"


def parse_input_spec(spec: str) -> tuple[str, str, int]:
    """
    Parse input specification in format: file[:page[:rotation]]
    
    Returns:
        Tuple of (file, page, rotation)
    """
    parts = spec.split(":")
    file = parts[0]
    page = parts[1] if len(parts) > 1 else "last"
    rotation = int(parts[2]) if len(parts) > 2 else 0
    
    return file, page, rotation


def resolve_file_path(file: str) -> Path:
    """
    Resolve file path, checking Downloads folder if not absolute.
    """
    # Expand user home directory and normalize path
    file = os.path.expanduser(file.strip())
    path = Path(file)
    
    # If absolute path and exists, use it
    downloads_fallback_path = None
    if path.is_absolute():
        if path.exists():
            return path.resolve()  # Resolve to absolute canonical path
        # If absolute path doesn't exist, still check Downloads as fallback
        # (in case user typed absolute path but file is actually in Downloads)
        filename = path.name
        downloads_fallback_path = DEFAULT_DOWNLOADS / filename
        if downloads_fallback_path.exists():
            return downloads_fallback_path.resolve()
    
    # Check in Downloads folder
    downloads_path = DEFAULT_DOWNLOADS / file
    if downloads_path.exists():
        return downloads_path.resolve()
    
    # Try as relative path from current directory
    if path.exists():
        return path.resolve()
    
    # File not found - provide helpful error
    checked_paths = []
    if path.is_absolute():
        checked_paths.append(path.resolve())
        # Also checked Downloads with just filename
        if downloads_fallback_path:
            checked_paths.append(downloads_fallback_path.resolve())
    else:
        checked_paths.append(path.resolve() if path.exists() else path.absolute())
        checked_paths.append(downloads_path.resolve())
    
    raise FileNotFoundError(
        f"File not found: {file}\n"
        f"Checked locations:\n"
        + "\n".join(f"  - {p}" for p in checked_paths)
    )


@app.command()
def generate(
    # Input file for preset
    input_file: Optional[str] = typer.Argument(
        None,
        help="Input file (PDF or image). If not absolute, looks in ~/Downloads/\n"
             "Examples: 'input.pdf', '/path/to/file.pdf', 'label.jpg'"
    ),
    
    # Preset
    preset: Optional[str] = typer.Option(
        None,
        "--preset", "-p",
        help="Use a predefined layout preset. Run 'label-sheet presets' to see all options.\n"
             "Examples: 'shipping-label-with-notes', 'label-only', 'notes-q3'\n"
             "Usage: label-sheet generate input.pdf --preset <name>"
    ),
    
    # Quadrant overrides
    q1: Optional[str] = typer.Option(
        None,
        "--q1", "--quadrant-1",
        help="Top-left quadrant specification: file[:page[:rotation]]\n"
             "Format: filename[:page[:rotation_degrees]]\n"
             "Examples: 'label.pdf', 'label.pdf:last', 'label.pdf:-1:0', 'notes.pdf:2:-90'"
    ),
    q2: Optional[str] = typer.Option(
        None,
        "--q2", "--quadrant-2",
        help="Top-right quadrant specification: file[:page[:rotation]]\n"
             "Format: filename[:page[:rotation_degrees]]\n"
             "Examples: 'label.pdf', 'label.pdf:last', 'label.pdf:-1:0', 'notes.pdf:2:-90'"
    ),
    q3: Optional[str] = typer.Option(
        None,
        "--q3", "--quadrant-3",
        help="Bottom-left quadrant specification: file[:page[:rotation]]\n"
             "Format: filename[:page[:rotation_degrees]]\n"
             "Examples: 'label.pdf', 'label.pdf:last', 'label.pdf:-1:0', 'notes.pdf:2:-90'"
    ),
    q4: Optional[str] = typer.Option(
        None,
        "--q4", "--quadrant-4",
        help="Bottom-right quadrant specification: file[:page[:rotation]]\n"
             "Format: filename[:page[:rotation_degrees]]\n"
             "Examples: 'label.pdf', 'label.pdf:last', 'label.pdf:-1:0', 'notes.pdf:2:-90'"
    ),
    
    # Output options
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output PDF file path. If not specified, uses '<input>_output.pdf'\n"
             "Examples: 'output.pdf', '/path/to/output.pdf', 'my_labels.pdf'"
    ),
    
    # Layout options
    margin: float = typer.Option(
        0.25,
        "--margin", "-m",
        help="Margin for each quadrant in inches (default: 0.25)\n"
             "Examples: 0.25, 0.5, 0.1"
    ),
    no_grid: bool = typer.Option(
        False,
        "--no-grid",
        help="Don't draw grid lines between quadrants (default: grid is shown)"
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        help="DPI for PDF to image conversion (default: 300)\n"
             "Higher values = better quality but larger file size\n"
             "Examples: 150, 300, 600"
    ),
    
    # Interactive mode
    interactive: bool = typer.Option(
        False,
        "--interactive", "-i",
        help="Enable interactive mode to prompt for input file location when using presets.\n"
             "Usage: label-sheet generate --preset <name> --interactive"
    ),
):
    """
    Generate a label sheet PDF with specified quadrant configurations.
    
    PAGE SPECIFICATION FORMAT:
    ---------------------------
    When specifying quadrants, you can use the format: file[:page[:rotation]]
    
    Page values:
      • "last" or -1: Last page of PDF
      • "second-last" or -2: Second-to-last page
      • 0 or 1: First page
      • 2, 3, etc.: Page number (1-indexed)
      • -3, -4, etc.: Count from end (negative indexing)
    
    Rotation values:
      • 0: No rotation (default)
      • 90, 180, 270: Rotate counter-clockwise
      • -90, -180, -270: Rotate clockwise
    
    Examples:
    
    \b
    # Use preset with input file (output: input_output.pdf)
    $ label-sheet generate input.pdf --preset shipping-label-with-notes
    
    \b
    # Use preset with custom output
    $ label-sheet generate input.pdf --preset label-only -o my_labels.pdf
    
    \b
    # Manual quadrant configuration - all 4 quadrants
    $ label-sheet generate --q1 label.pdf:last --q2 label.pdf:-1 --q3 notes.pdf:2:-90 --q4 empty.pdf
    
    \b
    # Manual configuration - single quadrant
    $ label-sheet generate --q1 label.jpg -o single.pdf
    
    \b
    # Preset with quadrant override
    $ label-sheet generate input.pdf --preset label-only --q3 notes.pdf:-2:-90
    
    \b
    # Using page numbers and rotations
    $ label-sheet generate --q1 doc.pdf:1:0 --q2 doc.pdf:2:90 --q3 doc.pdf:-1:-90
    
    \b
    # Different file types (PDF, JPG, PNG)
    $ label-sheet generate --q1 label.pdf:last --q2 image.jpg --q3 photo.png:0:180
    
    \b
    # Custom margin and no grid
    $ label-sheet generate input.pdf --preset label-only --margin 0.5 --no-grid
    
    \b
    # High quality output (600 DPI)
    $ label-sheet generate input.pdf --preset shipping-label-with-notes --dpi 600
    
    \b
    # Interactive mode - prompts for input file
    $ label-sheet generate --preset shipping-label-with-notes --interactive
    """
    try:
        quadrants = {}
        
        # Handle interactive mode without preset
        if interactive and not preset:
            console.print(
                "[yellow]Note:[/yellow] Interactive mode requires a preset. "
                "Use --preset <name> with --interactive, or specify quadrants manually.",
                style="bold"
            )
            console.print("\nAvailable presets:")
            preset_list = config_manager.list_presets()
            for name, description in preset_list.items():
                console.print(f"  • {name}: {description}")
            console.print("\nExample: label-sheet generate --preset shipping-label-with-notes --interactive")
            raise typer.Exit(1)
        
        # Check if using preset
        if preset:
            # If interactive mode, prompt for input file
            if interactive and not input_file:
                console.print(f"\n[cyan]Using preset:[/cyan] {preset}")
                input_file = typer.prompt(
                    "Enter input file location",
                    default=""
                )
                if not input_file:
                    console.print(
                        "[red]Error:[/red] Input file is required",
                        style="bold"
                    )
                    raise typer.Exit(1)
            
            if not input_file:
                console.print(
                    "[red]Error:[/red] Input file required when using preset",
                    style="bold"
                )
                raise typer.Exit(1)
            
            # Resolve input file
            input_path = resolve_file_path(input_file)
            
            # Parse manual overrides
            overrides = {}
            for quad_num, spec in [(1, q1), (2, q2), (3, q3), (4, q4)]:
                if spec:
                    file, page, rotation = parse_input_spec(spec)
                    file_path = resolve_file_path(file)
                    overrides[quad_num] = {
                        "source": str(file_path),
                        "page": page,
                        "rotation": rotation,
                    }
            
            # Resolve preset with overrides
            quadrants = config_manager.resolve_preset(preset, input_path, overrides)
            
        else:
            # Manual configuration only
            for quad_num, spec in [(1, q1), (2, q2), (3, q3), (4, q4)]:
                if spec:
                    file, page, rotation = parse_input_spec(spec)
                    file_path = resolve_file_path(file)
                    quadrants[quad_num] = {
                        "source": str(file_path),
                        "page": page,
                        "rotation": rotation,
                    }
        
        if not quadrants:
            console.print(
                "[red]Error:[/red] No quadrants specified. Use --preset or --q1/--q2/--q3/--q4",
                style="bold"
            )
            raise typer.Exit(1)
        
        # Determine output path if not provided
        if output is None:
            if input_file:
                output_path = resolve_file_path(input_file)
                output = str(
                    output_path.with_name(f"{output_path.stem}_output.pdf")
                )
            else:
                output = "output.pdf"
        
        # Load images for each quadrant
        console.print("\n[cyan]Loading inputs...[/cyan]")
        quad_configs = {}
        
        for quad_num, config in quadrants.items():
            source_path = Path(config["source"])
            page = config["page"]
            rotation = config["rotation"]
            
            console.print(f"  Q{quad_num}: {source_path.name} (page: {page}, rotation: {rotation}°)")
            
            try:
                image = InputHandler.load_input(source_path, page, dpi)
                quad_configs[quad_num] = QuadrantConfig(image=image, rotation=rotation)
            except Exception as e:
                console.print(f"[red]Error loading Q{quad_num}:[/red] {e}", style="bold")
                raise typer.Exit(1)
        
        # Generate PDF
        console.print(f"\n[cyan]Generating PDF...[/cyan]")
        layout = LayoutEngine(margin_inches=margin, show_grid=not no_grid)
        
        layout.generate_pdf(
            output,
            q1=quad_configs.get(1),
            q2=quad_configs.get(2),
            q3=quad_configs.get(3),
            q4=quad_configs.get(4),
        )
        
        console.print(f"\n[green]✓[/green] Created: {output}", style="bold")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", style="bold")
        raise typer.Exit(1)


@app.command()
def presets():
    """
    List all available presets.
    
    Presets are predefined quadrant configurations that make it easy to generate
    common label sheet layouts. Use a preset with:
    
        $ label-sheet generate input.pdf --preset <preset-name>
    
    You can override individual quadrants even when using a preset:
    
        $ label-sheet generate input.pdf --preset label-only --q3 notes.pdf:-2:-90
    """
    preset_list = config_manager.list_presets()
    
    if not preset_list:
        console.print("No presets available.", style="dim")
        return
    
    table = Table(title="Available Presets", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    
    for name, description in preset_list.items():
        table.add_row(name, description)
    
    console.print()
    console.print(table)
    console.print()
    console.print("[dim]Use with: label-sheet generate input.pdf --preset <name>[/dim]")


if __name__ == "__main__":
    app()