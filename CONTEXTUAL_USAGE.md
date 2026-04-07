# Contextual Resume Renderer — Requirements + Mappings Workflow

This is the **simplest way** to build a resume: two files + a template you customize once.

## Quick Start

### 1. **Pick your requirements** (`data/requirements.txt`)
```
software engineer
knowledge of C++
```

See `data/all_requirements.txt` for the authoritative list. Edit it as you like.

### 2. **Map requirements to your text** (`data/mappings.yaml`)
```yaml
software engineer:
  title: "Software Engineer"
  description: "I am a software engineer with 5 years experience..."
  company: "Example Corp"

knowledge of C++:
  skill: "C++"
  proficiency: "Advanced"
  description: "5 years of experience with modern C++..."
```

Each requirement maps to **fields** (you define these). Fields can be anything: title, description, dates, proficiency, etc.

### 3. **Create your template** (`template/contextual.html.j2`)

Your template uses placeholders in the form: `{{ requirement_name_field_name }}`

```html
<h2>Experience</h2>
<h3>{{ software_engineer_title }}</h3>
<p>{{ software_engineer_description }}</p>
<p>{{ software_engineer_company }}</p>

<h2>Skills</h2>
<p><strong>{{ knowledge_of_c_skill }}</strong> ({{ knowledge_of_c_proficiency }})</p>
<p>{{ knowledge_of_c_description }}</p>
```

**Variable naming rules:**
- Requirement: `"software engineer"` → slug: `software_engineer`
- Field: `title` → full variable: `{{ software_engineer_title }}`
- All spaces/special chars converted to underscores

### 4. **Render to PDF**
```bash
python resume.py data/requirements.txt
# Output: output/resume.pdf
```

## How Variable Names Work

**Requirement** + **Field** = **Jinja2 Variable**

| Requirement | Field | Variable |
|---|---|---|
| `software engineer` | `title` | `{{ software_engineer_title }}` |
| `knowledge of C++` | `proficiency` | `{{ knowledge_of_c_proficiency }}` |
| `team leadership` | `description` | `{{ team_leadership_description }}` |

**Conversion:**
1. Requirement name → lowercase
2. Strip special characters (keep only letters, numbers, spaces)
3. Replace spaces/dashes with underscores
4. Append field name with underscore

## File Structure

```
data/
  ├── all_requirements.txt    ← Authoritative list (reference only)
  ├── requirements.txt        ← Your selected requirements (edit this)
  └── mappings.yaml          ← Your text for each requirement (edit this)

template/
  └── contextual.html.j2     ← Your resume template (customize once)

resume.py                     ← Renderer (don't edit)
```

## Workflow

1. **First time:**
   - Copy a requirement from `all_requirements.txt` to `requirements.txt`
   - Add a mapping for it in `mappings.yaml` with your hand-written text
   - Use the variable name in `template/contextual.html.j2`

2. **Iterate:**
   - Edit `mappings.yaml` to tweak your text
   - Edit CSS styles inline in the template
   - Run `python resume.py data/requirements.txt --html-only` to preview
   - When happy: `python resume.py data/requirements.txt` to generate PDF

## Customization

### Template
Edit `template/contextual.html.j2` to:
- Add/remove sections
- Reorder fields
- Add conditional logic (`{% if variable %}`...`{% endif %}`)

### Styling
Styles are inline `<style>` in the template. Edit CSS directly there.

### Mappings
Add as many fields per requirement as you need:

```yaml
software engineer:
  title: "Software Engineer"
  company: "Example Corp"
  location: "San Francisco, CA"
  dates: "Jan 2020 – Present"
  description: "..."
  achievements: "..."  # As many as you want
```

Then use them in the template:
```html
{{ software_engineer_title }} at {{ software_engineer_company }}
{{ software_engineer_location }} ({{ software_engineer_dates }})
<p>{{ software_engineer_description }}</p>
```

## Commands

```bash
# Generate PDF
python resume.py data/requirements.txt

# Preview as HTML (open in browser, iterate on styles)
python resume.py data/requirements.txt --html-only

# Specify different requirements file
python resume.py data/my_requirements.txt

# Specify different mappings
python resume.py data/requirements.txt --mappings data/my_mappings.yaml

# Specify output path
python resume.py data/requirements.txt --output ~/Desktop/my_resume.pdf

# Open PDF automatically after rendering
python resume.py data/requirements.txt --open
```

## Tips

- **Add more requirements** to `all_requirements.txt` for your specific domain
- **Create multiple requirement files** for different roles: `data/frontend_reqs.txt`, `data/backend_reqs.txt`
- **Use template conditionals** to hide empty sections:
  ```html
  {% if software_engineer_title %}
    <div class="job">...</div>
  {% endif %}
  ```
- **Keep mappings.yaml organized** — list requirements in the same order as requirements.txt

That's it! Two files, one template, instant tailored resume.
