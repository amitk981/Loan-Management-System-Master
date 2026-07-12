# Dependency Scan

`rg` confirms `MemberRegistry` is referenced inside `members/` only by the HTTP view adapter and the
module export. Generic `members.services` no longer imports the Registry. No new package or Python
dependency was added, and migration sync reports no changes.
