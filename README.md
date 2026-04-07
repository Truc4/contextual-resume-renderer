# Contextual Resume Renderer

A CLI tool to generate tailored resumes for job applications by mapping job requirements to your experience and skills.

## How It Works

1. **Extract job requirements** — from a job posting, extract required skills and qualifications
2. **Create a requirements file** — list the requirements with importance values (1-10)
3. **Render your resume** — the tool selects the top skills and experience from your data to match the job
4. **Generate PDF** — outputs a tailored, professionally formatted resume

The tool combines:
- **requirements.yaml** — what the job needs (with importance weights)
- **mappings.yaml** — how to present your skills and experience
- **personal.yaml** — your job history and education (gitignored)
- **template/contextual.html.j2** — HTML/CSS layout for the resume

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Copy `data/personal.yaml.example` to `data/personal.yaml` and fill in your job history and education
2. Create `data/requirements.yaml` with job requirements (see example in `data/requirements.yaml`)
3. Run `./render` to generate `output/resume.pdf`

## Commands

```bash
./render              # Generate resume PDF
./render --html-only  # Preview as HTML
./render --open       # Generate PDF and open in browser
```

## File Structure

```
contextual-resume-renderer/
├── render                      # Render command (bash wrapper)
├── resume.py                   # Python CLI tool
├── requirements.txt            # Python dependencies
├── template/
│   ├── contextual.html.j2     # Jinja2 resume template
│   └── style.css              # CSS styling
└── data/
    ├── personal.yaml          # Your job history & education (gitignored)
    ├── personal.yaml.example  # Template for personal.yaml
    ├── requirements.yaml      # Job requirements & importance
    ├── mappings.yaml          # Skill/experience descriptions
    └── roles.yaml             # Job title templates
```

## Data Files Explained

### personal.yaml (gitignored)
Contains your personal information:
- Job history (companies, dates, titles, achievements)
- Education background
- See `personal.yaml.example` for the structure

### requirements.yaml
Extract from a job posting:
```yaml
requirements:
  - name: "Python"
    importance: 10
  - name: "Docker"
    importance: 8
  - name: "API Development"
    importance: 9
```

### mappings.yaml
Maps requirements to your resume text:
```yaml
Python:
  skill: true
  summary: "5+ years building production Python applications"
```

Each requirement can have:
- `skill: true` — include in SKILLS section
- `summary: "text"` — include in SUMMARY section
- `either_or: "group"` — mark as mutually exclusive (only highest importance shown)

## Customizing the Template

Edit `template/contextual.html.j2` to change layout and styling:
- CSS is inline in `<style>` tags
- Jinja2 loops auto-populate sections from your data
- Conditional blocks hide empty fields

## License

MIT
