# GitHub Actions — Key/Value Cheat Sheet

A workflow file is just nested key-value pairs in YAML. Learn these keys in layers: **workflow-level → job-level → step-level → expressions**. Everything else is detail on top of this skeleton.

```yaml
name: ...        # workflow-level
on: ...           # workflow-level
jobs:
  job_id:        # job-level
    runs-on: ...
    steps:
      - uses: ... # step-level
        run: ...
```

---

## 1. Workflow-level keys

| Key | Purpose | Example |
|---|---|---|
| `name` | Display name of the workflow in the Actions tab | `name: Python CI` |
| `on` | What triggers the workflow | see section 2 |
| `env` | Env vars available to *all* jobs/steps | `env:\n  NODE_ENV: production` |
| `defaults` | Default settings (e.g. shell, working-directory) for every job | `defaults:\n  run:\n    shell: bash` |
| `permissions` | Sets the `GITHUB_TOKEN` scopes for the whole workflow | `permissions:\n  contents: read` |
| `concurrency` | Cancels/queues overlapping runs | see section 6 |
| `jobs` | The actual work — one or more named jobs | see section 3 |

---

## 2. `on` — triggers

```yaml
on:
  push:
    branches: [main]
    paths: ["src/**"]          # only trigger if these paths changed
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
  schedule:
    - cron: "30 0 * * *"        # every day at 00:30 UTC
  workflow_dispatch:            # manual "Run workflow" button
    inputs:
      environment:
        description: "Target environment"
        required: true
        default: "staging"
        type: choice
        options: [staging, production]
  workflow_call:                 # makes this workflow reusable by other workflows
  release:
    types: [published]
```

| Trigger | When it fires |
|---|---|
| `push` | Commits pushed to matching branches/tags |
| `pull_request` | PR opened/updated against matching branches |
| `schedule` | Cron-based, like a crontab |
| `workflow_dispatch` | Manual trigger from the UI/API, can take inputs |
| `workflow_call` | Lets another workflow call this one (`uses: ./.github/workflows/x.yml`) |
| `release` | A GitHub release is created/published |

---

## 3. Job-level keys

```yaml
jobs:
  test:
    runs-on: ubuntu-latest          # required: which runner image
    needs: [build]                  # wait for "build" job to succeed first
    if: github.ref == 'refs/heads/main'   # conditional execution
    timeout-minutes: 10             # kill the job if it hangs
    continue-on-error: false        # if true, failure doesn't fail the whole run
    permissions:
      contents: read
    env:
      PYTHONUNBUFFERED: "1"
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
        os: [ubuntu-latest, windows-latest]
      fail-fast: false              # don't cancel other matrix jobs on first failure
    outputs:
      build-id: ${{ steps.build_step.outputs.id }}
    steps:
      - ...
```

| Key | Purpose |
|---|---|
| `runs-on` | The VM image (`ubuntu-latest`, `windows-latest`, `macos-latest`, or self-hosted labels) |
| `needs` | Declares job dependencies → controls run order |
| `if` | Run the job only if the expression is true |
| `strategy.matrix` | Runs the same job multiple times with different variable combos (e.g. across Python versions/OSes) |
| `strategy.fail-fast` | Whether one matrix failure cancels the rest (default `true`) |
| `outputs` | Values this job exposes for *other jobs* to consume via `needs.<job>.outputs.x` |
| `timeout-minutes` | Safety net against hung jobs |
| `continue-on-error` | Job can fail without failing the overall workflow |

---

## 4. Step-level keys

```yaml
steps:
  - name: Install dependencies          # label shown in the UI
    id: install                          # so other steps can reference its outputs
    uses: actions/setup-python@v6        # run a pre-built Action...
    with:                                 # ...and pass it inputs
      python-version: "3.12"
      cache: "pip"

  - name: Run a shell command
    run: pip install -r requirements.txt   # ...OR run a shell command directly
    shell: bash
    working-directory: ./src
    env:
      PIP_NO_CACHE_DIR: "false"
    continue-on-error: false
    if: success()
```

