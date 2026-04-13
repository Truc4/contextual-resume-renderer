#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from datetime import date
from jinja2 import Template
from weasyprint import HTML
import tempfile
import subprocess
import sys
import os


def load_contextual_cover_letter(requirements_file, cover_letter_file, personal_file=None):
    """Load requirements and cover letter mappings, generate letter content."""
    # Load requirements
    requirements_path = Path(requirements_file)
    if not requirements_path.exists():
        raise click.ClickException(f"Requirements file not found: {requirements_file}")

    requirements_data = yaml.safe_load(requirements_path.read_text())

    if isinstance(requirements_data, dict) and 'requirements' in requirements_data:
        requirements_list = requirements_data['requirements']
        # Importance based on order: first item = 10, last = 1
        requirements = [(req['name'], max(1, 11 - i)) for i, req in enumerate(requirements_list)]
    else:
        requirements_text = requirements_path.read_text()
        requirements = [(line.strip(), max(1, 11 - i)) for i, line in enumerate(requirements_text.split('\n')) if line.strip()]

    # Load cover letter mappings
    cover_letter_path = Path(cover_letter_file)
    if not cover_letter_path.exists():
        raise click.ClickException(f"Cover letter file not found: {cover_letter_file}")

    cover_letter_data = yaml.safe_load(cover_letter_path.read_text()) or {}

    # Load personal data if provided
    personal_data = {}
    if personal_file:
        personal_path = Path(personal_file)
        if personal_path.exists():
            personal_data = yaml.safe_load(personal_path.read_text()) or {}

    # Get passion/personalized section if it exists
    passion = None
    if cover_letter_data.get('_passion'):
        passion = cover_letter_data['_passion'].get('paragraph') if isinstance(cover_letter_data['_passion'], dict) else cover_letter_data['_passion']

    # Collect paragraphs for matched requirements (with importance scores)
    paragraphs_with_importance = []
    for req, importance in requirements:
        req_lower = req.lower()
        # Find matching mapping (case-insensitive)
        for mapping_key in cover_letter_data.keys():
            if mapping_key.lower() == req_lower:
                mapping = cover_letter_data[mapping_key]
                if isinstance(mapping, dict) and 'paragraph' in mapping:
                    paragraphs_with_importance.append({
                        'text': mapping['paragraph'],
                        'importance': importance
                    })
                break

    # Sort by importance and take top 5
    paragraphs_with_importance.sort(key=lambda x: x['importance'], reverse=True)
    paragraphs = [p['text'] for p in paragraphs_with_importance[:5]]

    return {
        'paragraphs': paragraphs,
        'passion': passion,
        'name': personal_data.get('name', 'Your Name'),
        'email': personal_data.get('email', 'your.email@example.com'),
        'phone': personal_data.get('phone', '(123) 456-7890'),
    }


def build_cover_letter_text(data, hiring_manager, job_title, company):
    """Build plain text cover letter."""
    letter = f"{date.today().strftime('%B %d, %Y')}\n\n"

    # Use default if not provided
    if not hiring_manager:
        hiring_manager = 'Hiring Manager'
    letter += f"Dear {hiring_manager},\n\n"

    # Build opening sentence dynamically based on what's provided
    opening = "I am writing to express my strong interest in"
    if job_title:
        opening += f" the {job_title} position"
        if company:
            opening += f" at {company}"
        else:
            opening += " at your organization"
    elif company:
        opening += f" the position at {company}"
    else:
        opening += " the position at your organization"
    opening += ". I am confident that my skills and experience make me an excellent fit for this role.\n\n"

    letter += opening

    # Add passion/personalized section if it exists
    if data['passion']:
        letter += f"{data['passion']}\n\n"

    # Add requirement paragraphs
    for para in data['paragraphs']:
        letter += f"{para}\n\n"

    # Closing
    letter += f"I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how I align with your needs. "
    letter += f"Please feel free to contact me at {data['phone']} or {data['email']} at your convenience.\n\n"
    letter += f"Thank you for considering my application. I look forward to hearing from you.\n\n"
    letter += f"Sincerely,\n\n{data['name']}\n"

    return letter


