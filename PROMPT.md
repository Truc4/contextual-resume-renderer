# Resume Contextual Requirements Generator

You are helping to tailor a resume for a specific job application.

## Your Task

1. **Read the job description** provided below
2. **Extract all requirements and skills** mentioned in the job description
3. **Fill out `requirements.yaml`** with the top 10 most critical requirements, ranked by importance
4. **Rank by order only** — the first item has importance 10, second has 9, down to 10th item with importance 1
5. **Report which requirements are new** so the user can add mappings for them in `mappings.yaml`

## File: `requirements.yaml`

This file contains job requirements ranked by importance. Only the **top 10 requirements** matter:
- **Order determines importance**: Position 1 = importance 10, Position 2 = importance 9, ... Position 10 = importance 1
- **Anything after position 10 is ignored**
- Only `name` field is needed — no `importance` value

**Format:**
```yaml
requirements:
  - name: "SQL"

  - name: "Backend Development"

  - name: "Python"

  - name: "Database Design"

  - name: "Communication"

  - name: "System Design"

  - name: "Problem Solving"

  - name: "API Development"

  - name: "Team Collaboration"

  - name: "Code Review"
```

## Workflow

1. **Extract requirements** from the job description
   - Look for explicit requirements ("must have", "required")
   - Look for preferred skills ("nice to have", "preferred")
   - Extract technologies, frameworks, soft skills, education level, role titles
2. **Rank the top 10** most critical requirements
   - Order by importance (most critical first)
   - Discard anything ranked 11th or lower
3. **Populate `requirements.yaml`** in the proper YAML format
   - List top 10 in order (no importance field)
   - Position 1 will be treated as importance 10, position 2 as 9, etc.
4. **At the end**, clearly state:
   - Which requirements are NEW (not in current `requirements.yaml`)
   - Suggest mappings for new requirements (what resume section they should appear in)

## Example

**Job Description excerpt:**
> We're looking for a Senior Backend Engineer with 5+ years of experience in Python and Go, who can lead a team and design scalable databases. Strong communication skills required.

**Your output:**

### requirements.yaml (top 10 only, ranked by importance):
```yaml
requirements:
  - name: "Backend Engineer"

  - name: "Python"

  - name: "Communication"

  - name: "Database Design"

  - name: "Team Leadership"

  - name: "Go"

  - name: "Senior Software Engineer"

  - name: "System Design"

  - name: "Problem Solving"

  - name: "5+ Years Experience"
```

**Note:** Items are ordered by importance. Position 1 (Backend Engineer) = importance 10, Position 2 (Python) = importance 9, etc. Anything beyond position 10 is ignored.

---

## Ready for Job Description

Wait for the next prompt to be a job description.
