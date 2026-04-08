#!/usr/bin/env python3
import click
import yaml
import re
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


def slugify(text):
    """Convert text to variable-safe slug (underscores instead of hyphens)."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)  # Use underscore instead of hyphen
    return text.strip('_')


def default_output_path(data):
    """Generate output filename from company and job title."""
    company = data.get('meta', {}).get('company', 'resume')
    job_title = data.get('meta', {}).get('job_title', 'resume')

    company_slug = slugify(company)
    title_slug = slugify(job_title)

    return f"output/{company_slug}_{title_slug}.pdf"




def select_option(options, requirements):
    """Select an option based on exact requirement matches."""
    requirements_set = set(requirements)

    # Check for matches in reverse order (most specific first)
    for option in reversed(options):
        if 'requirements' in option:
            option_reqs = set(option['requirements'])
            # Check if all required terms are in requirements (exact match)
            if option_reqs.issubset(requirements_set):
                return option['title']

    # Return default
    for option in options:
        if option.get('default'):
            return option['title']

    # Fallback to first option
    return options[0]['title'] if options else None


def filter_either_or_requirements(requirements, mappings, importance_map):
    """Filter requirements to keep only one from each either/or group."""
    # Build either_or groups from mappings (with case-insensitive matching)
    either_or_groups = {}
    mapping_keys_lower = {k.lower(): k for k in mappings.keys()}

    for req_key, mapping in mappings.items():
        if 'either_or' in mapping:
            group = mapping['either_or']
            if group not in either_or_groups:
                either_or_groups[group] = []
            either_or_groups[group].append(req_key)

    # For each either_or group, keep only the highest importance requirement
    filtered_requirements = list(requirements)
    requirements_lower = {r.lower(): r for r in requirements}

    for group, group_reqs_from_mappings in either_or_groups.items():
        # Find which reqs from this group are in our requirements (case-insensitive)
        present_reqs = []
        for req_key in group_reqs_from_mappings:
            # Check if this requirement (case-insensitive) is in our requirements
            for req in requirements:
                if req.lower() == req_key.lower():
                    present_reqs.append(req)
                    break

        if len(present_reqs) > 1:
            # Keep only the one with highest importance
            highest_req = max(present_reqs, key=lambda r: importance_map.get(r, 0))
            # Remove all others from filtered list
            for req in present_reqs:
                if req != highest_req and req in filtered_requirements:
                    filtered_requirements.remove(req)

    return filtered_requirements


def load_contextual_resume(requirements_file, mappings_file, roles_file=None, personal_file=None):
    """Load requirements and mappings, collect sections and skills."""
    # Load requirements
    requirements_path = Path(requirements_file)
    if not requirements_path.exists():
        raise click.ClickException(f"Requirements file not found: {requirements_file}")

    # Parse requirements (support both YAML and plain text formats)
    requirements_data = yaml.safe_load(requirements_path.read_text())

    if isinstance(requirements_data, dict) and 'requirements' in requirements_data:
        # YAML format with importance values
        requirements_list = requirements_data['requirements']
        requirements = [req['name'] for req in requirements_list]
        importance_map = {req['name']: req.get('importance', 5) for req in requirements_list}
    else:
        # Plain text format (backwards compatibility)
        requirements_text = requirements_path.read_text()
        requirements = [line.strip() for line in requirements_text.split('\n') if line.strip()]
        importance_map = {req: 5 for req in requirements}  # default importance

    # Load mappings
    mappings_path = Path(mappings_file)
    if not mappings_path.exists():
        raise click.ClickException(f"Mappings file not found: {mappings_file}")

    mappings = yaml.safe_load(mappings_path.read_text()) or {}

    # Filter either/or requirements
    requirements = filter_either_or_requirements(requirements, mappings, importance_map)

    # Load roles if provided
    roles_data = {}
    if roles_file:
        roles_path = Path(roles_file)
        if roles_path.exists():
            roles_data = yaml.safe_load(roles_path.read_text()) or {}

    # Load personal data if provided
    personal_data = {}
    if personal_file:
        personal_path = Path(personal_file)
        if personal_path.exists():
            personal_data = yaml.safe_load(personal_path.read_text()) or {}

    # Initialize data structure
    data = {
        'summaries': [],
        'skills': [],
        'position': 'Software Developer',  # default
        'jobs': []
    }

    # Collect summaries and skills with importance for sorting
    summaries_with_importance = []
    skills_with_importance = []

    # Select main position title based on requirements
    if roles_data.get('main_position'):
        data['position'] = select_option(roles_data['main_position']['options'], requirements)

    # Process each requirement for summaries and skills
    for req in requirements:
        req_lower = req.lower()

        # Find matching mapping (case-insensitive)
        matching_key = None
        for mapping_key in mappings.keys():
            if mapping_key.lower() == req_lower:
                matching_key = mapping_key
                break

        if matching_key and matching_key in mappings:
            mapping = mappings[matching_key]
            importance = importance_map.get(req, 5)  # get importance from requirements file

            # If it's a skill, collect it with importance
            if mapping.get('skill'):
                skills_with_importance.append({
                    'name': req,
                    'importance': importance
                })

            # If it has a summary, collect it with importance
            if 'summary' in mapping:
                summaries_with_importance.append({
                    'text': mapping['summary'],
                    'importance': importance
                })

    # Sort summaries by importance (descending) and take top 5
    summaries_with_importance.sort(key=lambda x: x['importance'], reverse=True)
    data['summaries'] = [s['text'] for s in summaries_with_importance[:5]]

    # Sort skills by importance and include high-importance ones
    # Include all skills with importance >= 7, or top 5-6 whichever is more
    skills_with_importance.sort(key=lambda x: x['importance'], reverse=True)
    high_importance_skills = [s['name'] for s in skills_with_importance if s['importance'] >= 7]
    top_skills = [s['name'] for s in skills_with_importance[:6]]
    # Use high importance skills if there are any, otherwise use top 6
    data['skills'] = high_importance_skills if high_importance_skills else top_skills

    # Build jobs list with selected role titles from personal data
    if personal_data.get('jobs'):
        for job_key, job_config in personal_data['jobs'].items():
            job = {
                'company': job_config['company'],
                'dates': job_config['dates'],
                'role': select_option(job_config['role_options'], requirements),
                'bullets': job_config['bullets']
            }
            data['jobs'].append(job)

    # Add personal contact info to data
    if personal_data.get('name'):
        data['name'] = personal_data['name']
    if personal_data.get('location'):
        data['location'] = personal_data['location']
    if personal_data.get('email'):
        data['email'] = personal_data['email']
    if personal_data.get('phone'):
        data['phone'] = personal_data['phone']
    if personal_data.get('github'):
        data['github'] = personal_data['github']
    if personal_data.get('linkedin'):
        data['linkedin'] = personal_data['linkedin']
    if personal_data.get('portfolio'):
        data['portfolio'] = personal_data['portfolio']
    if personal_data.get('education'):
        data['education'] = personal_data['education']

    return data


@click.command()
@click.argument('requirements_file', type=click.Path(exists=True), required=False)
@click.option('--mappings', default=None, help='Path to mappings YAML file (auto-detected if not provided)')
@click.option('--roles', default=None, help='Path to roles YAML file (auto-detected if not provided)')
@click.option('--personal', default=None, help='Path to personal data YAML file (auto-detected if not provided)')
@click.option('--template', default='template/contextual.html.j2', help='Path to Jinja2 template')
@click.option('--output', default=None, help='Output file path')
@click.option('--html-only', is_flag=True, help='Output HTML only (no PDF rendering)')
@click.option('--open', 'open_after', is_flag=True, help='Open PDF after rendering')
def render(requirements_file, mappings, roles, personal, template, output, html_only, open_after):
    """Render a resume from requirements and mappings files."""

    # Auto-detect requirements file if not provided
    if not requirements_file:
        # Look for requirements.yaml first, then requirements.txt
        if Path('data/requirements.yaml').exists():
            requirements_file = 'data/requirements.yaml'
        else:
            requirements_file = 'data/requirements.txt'

    # Auto-detect mappings file if not provided
    if not mappings:
        req_path = Path(requirements_file)
        # Look for mappings.yaml in same directory
        mappings = str(req_path.parent / 'mappings.yaml')

    # Auto-detect roles file if not provided
    if not roles:
        req_path = Path(requirements_file)
        roles = str(req_path.parent / 'roles.yaml')

    # Auto-detect personal file if not provided
    if not personal:
        req_path = Path(requirements_file)
        personal = str(req_path.parent / 'personal.yaml')

    # Load data from requirements + mappings + roles + personal
    data = load_contextual_resume(requirements_file, mappings, roles, personal)

    # Set up Jinja2 environment
    template_dir = str(Path(template).parent.resolve())
    env = Environment(loader=FileSystemLoader(template_dir))
    tmpl = env.get_template(Path(template).name)

    # Add template directory to data for CSS path
    data['template_dir'] = template_dir

    # Render HTML template
    html_content = tmpl.render(**data)

    # Handle HTML-only output
    if html_only:
        out_path = Path(output or 'output/preview.html')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_content)
        click.echo(f"HTML written to {out_path}")
        return

    # Determine output path
    if not output:
        output = 'output/resume.pdf'

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Render PDF using WeasyPrint
    HTML(string=html_content).write_pdf(str(out_path))
    click.echo(f"PDF written to {out_path}")

    # Open PDF if requested (detached from Python process)
    if open_after:
        import sys
        import os
        opener = 'xdg-open' if sys.platform == 'linux' else 'open'
        # Use Popen to detach from Python — killing Python won't kill the browser
        subprocess.Popen([opener, str(out_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


if __name__ == '__main__':
    render()
