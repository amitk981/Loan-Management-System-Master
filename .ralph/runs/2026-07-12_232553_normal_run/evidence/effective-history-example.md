# Effective History Example

First verification creates record A with `effective_from = as_of_date`, `effective_to = null`, and
sets `Member.active_member_status_id = A`. A later decision locks the Member, closes A at one day
before the later as-of date, creates record B as the sole current row, and points the Member to B.
The unique current-record constraint prevents two null `effective_to` rows. Prior evidence snapshots
are never updated. The two PostgreSQL race logs prove one winner and zero loser history/audit rows.
