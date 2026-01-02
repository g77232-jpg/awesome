#!/bin/bash
set -euo pipefail

# Cleanup function to remove temporary directory
cleanup() {
	if [ -d "cloned" ]; then
		rm -rf cloned
	fi
}

# Set trap to ensure cleanup on exit
trap cleanup EXIT

# Extract repository URL from git diff
extract_repo_url() {
	git diff origin/main -- readme.md |
		grep '^+' |
		grep -Eo 'https.*#readme' |
		sed 's/#readme//' |
		head -n 1
}

# Validate that URL is a GitHub repository
validate_repo_url() {
	local url="$1"

	if [ -z "$url" ]; then
		return 1
	fi

	# Basic validation: ensure it's a GitHub URL
	if [[ ! "$url" =~ ^https://github\.com/ ]]; then
		echo "Error: URL must be a GitHub repository" >&2
		return 1
	fi

	return 0
}

# Clone repository and run linter
lint_repository() {
	local repo_url="$1"

	echo "Cloning $repo_url"
	mkdir -p cloned
	git clone --depth 1 --quiet "$repo_url" cloned

	cd cloned
	npx awesome-lint
}

# Main execution
main() {
	local repo_to_lint

	repo_to_lint=$(extract_repo_url)

	if ! validate_repo_url "$repo_to_lint"; then
		echo "No new link found in the format: https://github.com/...#readme"
		exit 0
	fi

	lint_repository "$repo_to_lint"
}

main
