#!/usr/bin/env bash

ralph_pinned_node_version() {
  local repo_root="${1:?repository root is required}"
  local project_dir="${2:-}"
  local version_file=""
  if [[ -f "$repo_root/.nvmrc" ]]; then
    version_file="$repo_root/.nvmrc"
  elif [[ -n "$project_dir" && -f "$repo_root/$project_dir/.nvmrc" ]]; then
    version_file="$repo_root/$project_dir/.nvmrc"
  fi
  [[ -n "$version_file" ]] || return 1
  tr -d '[:space:]' < "$version_file"
}

ralph_node_bin_dir_for_version() {
  local version="${1:?Node version is required}"
  local current_node="" current_version=""
  if command -v node >/dev/null 2>&1; then
    current_node="$(command -v node)"
    current_version="$(node --version 2>/dev/null || true)"
    if [[ "$current_version" == "v$version" ]]; then
      dirname "$current_node"
      return 0
    fi
  fi

  local nvm_root="${NVM_DIR:-$HOME/.nvm}"
  if [[ -x "$nvm_root/versions/node/v$version/bin/node" \
        && -x "$nvm_root/versions/node/v$version/bin/npm" ]]; then
    printf '%s\n' "$nvm_root/versions/node/v$version/bin"
    return 0
  fi
  return 1
}

ralph_activate_pinned_node() {
  local repo_root="${1:?repository root is required}"
  local project_dir="${2:-}"
  local version bin_dir
  version="$(ralph_pinned_node_version "$repo_root" "$project_dir")" || {
    echo "Missing repository Node pin (.nvmrc)." >&2
    return 1
  }
  bin_dir="$(ralph_node_bin_dir_for_version "$version")" || {
    echo "Pinned Node v$version is not installed. Install it before running Ralph." >&2
    return 1
  }
  export PATH="$bin_dir:$PATH"
  if [[ "$(node --version 2>/dev/null || true)" != "v$version" ]]; then
    echo "Unable to activate pinned Node v$version." >&2
    return 1
  fi
  command -v npm >/dev/null 2>&1 || {
    echo "npm is missing from pinned Node v$version." >&2
    return 1
  }
}
