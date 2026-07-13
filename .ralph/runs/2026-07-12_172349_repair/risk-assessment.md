# Risk Assessment — 006Y9 Trusted-Browser Contract Repair

Risk level: High, inherited from the real-session protected-identity acceptance slice.

This repair changes only the selected slice's machine-readable browser declaration. It corrects the
spec from repository-relative to project-relative form, declares the four required screenshot
basenames, and moves descriptive prose outside the strict section. Production code, browser test
logic, APIs, permissions, persistence, dependencies, source material, and visual styles are unchanged.

The remaining High-risk control is independent execution of the real member writes and protected
identity maker-checker flow. The orchestrator must run the exact scenario twice and verify all four
non-empty screenshots before committing. No screenshot was fabricated, and no protected or forbidden
path was modified. The repair remains below Ralph's diff limits.
