# Data

The invoice register is proprietary to the client and held in confidence. **No data is included in this repository**, and `.gitignore` excludes everything in this folder except this file.

## Expected layout

```
data/
├── raw/invoice_register.parquet          ← raw register, used only for the provenance check in notebook 01
├── processed/sales_clean.parquet         ← cleaned register, 94,872 lines (input to notebook 01)
├── processed/sales_scoped.parquet        ← written by notebook 01
├── lookup/book_master.csv                ← written by notebook 01, one row per ISBN
├── lookup/analysis_filters.json          ← written by notebook 01, the filter contract
└── lookup/confidential_labels.json       ← named series exclusions and case-study keys (client-confidential)
```

## Key columns in `sales_clean.parquet`

| Column | Meaning |
|---|---|
| `date`, `ym` | invoice date; year-month period |
| `Invoice/CM #`, `doc_type` | document number and type (invoice, credit note, delivery order…) |
| `Item ID`, `Item Description` | product code and hand-typed description |
| `isbn_key` | normalised ISBN, the title grain |
| `Customer ID` | customer code (`Name` exists but is never read by the analysis) |
| `Qty`, `Unit Price`, `Amount` | units, price and line value (SGD, GST-exclusive) |
| `FOC` | free-of-charge marker (presence only) |
| `Type` | format as invoiced (Paperback, eBook, services and others) |
| `Channel` | publishing arm |
| `genre_std`, `sub_category`, `subcat_family` | standardised genre vocabulary from the masterlist |
| `culture_pass` | title eligible for the Culture Pass scheme |
| `client_excluded` | advance-order lines the client asked to exclude |
| `is_return`, `is_foc`, `is_credit_adj`, `key_source` | flags derived during cleaning |

Notebook 01 adds `book_scope`, `scope_reason`, `line_role`, `amt_sign`, `qty_sign` and `has_genre`.
