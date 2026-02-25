# docassemble-privacy-doc-generator

A [Docassemble](https://docassemble.org) package for generating GDPR-compliant privacy policy documents through a guided interview.

## Features

- Guided interview to collect organisation details and data processing information
- Conditional GDPR clause selection based on interview answers
- Generates a formatted, downloadable privacy policy document (DOCX/PDF)
- Covers key GDPR requirements including lawful basis, data retention, third-party sharing, and data subject rights
- Supports jurisdiction-specific variations

## Installation

From your Docassemble server:

1. Navigate to **Package Management**
2. In the "GitHub" field, enter:
   ```
   https://github.com/MickLC/docassemble-privacy-doc-generator
   ```
3. Click **Install**
4. Once installed, the interview will be available at:
   ```
   /interview?i=docassemble.privacydocgenerator:data/questions/main.yml
   ```

## Package Structure

```
docassemble-privacy-doc-generator/
├── README.md
├── setup.py
├── setup.cfg
├── LICENSE
├── .gitignore
└── docassemble/
    ├── __init__.py
    └── privacydocgenerator/
        ├── __init__.py
        ├── data/
        │   ├── questions/
        │   │   ├── main.yml              # Interview entry point
        │   │   └── includes/
        │   │       ├── questions.yml     # Data collection questions
        │   │       ├── logic.yml         # GDPR clause conditional logic
        │   │       └── review.yml        # Review screen before document generation
        │   ├── templates/
        │   │   └── privacy_policy.docx   # Document template
        │   └── sources/
        │       └── gdpr_clauses.json     # Reusable GDPR clause definitions
        └── gdpr_module.py                # Python helper functions
```

## Development

This package follows standard Docassemble package development practices.

To contribute:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes with clear messages
4. Push to your fork and submit a pull request

## License

AGPL-3.0 — see [LICENSE](LICENSE) for details.
