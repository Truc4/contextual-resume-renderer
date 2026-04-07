#!/usr/bin/env python3
import click
import yaml
from pathlib import Path
from datetime import date


def load_contextual_cover_letter(requirements_file, cover_letter_file, personal_file=None):
    """Load requirements and cover letter mappings, generate letter content."""
    # Load requirements
    requirements_path = Path(requirements_file)
    if not requirements_path.exists():
        raise click.ClickException(f"Requirements file not found: {requirements_file}")

    requirements_data = yaml.safe_load(requirements_path.read_text())

    if isinstance(requirements_data, dict) and 'requirements' in requirements_data:
        requirements_list = requirements_data['requirements']
        requirements = [req['name'] for req in requirements_list]
    else:
        requirements_text = requirements_path.read_text()
        requirements = [line.strip() for line in requirements_text.split('\n') if line.strip()]

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

    # Collect paragraphs for matched requirements
    paragraphs = []
    for req in requirements:
        req_lower = req.lower()
        # Find matching mapping (case-insensitive)
        for mapping_key in cover_letter_data.keys():
            if mapping_key.lower() == req_lower:
                mapping = cover_letter_data[mapping_key]
                if isinstance(mapping, dict) and 'paragraph' in mapping:
                    paragraphs.append(mapping['paragraph'])
                break

    # Get job title from requirements data if available
    job_title = 'the position'
    if isinstance(requirements_data, dict) and 'job_title' in requirements_data:
        job_title = requirements_data['job_title']

    return {
        'paragraphs': paragraphs,
        'passion': passion,
        'job_title': job_title,
        'name': personal_data.get('name', 'Your Name'),
        'email': personal_data.get('email', 'your.email@example.com'),
        'phone': personal_data.get('phone', '(123) 456-7890'),
    }


@click.command()
@click.argument('requirements_file', type=click.Path(exists=True), required=False)
@click.option('--cover-letter', default=None, help='Path to cover letter mappings file (auto-detected if not provided)')
@click.option('--personal', default=None, help='Path to personal data file (auto-detected if not provided)')
@click.option('--hiring-manager', default='Hiring Manager', help='Name of hiring manager')
@click.option('--job-title', default=None, help='Job title (auto-detected from requirements if not provided)')
@click.option('--output', default=None, help='Output file path')
def generate(requirements_file, cover_letter, personal, hiring_manager, job_title, output):
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

    # Use provided job title or fall back to detected one
    if job_title:
        data['job_title'] = job_title

    # Determine output path
    if not output:
        output = 'output/cover_letter.txt'

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build cover letter
    letter = f"{date.today().strftime('%B %d, %Y')}\n\n"
    letter += f"Dear {hiring_manager},\n\n"
    letter += f"I am writing to express my strong interest in the {data['job_title']} position at your organization. "
    letter += f"I am confident that my skills and experience make me an excellent fit for this role.\n\n"

    # Add passion/personalized section if it exists
    if data['passion']:
        letter += f"{data['passion']}\n\n"

    # Add requirement paragraphs
    for para in data['paragraphs']:
        letter += f"{para}\n\n"

    # Closing
    letter += f"I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how my background, skills, and enthusiasm align with your needs. "
    letter += f"Please feel free to contact me at {data['phone']} or {data['email']} at your convenience.\n\n"
    letter += f"Thank you for considering my application. I look forward to hearing from you.\n\n"
    letter += f"Sincerely,\n\n{data['name']}\n"

    # Write to file
    out_path.write_text(letter)
    click.echo(f"Cover letter written to {out_path}")


if __name__ == '__main__':
    generate()
