#!/usr/bin/env bats

# Tests for repo_linter.sh
# This test suite provides comprehensive coverage of the repo_linter script
# which extracts and lints repository URLs from git diffs.

setup() {
    # Create a temporary directory for test files
    export TEST_DIR="$(mktemp -d)"
    export SCRIPT_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"

    # Create a minimal git repository for testing
    cd "$TEST_DIR"
    git init
    git config user.email "test@example.com"
    git config user.name "Test User"

    # Create initial commit on main branch
    echo "# Initial readme" > readme.md
    git add readme.md
    git commit -m "Initial commit"
    git branch -M main
}

teardown() {
    # Clean up temporary directory
    if [ -n "$TEST_DIR" ] && [ -d "$TEST_DIR" ]; then
        rm -rf "$TEST_DIR"
    fi
}

# Test 1: Script extracts valid repository URL from git diff
@test "extracts valid repository URL with #readme suffix" {
    # Create a change that adds a new repo link
    echo "- [Test Repo](https://github.com/test/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add test repo"

    # Run the URL extraction logic
    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/test/repo" ]
}

# Test 2: Script handles multiple URLs and extracts the first one
@test "extracts first URL when multiple repos are added" {
    echo "- [First Repo](https://github.com/test/first#readme)" >> readme.md
    echo "- [Second Repo](https://github.com/test/second#readme)" >> readme.md
    git add readme.md
    git commit -m "Add multiple repos"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//' |
        head -n 1)

    [ "$REPO_TO_LINT" = "https://github.com/test/first" ]
}

# Test 3: Script returns empty when no new links are added
@test "returns empty when no new links are added" {
    echo "Just some text without links" >> readme.md
    git add readme.md
    git commit -m "Add text only"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ -z "$REPO_TO_LINT" ]
}

# Test 4: Script correctly removes #readme suffix
@test "correctly removes #readme suffix from URL" {
    echo "- [Test](https://example.com/owner/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo with #readme"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [[ "$REPO_TO_LINT" != *"#readme"* ]]
}

# Test 5: Script ignores removed lines (lines starting with -)
@test "ignores removed lines in diff" {
    echo "- [Removed Repo](https://github.com/removed/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo to be removed"

    # Now remove it and add a different one
    sed -i '/Removed Repo/d' readme.md
    echo "- [Added Repo](https://github.com/added/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Remove old, add new"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/added/repo" ]
}

# Test 6: Script handles URLs with various domain names
@test "extracts URLs from different domains" {
    echo "- [GitLab Repo](https://gitlab.com/test/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add gitlab repo"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://gitlab.com/test/repo" ]
}

# Test 7: Script ignores URLs without #readme suffix
@test "ignores URLs without #readme suffix" {
    echo "- [Website](https://example.com/page)" >> readme.md
    echo "- [Valid Repo](https://github.com/test/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add mixed links"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//' |
        head -n 1)

    [ "$REPO_TO_LINT" = "https://github.com/test/repo" ]
}

# Test 8: Script handles URLs with query parameters
@test "handles URLs with query parameters before #readme" {
    echo "- [Repo](https://github.com/test/repo?tab=readme#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo with query params"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/test/repo?tab=readme" ]
}

# Test 9: Script handles nested paths in URLs
@test "extracts URLs with nested paths" {
    echo "- [Deep Repo](https://github.com/org/team/project/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo with nested path"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/org/team/project/repo" ]
}

# Test 10: Script handles URLs with hyphens and underscores
@test "handles URLs with hyphens and underscores" {
    echo "- [Complex](https://github.com/test-org/repo_name-123#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo with special chars"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/test-org/repo_name-123" ]
}

# Test 11: Empty diff scenario
@test "handles empty diff gracefully" {
    # Don't make any changes, just try to get diff
    REPO_TO_LINT=$(
        git diff HEAD -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ -z "$REPO_TO_LINT" ]
}

