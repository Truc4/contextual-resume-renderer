# Resume Contextual Requirements Generator

You are helping to tailor a resume for a specific job application.

## Your Task

1. **Read the job description** provided below
2. **Extract all requirements and skills** mentioned in the job description
3. **Fill out `requirements.yaml`** with the extracted requirements
4. **Assign importance values** (1-10) based on how critical each requirement is to the job
5. **Report which requirements are new** so the user can add mappings for them in `mappings.yaml`

## File: `requirements.yaml`

This file contains job requirements with importance ratings. Each requirement has:
- **name**: The requirement/skill name
- **importance**: A numeric value from 1-10 indicating how important this is for the job (10 = critical, 1 = nice to have)

**Format:**
```yaml
requirements:
  - name: "Full Stack Developer"
    importance: 9

  - name: "SQL"
    importance: 10

  - name: "Database"
    importance: 9

  - name: "API Development"
    importance: 8

  - name: "Communication"
    importance: 10

  - name: "Problem Solving"
    importance: 10
```

## Workflow

1. **Extract requirements** from the job description
   - Look for explicit requirements ("must have", "required")
   - Look for preferred skills ("nice to have", "preferred")
   - Extract technologies, frameworks, soft skills, education level, role titles
2. **Assess importance** for each requirement
   - Critical/must-have requirements → 9-10
   - Important requirements → 7-8
   - Nice-to-have → 5-6
   - Bonus skills → 1-4
3. **Populate `requirements.yaml`** in the proper YAML format with name and importance
4. **At the end**, clearly state:
   - Which requirements are NEW (not in current `requirements.yaml`)
   - Suggest mappings for new requirements (what resume section they should appear in)

## Example

**Job Description excerpt:**
> We're looking for a Senior Backend Engineer with 5+ years of experience in Python and Go, who can lead a team and design scalable databases. Strong communication skills required.

**Your output:**

### requirements.yaml:
```yaml
requirements:
  - name: "Senior Software Engineer"
    importance: 9

  - name: "Backend Engineer"
    importance: 10

  - name: "Python"
    importance: 10

  - name: "Go"
    importance: 9

  - name: "Team Leadership"
    importance: 8

  - name: "Database Design"
    importance: 9

  - name: "Communication"
    importance: 10
```

---

## Ready for Job Description

Wait for the next prompt to be a job description.
