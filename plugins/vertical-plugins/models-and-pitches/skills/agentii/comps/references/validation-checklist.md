# Validation Checklist

- [ ] Every input figure cites a filing page or XBRL accession.
- [ ] Recalc/audit returns no hardcoded-over-formula cells.
- [ ] Statement identities balance within rounding.
- [ ] Period labels match `resolve_period`'s fiscal reading; `comparison_basis` is stated and never mixed.
- [ ] Coverage gaps are surfaced, not silently dropped.