| Key | Purpose |
|---|---|
| `name` | Optional human-readable label |
| `id` | Reference handle for this step's outputs elsewhere (`steps.<id>.outputs.x`) |
| `uses` | Run a packaged Action (`owner/repo@version`) |
| `run` | Run a raw shell command instead of an Action |
| `with` | Inputs passed to an Action used via `uses` |
| `env` | Step-scoped environment variables |
| `shell` | Override the shell (`bash`, `pwsh`, `cmd`, `python`, etc.) |
| `working-directory` | Run this step from a specific folder |
| `if` | Conditional step execution (see section 5) |
| `continue-on-error` | Step can fail without failing the job |

**Rule of thumb:** use `uses` when someone already built the Action you need (checkout, setup-python, cache, upload-artifact...). Use `run` for anything you'd type at a terminal yourself.

---

## 5. Expressions & contexts — `${{ }}`

Anything inside `${{ }}` is evaluated, not just substituted.

```yaml
if: github.event_name == 'pull_request'
if: ${{ success() }}
if: ${{ always() }}
run: echo "Branch is ${{ github.ref_name }}"
run: pip install -r requirements.txt --extra-index-url ${{ secrets.PYPI_TOKEN }}
```

| Context | What it gives you |
|---|---|
| `github` | Event metadata: `github.ref`, `github.sha`, `github.event_name`, `github.actor`, `github.repository` |
| `env` | Workflow/job/step-level env vars |
| `secrets` | Encrypted secrets you've set in repo/org settings: `secrets.MY_TOKEN` |
| `vars` | Plain (non-secret) repo/org variables: `vars.MY_VAR` |
| `matrix` | Current matrix combination: `matrix.python-version` |
| `steps` | Outputs from previous steps: `steps.install.outputs.x` |
| `needs` | Outputs from dependency jobs: `needs.build.outputs.x` |
| `job` | Current job's status: `job.status` |
| `runner` | Runner info: `runner.os`, `runner.temp` |

**Status check functions** — usually used in `if:`:

| Function | True when |
|---|---|
| `success()` | All previous steps succeeded (default for every step) |
| `failure()` | A previous step failed |
| `always()` | Always — even after failure or cancellation. Good for cleanup/notify steps |
| `cancelled()` | The run was cancelled |

```yaml
- name: Notify on failure
  if: failure()
  run: echo "Something broke!"
```

---

## 6. Concurrency, caching, artifacts — patterns worth knowing

**Cancel superseded runs on the same branch** (saves CI minutes on rapid pushes):

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Cache dependencies** so reinstalling is fast:

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"          # built-in caching, no separate cache action needed
```

**Pass files between jobs** with artifacts:

```yaml
# in job "build"
- uses: actions/upload-artifact@v4
  with:
    name: dist
    path: dist/

# in job "deploy", needs: [build]
- uses: actions/download-artifact@v4
  with:
    name: dist
    path: dist/
```

---

## 7. Full worked example (your Python project)

```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
      fail-fast: false

    steps:
      - name: Check out code
        uses: actions/checkout@v7

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest

      - name: Upload test results on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: pytest-logs-${{ matrix.python-version }}
          path: .pytest_cache/
```

What this adds over your current setup:
- **Matrix** tests across three Python versions in parallel instead of one.
- **`cache: pip`** so dependency installs are fast on repeat runs.
- **`concurrency`** so pushing twice quickly doesn't waste minutes running both.
- **`if: failure()`** step to grab logs only when something breaks.

---

## 8. Suggested learning order

1. `name`, `on`, `jobs`, `runs-on`, `steps`, `uses`, `run`, `with` — get a basic pipeline green.
2. `env`, `secrets`, `${{ }}` expressions — make workflows configurable.
3. `if`, `needs`, job `outputs` — control flow between jobs/steps.
4. `strategy.matrix` — test across multiple versions/platforms at once.
5. `permissions`, `concurrency`, caching, artifacts — production-grade polish.

Official syntax reference (worth bookmarking): https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax