#!/usr/bin/env bash

# Resolve Ralph's protected Codex profile configuration into concrete adapter
# arguments. The resolver is intentionally fail-closed: a missing profile,
# unsupported mode, or malformed value stops before an agent session starts.

ralph_codex_profile_values() {
  local config="${1:?config path is required}"
  local requested_profile="${2:-}"
  local mode="${3:?Ralph mode is required}"
  local requested_model="${4:-}"
  local requested_effort="${5:-}"
  local requested_verbosity="${6:-}"
  local requested_approval="${7:-}"

  command -v ruby >/dev/null 2>&1 || {
    echo "Ruby is required to resolve .ralph/config.yaml Codex profiles." >&2
    return 1
  }

  ruby -ryaml - "$config" "$requested_profile" "$mode" \
    "$requested_model" "$requested_effort" "$requested_verbosity" \
    "$requested_approval" <<'RUBY'
config_path, requested, mode, requested_model, requested_effort,
  requested_verbosity, requested_approval = ARGV
config = YAML.load_file(config_path)
codex = config.dig("agent", "codex")
abort "Missing agent.codex profile configuration." unless codex.is_a?(Hash)

profile_name = requested.to_s.strip
if profile_name.empty?
  profile_name = case mode
                 when "repair" then "repair"
                 when "architecture_review" then "architecture"
                 when "bootstrap" then "deep"
                 else codex.fetch("default_profile", "default").to_s
                 end
end

profiles = codex["profiles"]
abort "Missing agent.codex.profiles." unless profiles.is_a?(Hash)
profile = profiles[profile_name]
abort "Unknown Codex profile: #{profile_name}" unless profile.is_a?(Hash)

allowed_modes = Array(profile["allowed_modes"]).map(&:to_s)
abort "Codex profile #{profile_name} does not allow mode #{mode}." unless allowed_modes.include?(mode)

model = profile["model"].to_s.strip
effort = profile["reasoning_effort"].to_s.strip
verbosity = profile["verbosity"].to_s.strip

allow_model_override = codex["allow_model_override"] == true
allow_effort_override = codex["allow_effort_override"] == true
allow_verbosity_override = codex["allow_verbosity_override"] == true
allow_xhigh = codex["allow_xhigh"] == true

unless requested_model.to_s.strip.empty? || requested_model.to_s.strip == model
  abort "Codex model override is disabled." unless allow_model_override
  model = requested_model.to_s.strip
end
unless requested_effort.to_s.strip.empty? || requested_effort.to_s.strip == effort
  abort "Codex reasoning-effort override is disabled." unless allow_effort_override
  effort = requested_effort.to_s.strip
end
unless requested_verbosity.to_s.strip.empty? || requested_verbosity.to_s.strip == verbosity
  abort "Codex verbosity override is disabled." unless allow_verbosity_override
  verbosity = requested_verbosity.to_s.strip
end

approval = requested_approval.to_s.strip
approval = "never" if approval.empty?
allowed_approvals = Array(codex["approval_modes_allowed"]).map(&:to_s)
abort "Codex approval mode #{approval.inspect} is not allowed." unless allowed_approvals.include?(approval)

abort "Codex profile #{profile_name} has no model." if model.empty?
abort "Codex profile #{profile_name} has invalid model #{model.inspect}." unless model.match?(/\A[A-Za-z0-9][A-Za-z0-9._:-]*\z/)
abort "Codex profile #{profile_name} has invalid reasoning_effort #{effort.inspect}." unless %w[low medium high xhigh].include?(effort)
abort "Codex xhigh reasoning is disabled." if effort == "xhigh" && !allow_xhigh
abort "Codex profile #{profile_name} has invalid verbosity #{verbosity.inspect}." unless %w[low medium high].include?(verbosity)

puts [profile_name, model, effort, verbosity, approval].join("\t")
RUBY
}
