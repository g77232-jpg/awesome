# Repository Linter Tests

This directory contains comprehensive tests for the `repo_linter.sh` script.

## Test Coverage

The test suite (`repo_linter.test.sh`) provides 20 comprehensive test cases covering:

### Core Functionality Tests
1. **Valid URL extraction** - Ensures the script correctly extracts repository URLs with `#readme` suffix
2. **Multiple URL handling** - Tests behavior when multiple repositories are added
3. **Empty diff handling** - Validates graceful handling when no links are found
4. **#readme suffix removal** - Confirms proper URL cleaning
5. **Diff line filtering** - Ensures only additions (lines starting with `+`) are processed

### Edge Cases
6. **Removed lines** - Verifies that deletions (lines starting with `-`) are ignored
7. **Multiple domains** - Tests extraction from GitHub, GitLab, and other platforms
8. **URLs without #readme** - Ensures non-matching URLs are filtered out
9. **Query parameters** - Handles URLs with query strings before `#readme`
10. **Nested paths** - Supports repositories with deep path structures

### Input Validation
11. **Empty diff** - Handles scenarios with no file changes
12. **Modified lines** - Processes line modifications correctly
13. **HTTPS protocol** - Validates HTTPS URL extraction
14. **HTTP filtering** - Ensures non-HTTPS URLs are ignored
15. **Whitespace handling** - Manages indentation and spacing variations

### Integration Tests
16. **Conditional logic (no repo)** - Tests the "no new link found" code path
17. **Conditional logic (repo found)** - Tests the "cloning" code path
18. **Special characters** - Handles dots, hyphens, underscores in names
19. **Pattern specificity** - Verifies grep pattern accuracy
20. **URL format validation** - End-to-end validation of extracted URLs

## Prerequisites

To run these tests, you need to install [BATS (Bash Automated Testing System)](https://github.com/bats-core/bats-core):

### Installation

**macOS:**
```bash
brew install bats-core
```

**Ubuntu/Debian:**
```bash
sudo apt-get install bats
```

**From source:**
```bash
git clone https://github.com/bats-core/bats-core.git
cd bats-core
./install.sh /usr/local
```

## Running the Tests

### Run all tests:
```bash
bats .github/workflows/repo_linter.test.sh
```

### Run with verbose output:
```bash
bats --tap .github/workflows/repo_linter.test.sh
```

### Run a specific test:
```bash
bats --filter "extracts valid repository URL" .github/workflows/repo_linter.test.sh
```

### Run tests with timing information:
```bash
bats --timing .github/workflows/repo_linter.test.sh
```

## Expected Output

When all tests pass, you should see:
```
✓ extracts valid repository URL with #readme suffix
✓ extracts first URL when multiple repos are added
✓ returns empty when no new links are added
✓ correctly removes #readme suffix from URL
✓ ignores removed lines in diff
✓ extracts URLs from different domains
✓ ignores URLs without #readme suffix
✓ handles URLs with query parameters before #readme
✓ extracts URLs with nested paths
✓ handles URLs with hyphens and underscores
✓ handles empty diff gracefully
✓ ignores modified lines that aren't pure additions
✓ extracts HTTPS URLs
✓ ignores non-HTTPS URLs
✓ script exits quietly when no repo is found
✓ script shows cloning message when repo is found
✓ handles whitespace variations in diff
✓ handles special characters in org and repo names
✓ only matches lines starting with + (additions)
✓ extracted URL is valid format

20 tests, 0 failures
```

## Continuous Integration

These tests are automatically run in GitHub Actions on every pull request. See the `test_repo_linter.yml` workflow for CI configuration.

## Test Structure

Each test follows this pattern:
1. **setup()** - Creates a temporary git repository
2. **test execution** - Simulates realistic git diff scenarios
3. **assertions** - Validates expected behavior
4. **teardown()** - Cleans up temporary files

## Contributing

When modifying `repo_linter.sh`, please:
1. Run the existing test suite to ensure no regressions
2. Add new tests for any new functionality
3. Update this README if new test categories are added

## Troubleshooting

**Tests fail with "command not found: bats"**
- Install BATS using the installation instructions above

**Tests fail with git errors**
- Ensure git is installed and configured with user.name and user.email

**Permission denied errors**
- Make the test file executable: `chmod +x .github/workflows/repo_linter.test.sh`
