# Quick Start

## 1. Prepare the free tool

Download or clone:

https://github.com/Ika300/so-memory-kernel

## 2. Prepare your CSV

Use:

`templates/rag_trace_template.csv`

Minimum required columns:

- query_id
- query_text
- rank
- document_id
- chunk_id
- retrieved_text
- score

Optional columns:

- answer_used
- source_system
- notes

## 3. Run the analyzer

From the `so-memory-kernel` folder:

```bash
python tools/rag_trace_analyzer/rag_trace_analyzer.py path/to/your_trace.csv --out report.md --html report.html
```

## 4. Read the output

Use:

`guides/how_to_read_reports.md`

Focus on:

- repeated same-source evidence
- independent document evidence
- noisy retrieval
- weak or missing support
- answer risk

## 5. Create a client-facing report

Use:

`report_templates/client_report_template.md`

Keep client data local.
Do not paste confidential text into external AI tools unless the client explicitly approves it.
