#!/usr/bin/env python
"""Automated git workflow for pernambucoaval scraper feature.

Usage:
  python git_workflow.py [--branch BRANCH] [--message MESSAGE]

Or simply:
  python git_workflow.py
"""
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--branch', default='feat/pernambucoaval-scraper')
    parser.add_argument('--message', default='feat(pernambucoaval): add structured scraper, validation and predictive_by_group support')
    args = parser.parse_args()

    print("JDB Pernambucoaval Scraper - Automated Git Workflow")
    print("=" * 50)

    # Check git
    print("\nChecking git...")
    run_cmd(['git', '--version'])

    # Current branch
    result = run_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], check=False)
    current = result.stdout.strip()
    print(f"Current branch: {current}\n")

    # Create branch
    print(f"Creating/switching to branch '{args.branch}'...")
    run_cmd(['git', 'checkout', '-b', args.branch], check=False)
    run_cmd(['git', 'checkout', args.branch], check=True)

    # Files to stage
    files = [
        "fetch_pernambucoaval.py",
        "generate_landing_data.py",
        "web/landing.html",
        "web/app.js",
        "web/landing_data.js",
        "SCRAPER_README.md",
        "scraper_validation.py",
        "tests/test_scraper_helpers.py",
        "cache_results.json",
        "cache_results.json.bak",
        "scraper_report_examples.csv",
        "commit_and_push.ps1",
        "git_workflow.py",
        "IMPLEMENTATION_NOTES.md",
    ]

    print("\nStaging files...")
    for f in files:
        p = Path(f)
        if p.exists():
            run_cmd(['git', 'add', f], check=False)
            print(f"  + {f}")
        else:
            print(f"  ? {f} (not found)")

    # Status
    print("\nGit status:")
    run_cmd(['git', 'status', '--short'])

    # Commit
    print(f"\nCommitting: '{args.message}'")
    run_cmd(['git', 'commit', '-m', args.message])

    # Push
    print(f"\nPushing to origin/{args.branch}...")
    run_cmd(['git', 'push', '-u', 'origin', args.branch])

    print("\n" + "=" * 50)
    print("Workflow completed successfully!")
    print(f"Create PR: https://github.com/drbq-advogados/jdb/compare/{args.branch}")


if __name__ == '__main__':
    main()
