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
    """Generate output filename from personal name."""
    name = data.get('name', 'resume')
    # Split name into first and last
    name_parts = name.split()
    if len(name_parts) >= 2:
        first_name = slugify(name_parts[0])
        last_name = slugify(name_parts[-1])
        filename = f"{first_name}-{last_name}-resume"
    else:
        filename = slugify(name) or 'resume'

    return f"output/{filename}.pdf"




def select_option(options, requirements, importance_map=None):
    """Select an option based on exact requirement matches, preferring highest importance."""
    requirements_set = set(requirements)
    matching_options = []

    # Find all matching options
    for option in options:
        if 'requirements' in option:
            option_reqs = set(option['requirements'])
            # Check if all required terms are in requirements (exact match)
            if option_reqs.issubset(requirements_set):
                matching_options.append(option)

    # If we have matches, pick the one with highest importance
    if matching_options:
        if importance_map:
            # Find the match with the highest importance requirement
            best_option = max(matching_options,
                            key=lambda opt: max(importance_map.get(req, 0) for req in opt['requirements']))
            return best_option['title']
        else:
            # Without importance map, return the last match (most specific)
            return matching_options[-1]['title']

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


def load_contextual_resume(requirements_file, mappings_file, roles_file=None, personal_file=None, location_override=None, summary_override=None):
    """Load requirements and mappings, collect sections and skills."""
    # Load requirements
    requirements_path = Path(requirements_file)
    if not requirements_path.exists():
        raise click.ClickException(f"Requirements file not found: {requirements_file}")

    # Parse requirements (support both YAML and plain text formats)
    requirements_data = yaml.safe_load(requirements_path.read_text())

    if isinstance(requirements_data, dict) and 'requirements' in requirements_data:
        # YAML format
        requirements_list = requirements_data['requirements']
        requirements = [req['name'] for req in requirements_list]
        # Importance based on order: first item = 10, last = 1
        importance_map = {req['name']: max(1, 11 - i) for i, req in enumerate(requirements_list)}
    else:
        # Plain text format (backwards compatibility)
        requirements_text = requirements_path.read_text()
        requirements = [line.strip() for line in requirements_text.split('\n') if line.strip()]
        importance_map = {req: max(1, 11 - i) for i, req in enumerate(requirements)}

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
    # Check personal_data first, then roles_data for backwards compatibility
    main_position_data = personal_data.get('main_position') or roles_data.get('main_position')
    if main_position_data:
        data['position'] = select_option(main_position_data['options'], requirements, importance_map)

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

    # Sort summaries by importance (descending) and take top 4
    summaries_with_importance.sort(key=lambda x: x['importance'], reverse=True)
    if summary_override:
        data['summaries'] = [summary_override]
    else:
        data['summaries'] = [s['text'] for s in summaries_with_importance[:4]]

    # Sort skills by importance and include top 10
    skills_with_importance.sort(key=lambda x: x['importance'], reverse=True)
    data['skills'] = [s['name'] for s in skills_with_importance[:10]]

    # Build jobs list with selected role titles from personal data
    if personal_data.get('jobs'):
        for job_key, job_config in personal_data['jobs'].items():
            job = {
                'company': job_config['company'],
                'dates': job_config['dates'],
                'role': select_option(job_config['role_options'], requirements, importance_map),
                'bullets': job_config['bullets']
            }
            data['jobs'].append(job)

    # Add personal contact info to data
    if personal_data.get('name'):
        data['name'] = personal_data['name']

    # Handle location with override
    default_location = personal_data.get('location')
    final_location = location_override or default_location
    if final_location:
        # If location differs from default, format as relocation notice
        if location_override and location_override != default_location:
            data['location'] = f"Relocating to {final_location} - May 2026"
        else:
            data['location'] = final_location
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
@click.option('--location', default=None, help='Override location (shows as "Relocating to X, Y May 2026" if different from default)')
@click.option('--summary', default=None, help='Override summary section')
def render(requirements_file, mappings, roles, personal, template, output, html_only, open_after, location, summary):
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
    data = load_contextual_resume(requirements_file, mappings, roles, personal, location, summary)

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
        output = default_output_path(data)

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
