# Project maintenance utilities

This directory provides optional tools to help satisfy the **mandatory** project documentation rules. Read [root AGENTS.md](../AGENTS.md) and the [documentation roll-up checklist](../project-archive/processes/DOCUMENTATION-ROLLUP-CHECKLIST.md) before changing the repository.

## Documentation roll-up checker

The script [check_documentation_rollup.py](check_documentation_rollup.py) checks that changed files within project-archive have all their ancestor DIRECTORY.md records included in the same Git change set, and that root onboarding changes include an update to the project overview.

Recommended use from the clean Git worktree:

```sh
python3 scripts/check_documentation_rollup.py --staged
```

For a fully committed branch comparison, use the --base option with the branch's common base. The checker verifies **structural coverage**, not the truth of the status claims, hash identity, source evidence, or whether a newly added historical note is safe for public publication. Those require review.

The engineering procedures are references that can evolve. Accurate documentation and necessary safety/authorization checks are binding.