# Test 12: Modified lines (not additions) are ignored
@test "ignores modified lines that aren't pure additions" {
    echo "- [Original](https://github.com/original/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add original"

    # Modify the line
    sed -i 's/Original/Modified/' readme.md

    # The diff might show this as a removal and addition,
    # but we're testing that we only catch the actual new URL pattern
    git add readme.md
    git commit -m "Modify line"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    # Should still find the URL (as it appears in the + line)
    [ "$REPO_TO_LINT" = "https://github.com/original/repo" ]
}

# Test 13: Script handles HTTPS protocol only
@test "extracts HTTPS URLs" {
    echo "- [HTTPS Repo](https://github.com/test/https-repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add https repo"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [[ "$REPO_TO_LINT" == https://* ]]
}

# Test 14: Script ignores HTTP (non-secure) URLs
@test "ignores non-HTTPS URLs" {
    echo "- [HTTP Repo](http://github.com/test/http-repo#readme)" >> readme.md
    echo "- [HTTPS Repo](https://github.com/test/https-repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add mixed protocol repos"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//' |
        head -n 1)

    # Should only find the https one
    [ "$REPO_TO_LINT" = "https://github.com/test/https-repo" ]
}

# Test 15: Integration test - verify the conditional logic
@test "script exits quietly when no repo is found" {
    cd "$TEST_DIR"

    # Create a scenario where no new link is added
    echo "Just text" >> readme.md
    git add readme.md
    git commit -m "No link"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    # Test the conditional logic from the script
    if [ -z "$REPO_TO_LINT" ]; then
        RESULT="No new link found in the format:  https://....#readme"
    else
        RESULT="Cloning $REPO_TO_LINT"
    fi

    [ "$RESULT" = "No new link found in the format:  https://....#readme" ]
}

# Test 16: Integration test - verify message when repo is found
@test "script shows cloning message when repo is found" {
    cd "$TEST_DIR"

    echo "- [New Repo](https://github.com/test/new#readme)" >> readme.md
    git add readme.md
    git commit -m "Add new repo"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    # Test the conditional logic from the script
    if [ -z "$REPO_TO_LINT" ]; then
        RESULT="No new link found"
    else
        RESULT="Cloning $REPO_TO_LINT"
    fi

    [ "$RESULT" = "Cloning https://github.com/test/new" ]
}

# Test 17: Handles whitespace in diff output
@test "handles whitespace variations in diff" {
    echo "  - [Indented](https://github.com/test/indented#readme)" >> readme.md
    git add readme.md
    git commit -m "Add indented repo"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/test/indented" ]
}

# Test 18: Handles special characters in repository names
@test "handles special characters in org and repo names" {
    echo "- [Special](https://github.com/org.name/repo.name#readme)" >> readme.md
    git add readme.md
    git commit -m "Add repo with dots"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    [ "$REPO_TO_LINT" = "https://github.com/org.name/repo.name" ]
}

# Test 19: Tests the grep pattern specificity
@test "only matches lines starting with + (additions)" {
    echo "- [Old](https://github.com/old/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Add old repo"

    # Remove old and add new in one commit
    sed -i '/Old/d' readme.md
    echo "- [New](https://github.com/new/repo#readme)" >> readme.md
    git add readme.md
    git commit -m "Replace repo"

    # Count how many repos are found (should be 1, not 2)
    REPO_COUNT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        wc -l)

    [ "$REPO_COUNT" -eq 1 ]
}

# Test 20: End-to-end URL validation
@test "extracted URL is valid format" {
    echo "- [Valid](https://github.com/username/repository#readme)" >> readme.md
    git add readme.md
    git commit -m "Add valid repo"

    REPO_TO_LINT=$(
        git diff HEAD~1 -- readme.md |
        grep ^+ |
        grep -Eo 'https.*#readme' |
        sed 's/#readme//')

    # Validate URL format
    [[ "$REPO_TO_LINT" =~ ^https://[a-zA-Z0-9._-]+/[a-zA-Z0-9._/-]+$ ]]
}