def build_cover_letter_html(text):
    """Convert plain text cover letter to HTML for PDF rendering."""
    # Escape HTML entities
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Convert paragraphs (double newlines)
    paragraphs = text.split('\n\n')
    html_content = '\n'.join(f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs if p.strip())

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            margin: 0.5in 1in;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        p {{
            margin: 0 0 12px 0;
            text-align: justify;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    return html


@click.command()
@click.argument('requirements_file', type=click.Path(exists=True), required=False)
@click.option('--cover-letter', default=None, help='Path to cover letter mappings file (auto-detected if not provided)')
@click.option('--personal', default=None, help='Path to personal data file (auto-detected if not provided)')
@click.option('--hiring-manager', default=None, help='Name of hiring manager')
@click.option('--position', '--job-title', default=None, help='Job position/title')
@click.option('--company', default=None, help='Company name')
@click.option('--location', default=None, help='Location (accepted for compatibility, not used in cover letter)')
@click.option('--output', default=None, help='Output file path (auto-detected if not provided)')
@click.option('--format', type=click.Choice(['txt', 'pdf', 'both']), default='both', help='Output format')
@click.option('--no-prompt', is_flag=True, help='Skip interactive prompts and use defaults/options')
@click.option('--open', 'open_after', is_flag=True, help='Open PDF in browser after rendering')
def generate(requirements_file, cover_letter, personal, hiring_manager, position, company, location, output, format, no_prompt, open_after):
    """Generate a cover letter from requirements and mappings."""

    # Auto-detect requirements file if not provided
    if not requirements_file:
        if Path('data/requirements.yaml').exists():
            requirements_file = 'data/requirements.yaml'
        else:
            requirements_file = 'data/requirements.txt'

    # Auto-detect cover letter file if not provided
    if not cover_letter:
        req_path = Path(requirements_file)
        cover_letter = str(req_path.parent / 'cover_letter.yaml')

    # Auto-detect personal file if not provided
    if not personal:
        req_path = Path(requirements_file)
        personal = str(req_path.parent / 'personal.yaml')

    # Load data
    data = load_contextual_cover_letter(requirements_file, cover_letter, personal)

    # Interactive prompts for cover letter details
    if not no_prompt:
        if hiring_manager is None:
            hiring_manager = click.prompt('Hiring Manager name', default='')
        if position is None:
            position = click.prompt('Position/Job Title', default='')
        if company is None:
            company = click.prompt('Company name', default='')

    # Determine output path
    if not output:
        if company and position:
            company_slug = company.lower().replace(' ', '_')
            position_slug = position.lower().replace(' ', '_')
            base_output = f"output/{company_slug}_{position_slug}_cover_letter"
        else:
            base_output = 'output/cover_letter'

    # Build cover letter text (use provided values, empty strings for defaults)
    letter = build_cover_letter_text(data, hiring_manager or '', position or '', company or '')

    # Write outputs based on format
    if format in ['txt', 'both']:
        txt_output = Path(output or f"{base_output}.txt")
        txt_output.parent.mkdir(parents=True, exist_ok=True)
        txt_output.write_text(letter)
        click.echo(f"Text cover letter written to {txt_output}")

    if format in ['pdf', 'both']:
        pdf_output = Path(output or f"{base_output}.pdf") if output else Path(f"{base_output}.pdf")
        pdf_output.parent.mkdir(parents=True, exist_ok=True)
        html = build_cover_letter_html(letter)
        HTML(string=html).write_pdf(str(pdf_output))
        click.echo(f"PDF cover letter written to {pdf_output}")

        # Open PDF if requested (detached from Python process)
        if open_after:
            opener = 'xdg-open' if sys.platform == 'linux' else 'open'
            # Use Popen to detach from Python — killing Python won't kill the browser
            subprocess.Popen([opener, str(pdf_output)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


if __name__ == '__main__':
    generate()
