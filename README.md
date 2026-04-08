# Contextual Resume Renderer

A template-based resume and cover letter renderer that tailors documents to specific job postings by filtering and reorganizing your existing content.

## What This Is

- **A filtering tool** - it takes your pre-written experience, skills, and paragraphs and selects only the ones relevant to a specific job
- **A layout renderer** - it takes your selected content and formats it into a professional PDF resume and cover letter
- **A time-saver** - automates the manual copy-paste work of tailoring documents to each job application

## What This Is NOT

- **An AI writer** - this does not generate or write resume text for you
- **A content generator** - you must provide all the writing (job history, summaries, cover letter paragraphs) yourself
- **A writing assistant** - it only filters what you've already written, it doesn't improve or rewrite it

You write the content. This tool just shows only the parts that matter for each job.

**Note:** There's a separate prompt available for generating `requirements.yaml` files, but AI is not part of this project itself. The renderer is a deterministic template engine-no LLMs or generative models involved.

## How It Works

1. **Extract job requirements** - read a job posting and list required skills/qualifications
2. **Create a requirements file** - list these with importance values (1-10)
3. **Filter your content** - the tool selects the top skills and experience from your pre-written data
4. **Generate PDF** - formats the filtered content into a tailored, professional resume and cover letter

The tool combines:
- **requirements.yaml** - what the job needs (with importance weights)
- **mappings.yaml** - how to present your skills and experience
- **personal.yaml** - your job history, education, and job title options (gitignored)
- **template/contextual.html.j2** - HTML/CSS layout for the resume

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Copy `data/personal.yaml.example` to `data/personal.yaml` and fill in your job history and education
2. Create `data/requirements.yaml` with job requirements (see example in `data/requirements.yaml`)
3. Run `./render` to generate both resume and cover letter PDFs

## Commands

### Resume Only
```bash
./resume              # Generate resume PDF
./resume --html-only  # Preview as HTML
./resume --open       # Generate PDF and open in browser
```

### Cover Letter
```bash
./cover_letter                                   # Interactive prompts for hiring manager, position, company
./cover_letter --no-prompt                       # Skip prompts, use defaults
./cover_letter --hiring-manager "Jane Smith" \
  --position "Senior Engineer" \
  --company "TechCorp"                           # Specify details directly
./cover_letter --format txt                      # Output text only (default: both)
./cover_letter --format pdf                      # Output PDF only
./cover_letter --open                            # Generate and open PDF in browser
```

### Render Both
```bash
./render                                         # Generate both resume and cover letter
./render --position "Engineer" \
  --company "Acme" \
  --hiring-manager "John"                        # With cover letter details
./render --open                                  # Generate both and open in browser
```

## File Structure

```
contextual-resume-renderer/
├── render                      # Render both resume & cover letter
├── resume                      # Resume render command (bash wrapper)
├── cover_letter                # Cover letter command (bash wrapper)
├── resume.py                   # Resume Python CLI tool
├── cover_letter.py             # Cover letter Python CLI tool
├── requirements.txt            # Python dependencies
├── template/
│   ├── contextual.html.j2     # Jinja2 resume template
│   └── style.css              # CSS styling
└── data/
    ├── personal.yaml          # Your job history, education, and job title options
    ├── personal.yaml.example  # Example to copy and customize
    ├── requirements.yaml      # Job requirements & importance
    ├── requirements.yaml.example  # Example to copy
    ├── mappings.yaml          # Skill/experience descriptions
    ├── mappings.yaml.example  # Example to copy
    ├── cover_letter.yaml      # Cover letter paragraph mappings
    └── cover_letter.yaml.example  # Example to copy
```

## Data Files Explained

### personal.yaml
Contains your personal information and job title options:
- Contact information (name, email, phone, GitHub, LinkedIn, portfolio)
- Job history (companies, dates, titles, role options, achievements)
- Education background
- Main position title options (dynamically selected based on job requirements)
- See `personal.yaml.example` for the structure to copy and customize

### requirements.yaml
Extract requirements from a job posting and list them with importance (1-10):
```yaml
requirements:
  - name: "Python"
    importance: 10
  - name: "Docker"
    importance: 8
  - name: "API Development"
    importance: 9
```
See `requirements.yaml.example` for a template.

### mappings.yaml
Maps each requirement to your pre-written resume content:
```yaml
Python:
  skill: true
  summary: "5+ years building production Python applications"
```

Each requirement can have:
- `skill: true` - include in SKILLS section
- `summary: "text"` - include in SUMMARY section
- `either_or: "group"` - mark as mutually exclusive (only highest importance shown)

See `mappings.yaml.example` for a template.

### cover_letter.yaml
Maps requirements to cover letter paragraphs you've written:
- Each requirement key maps to a paragraph describing your experience
- See `cover_letter.yaml.example` for the structure

## Customizing the Template

Edit `template/contextual.html.j2` to change layout and styling:
- CSS is inline in `<style>` tags
- Jinja2 loops auto-populate sections from your data
- Conditional blocks hide empty fields
