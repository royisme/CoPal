# Context7 Usage Guide – Analysis Stage

## Tool Overview

Context7 is a documentation discovery tool that helps you:
- Query official documentation and API references
- Gather best practices and example code
- Check library/framework versions and compatibility

## Recommendations for the Analysis Stage

1. **Research technical stacks**
   - Confirm the latest versions used by the project
   - Capture key concepts and terminology
   - Identify constraints or limitations

2. **Collect background information**
   - Review documentation to expand context
   - Understand common use cases and patterns
   - Spot potential technical risks

3. **Record key findings**
   - Add important notes to the analysis report
   - Cite documentation sources and version numbers
   - Flag technical details that require further validation

## Example Queries

```bash
context7 resolve-library-id "react"
context7 get-library-docs --id <id> --topic "what's new"
context7 get-library-docs --id <id> --topic "typing best practices"
context7 get-library-docs --id <id> --topic "specific API usage"
```

## Tips

- Prioritise official documentation to ensure accuracy.
- Record the retrieval time and version for each citation.
- If documentation is unclear, list it as an open question for the next stage.
