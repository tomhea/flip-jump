# Catalog — Master Spec List

This file is the internal master list of catalog programs. Locked at the end
of Phase 2 (ideation). During Phase 3 it is the contract; rows are only added
when a `RETIRED` row is being replaced, and only at the end.

Number assignment is in (category-order, in-category-order) sequence — see
`CONVENTIONS.md`. Numbers are never recycled.

## Status

- **Phase 1 (Setup)**: this file is empty. Numbers will be assigned at the end of Phase 2.

## Row format

| # | category | name | description |
|---|---|---|---|

Each row is one program. The `description` column is the single source of
truth — it propagates verbatim to `README.md` and to the first description
line in the `.fj` header.

## Retired rows (Phase 3)

When a row cannot be implemented within budget and gets replaced, mark it
`RETIRED: <reason>` in the `description` column, and add the replacement at
the bottom of the table with the next free `#NNNN`.
