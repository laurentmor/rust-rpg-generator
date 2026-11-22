# Automated GitHub releases

## Local repository

This archive contains a real local Git repository on branch `main` (including `.git`). Extract it, then connect it to a GitHub repository:

```powershell
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

GitHub repository settings: **Settings > Actions > General > Workflow permissions**: grant read/write permissions. Enable **Allow GitHub Actions to create and approve pull requests** for release-please.

## Workflows

- `release-please.yml`: on push to `main`, creates/updates a **release PR** based on conventional commits. A GitHub release is generated **when that PR is merged** (not on every push).
- `publish.yml`: **Actions > Certify and publish candidate > Run workflow**: on **every successful manual execution**, runs Windows certification, packages the ZIP and SHA-256 manifest, and creates a unique prerelease tag by default (`v1.0.0-rc2-runN`). It also attaches artifacts when release-please publishes a GitHub release.

The certification must pass before a manual prerelease is created. Release-please itself publishes a GitHub release on merge *before* the `release`-triggered certification job attaches files; therefore a failed certification can leave a GitHub release without assets. To enforce a strict release gate for stable versions, use branch protection and require the full certification before merging the release PR.

## Usage

Use conventional commit messages (`fix: ...`, `feat: ...`) for release-please versioning. Avoid specifying the same manual version twice: tags must be unique.

For local certification and ZIP packaging:

```powershell
.\release.ps1 -Version '1.0.0-rc2' -Heartbeat 5
```

**Caution:** manual French/English playthrough remains pending. The workflow-created candidates are marked prerelease.
