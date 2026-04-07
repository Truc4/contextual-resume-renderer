# Contextual Resume Renderer

A minimal CLI tool to tailor your resume for specific job applications. Write once, render many.

## How It Works

1. **Edit the template once** — customize `template/contextual.html.j2` with your layout and styles
2. **LLM fills data** — send `data/example.yaml` to an LLM with a job listing. The schema guides it to fill relevant skills, experience bullets, and summary
3. **Render to PDF** — the CLI merges template + data and outputs a tailored resume as PDF

The LLM is not part of this project — you provide the filled YAML file, this tool renders it.

## Installation

```bash
pip install -r requirements.txt
```

## Commands

```bash
./render              # Generate resume.pdf
./render --html-only  # Preview as HTML
./render --open       # Generate PDF and open in browser
```

## File Structure

```
contextual-resume-renderer/
├── render                 # Render command
├── resume.py              # Python renderer
├── requirements.txt       # Python dependencies
├── template/
│   └── contextual.html.j2 # Resume template (customize layout & styles)
├── data/
│   ├── requirements.txt   # Your selected requirements
│   ├── mappings.yaml      # Your text for each requirement
│   └── all_requirements.txt # Reference list of all possible requirements
└── output/                # Generated PDFs (gitignored)
```

## Data Structure

See `CONTEXTUAL_USAGE.md` for the two-file system:
- `data/requirements.txt` — your selected requirements
- `data/mappings.yaml` — your text for each requirement (with any fields you need)

## Customizing the Template

Edit `template/contextual.html.j2` to change layout and styling. The template has:
- Inline `<style>` tags — edit CSS directly there
- Jinja2 loops that auto-populate requirements from `data/requirements.txt`
- Conditional sections to hide empty fields

No hardcoded requirement fields needed — the template iterates over whatever requirements you select.

## Quick Start

1. Edit `data/requirements.txt` to pick requirements
2. Edit `data/mappings.yaml` with your text for each requirement
3. Customize `template/contextual.html.j2` (layout & styling)
4. Run `./render` to generate PDF

See `CONTEXTUAL_USAGE.md` for full documentation.


## License

MIT
