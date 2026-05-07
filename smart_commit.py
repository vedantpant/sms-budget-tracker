"""
Smart Git Commit — AI-powered commit messages using Ollama
Usage: python smart_commit.py
"""

import subprocess
import requests
import json
import sys


def run_cmd(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    stdout = result.stdout.strip() if result.stdout else ""
    stderr = result.stderr.strip() if result.stderr else ""
    return stdout, stderr, result.returncode


def get_git_status():
    """Get list of changed files."""
    stdout, _, _ = run_cmd("git status --porcelain")
    if not stdout:
        return []
    return stdout.split("\n")


def get_git_diff():
    """Get diff of staged + unstaged changes."""
    # Staged changes
    staged, _, _ = run_cmd("git diff --cached --stat")
    staged_detail, _, _ = run_cmd("git diff --cached")

    # Unstaged changes
    unstaged, _, _ = run_cmd("git diff --stat")
    unstaged_detail, _, _ = run_cmd("git diff")

    # Untracked files
    untracked, _, _ = run_cmd("git ls-files --others --exclude-standard")

    diff_summary = ""
    if staged:
        diff_summary += f"=== STAGED CHANGES ===\n{staged}\n\n{staged_detail[:2000]}\n"
    if unstaged:
        diff_summary += f"=== UNSTAGED CHANGES ===\n{unstaged}\n\n{unstaged_detail[:2000]}\n"
    if untracked:
        diff_summary += f"=== NEW FILES ===\n{untracked}\n"

    return diff_summary


def generate_commit_message(diff):
    """Use Ollama to generate a commit message from the diff."""
    prompt = f"""You are a git commit message generator. Analyze the following git diff and generate a professional commit message.

Rules:
1. First line: type(scope): short description (max 72 chars)
   Types: feat, fix, refactor, docs, test, chore, style
2. Blank line after first line
3. Bullet points describing key changes (use - prefix)
4. Be specific about WHAT changed, not HOW

Git diff:
{diff[:3000]}

Respond ONLY with the commit message, nothing else. No markdown backticks."""

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }, timeout=30)

        return response.json()["response"].strip()
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server not running! Start it with: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        sys.exit(1)


def main():
    print("🔍 Checking git status...\n")

    # Check if inside a git repo
    _, _, code = run_cmd("git rev-parse --is-inside-work-tree")
    if code != 0:
        print("❌ Not a git repository!")
        sys.exit(1)

    # Get changed files
    changes = get_git_status()
    if not changes:
        print("✅ Nothing to commit — working tree clean!")
        sys.exit(0)

    # Show changed files
    print("📁 Changed files:")
    for change in changes:
        status = change[:2].strip()
        filename = change[3:]
        icon = {"M": "📝", "A": "➕", "D": "🗑️", "??": "🆕"}.get(status, "❓")
        print(f"   {icon} {filename}")

    # Ask which files to stage
    print("\n" + "=" * 50)
    stage_choice = input("\nStage all files? (y/n/select): ").strip().lower()

    if stage_choice == "y":
        run_cmd("git add .")
        # Unstage files that should be ignored
        run_cmd("git reset HEAD -- all_sms.json")
        run_cmd("git reset HEAD -- all_sms_new.json")
        print("✅ All files staged (respecting .gitignore)")
    elif stage_choice == "select":
        print("\nEnter file names to stage (space-separated):")
        files = input("> ").strip()
        if files:
            run_cmd(f"git add {files}")
            print(f"✅ Staged: {files}")
        else:
            print("❌ No files selected")
            sys.exit(1)
    elif stage_choice == "n":
        # Check if anything already staged
        staged, _, _ = run_cmd("git diff --cached --name-only")
        if not staged:
            print("❌ No files staged. Stage files first or choose 'y'.")
            sys.exit(1)
        print("Using already staged files.")
    else:
        print("❌ Invalid choice")
        sys.exit(1)

    # Get diff for commit message generation
    print("\n🤖 Generating commit message with Ollama...\n")
    diff = get_git_diff()
    if not diff:
        print("❌ No changes detected in diff")
        sys.exit(1)

    commit_msg = generate_commit_message(diff)

    # Show generated message
    print("=" * 50)
    print("📝 Generated commit message:\n")
    print(commit_msg)
    print("\n" + "=" * 50)

    # Ask for confirmation
    choice = input("\n(y) Commit  |  (e) Edit message  |  (n) Cancel: ").strip().lower()

    if choice == "y":
        # Commit
        # Write message to temp file to handle multi-line
        with open(".commit_msg_temp", "w") as f:
            f.write(commit_msg)
        _, stderr, code = run_cmd('git commit -F .commit_msg_temp')
        run_cmd("del .commit_msg_temp 2>nul || rm -f .commit_msg_temp")

        if code == 0:
            print("✅ Committed successfully!")
        else:
            print(f"❌ Commit failed: {stderr}")
            sys.exit(1)

    elif choice == "e":
        print("\nType your commit message (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                lines.pop()  # Remove trailing empty line
                break
            lines.append(line)
        custom_msg = "\n".join(lines)

        with open(".commit_msg_temp", "w") as f:
            f.write(custom_msg)
        _, stderr, code = run_cmd('git commit -F .commit_msg_temp')
        run_cmd("del .commit_msg_temp 2>nul || rm -f .commit_msg_temp")

        if code == 0:
            print("✅ Committed with custom message!")
        else:
            print(f"❌ Commit failed: {stderr}")
            sys.exit(1)
    else:
        print("❌ Cancelled")
        sys.exit(0)

    # Ask to push
    push = input("\n🚀 Push to remote? (y/n): ").strip().lower()
    if push == "y":
        print("Pushing...")
        _, stderr, code = run_cmd("git push origin main")
        if code == 0:
            print("✅ Pushed to origin/main!")
        else:
            print(f"⚠️ Push failed: {stderr}")
            print("Try manually later: git push origin main")
    else:
        print("Skipped push. Run 'git push origin main' later.")

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
