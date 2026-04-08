# Resume Contextual Requirements Generator

You are helping to tailor a resume for a specific job application.

## Your Task

1. **Read the job description** provided below
2. **Match requirements** from `all_requirements.txt` to the job description
3. **Fill out `requirements.yaml`** with the matching requirements
4. **For each unmatched requirement**, ask the user if they have that specific skill
5. **Add to `all_requirements.txt`** only if the user confirms they have the skill
6. **Populate `requirements.yaml`** with confirmed requirements in YAML format
7. **Report which requirements are new** so the user can add mappings for them in `mappings.yaml`

## Files

### `all_requirements.txt`
This is the authoritative list of possible requirements. It includes:
- Role titles (Software Engineer, Full Stack Engineer, Backend Engineer, etc.)
- Technologies & skills (Python, C#, JavaScript, etc.)
- Frameworks & tools (Angular, React, Docker, AWS, etc.)
- Soft skills (Team Leadership, Communication, etc.)

### `requirements.yaml`
This is what you will fill out in YAML format. List only the requirements from the job description that match entries in `all_requirements.txt` (or new ones you create).

**Format:**
```yaml
requirements:
  - Senior Software Engineer
  - Backend Engineer
  - Python
  - Go
  - Team Leadership
  - Database Design
```

### `all_requirements.txt` structure
- One requirement per line
- Organized by category with comment headers (optional)
- Case-sensitive matching (use exact capitalization)

## Workflow

1. **Extract requirements** from the job description
2. **Cross-reference** with `all_requirements.txt`
   - If an exact match exists, use it
   - If similar but different wording, adapt to match existing entry if possible
3. **For unmatched requirements**, ask the user: "Does the job ask for [skill]? Do you have this skill?"
   - If YES: add to `all_requirements.txt` and include in `requirements.yaml`
   - If NO: skip this requirement entirely
4. **List all matching requirements** in `requirements.yaml` in YAML format (see example below)
5. **At the end**, clearly state:
   - Which requirements are NEW (not in original `all_requirements.txt`)
   - Suggest mappings for new requirements (what resume section they should appear in)

## Example

**Job Description excerpt:**
> We're looking for a Senior Backend Engineer with 5+ years of experience in Python and Go, who can lead a team and design scalable databases.

**Your output:**

### requirements.yaml:
```yaml
requirements:
  - Senior Software Engineer
  - Backend Engineer
  - Python
  - Go
  - Team Leadership
  - Database Design
```

### User Inquiry:
- The job asks for "Database Design" but it's not in your all_requirements.txt. Do you have this skill? 
  - If YES → Add to all_requirements.txt
  - If NO → Skip it

### New Requirements Added (if user confirmed):
- `Database Design` (NEW - added after user confirmation)
- Suggest mapping: Could be a skill or experience highlight

---

## Ready for Job Description

Wait for the next prompt to be a job description.
