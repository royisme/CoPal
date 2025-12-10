# Context7 Usage Guide – Plan Stage

## Tool Overview

Use Context7 during planning to validate technical decisions and gather detailed API knowledge.

## Recommendations for the Plan Stage

1. **Confirm APIs and interfaces**
   - Retrieve official method signatures and usage examples
   - Check breaking changes across versions
   - Note deprecations or migration steps

2. **Design solutions with confidence**
   - Validate assumptions about third-party integrations
   - Review performance considerations and limitations
   - Identify additional dependencies introduced by the plan

3. **Document references**
   - Record library IDs, versions, and key URLs in the plan
   - List follow-up actions if documentation is incomplete

## Example Commands

```bash
context7 resolve-library-id "nextjs"
context7 get-library-docs --id <id> --topic "api routes"
context7 get-library-docs --id <id> --topic "breaking changes"
```

## Tips

- Capture the exact API version you plan to implement.
- Include retrieved snippets in the plan to guide implementers.
- If documentation gaps remain, flag them as risks in `.copal/artifacts/plan.md`.
