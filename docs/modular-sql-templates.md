# Modular SQL Templates

To battle the combinatoric explosion behind writing any possible
feature/label combination by hand,
the SQL-templating system allows to only write the SQL for each
feature and each label once, then combine everything arbitrarily.

## Adding a new template

New templates are stored in
[`rapp.resources.sqltemplates`](../rapp/resources/sqltemplates).
Features and labels are stored in the subdirectories `features` and `labels`,
respectively.

A new template is stored as a subdirectory to either `features` or `labels`
and contains up to three files:

1. `select.sql` (mandatory)
1. `join.sql` (optional)
1. `where.sql` (optional)

## Semantics of the template files

The template files for SELECT, JOIN, and WHERE
are put into a [mustache template](../rapp/resources/sqltemplates/skeleton.sql)
which has the following form

```sql
SELECT
-- Features
{{{feature_select}}},
-- Labels
{{{label_select}}}
FROM
  Student as S,
  Student_schreibt_Pruefung as SSP,
  Pruefung as P,
  Einschreibung as E
{{{feature_join}}}
{{{label_join}}}
WHERE
    S.Pseudonym = SSP.Pseudonym
AND S.Pseudonym = E.Pseudonym
AND SSP.Version = P.Version
AND SSP.Nummer = P.Nummer
{{{feature_where}}}
{{{label_where}}}
GROUP BY S.Pseudonym
```

As can be seen, `select.sql` needs to only contain the respective fields that
are queried.
`join.sql`, if exists, prepares any necessary joins from which the fields can
be combined.
`where.sql`, if exists, poses any necessary constraints onto the selected rows.

All SQL template files assume the presence of the four main tables:

```sql
Student as S,
Student_schreibt_Pruefung as SSP,
Pruefung as P,
Einschreibung as E
```

If no `join.sql` or `where.sql` is given for a specific template,
the mustache placeholder will be replaced with the empty string.

## Constructing an SQL query from the templates

Just follow the instructions on the code snippet below

```python
from rapp.sqlbuilder import load_sql

constructed_sql_query = load_sql(features_id=feature_template_id,
                                 labels_id=label_template_id)
```

The respective template IDs are the names of the template
subdirectories in either
`rapp.resources.sqltemplates.features`
or
`rapp.resources.sqltemplates.labels`.
