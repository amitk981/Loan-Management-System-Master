"""Deterministic PDF/XLSX adapters for frozen quarterly MIS snapshots."""

import io
import json
import zipfile
from xml.sax.saxutils import escape

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ROW_HEADINGS = (
    "Loan application number", "Borrower name", "Borrower type", "Loan status",
    "Disbursement date", "Sanctioned amount", "Disbursed amount", "Principal outstanding",
    "Revised principal", "Interest outstanding", "Quarter repayments", "Days past due",
    "DPD bucket", "Reminder count", "Last repayment date", "Interest invoice status",
    "Default status", "Recommended action", "Region", "Crop", "Security type",
)

def render_pdf(*, report, snapshot):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    output = io.BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4, invariant=1)
    lines = [
        f"SFPCL CFO Quarterly MIS - {report.financial_year} {report.quarter}",
        f"As of: {report.as_of_date.isoformat()} | Revision: {report.revision}",
        "TOTALS " + json.dumps(snapshot.totals_json, sort_keys=True),
        "AVAILABILITY " + json.dumps(snapshot.availability_json, sort_keys=True),
    ]
    y = 800
    for line in lines:
        for offset in range(0, len(line), 95):
            pdf.drawString(40, y, line[offset : offset + 95])
            y -= 14
    for row in snapshot.rows_json:
        line = "ROW " + json.dumps(row, sort_keys=True)
        for offset in range(0, len(line), 95):
            if y < 60:
                pdf.showPage()
                y = 800
            pdf.drawString(40, y, line[offset : offset + 95])
            y -= 14
    pdf.showPage()
    pdf.save()
    return output.getvalue()

def render_xlsx(*, report, snapshot):
    summary = [
        ("Financial year", report.financial_year),
        ("Quarter", report.quarter),
        ("As of date", report.as_of_date.isoformat()),
        ("Revision", report.revision),
        *[
            (f"total.{key}", json.dumps(value, sort_keys=True) if isinstance(value, dict) else value)
            for key, value in snapshot.totals_json.items()
        ],
        *[(f"availability.{key}", value) for key, value in snapshot.availability_json.items()],
        (),
        ROW_HEADINGS,
    ]
    rows = summary + [
        (
            row["loan_application_number"],
            row["borrower_name"],
            row["borrower_type"],
            row["loan_status"],
            row["disbursement_date"],
            row["sanctioned_amount"],
            row["disbursed_amount"],
            row["principal_outstanding_amount"],
            row["revised_principal_amount"],
            row["interest_outstanding_amount"],
            row["repayments_received_in_quarter"],
            row["days_past_due"],
            row["dpd_bucket"],
            row["reminder_count"],
            row["last_repayment_date"],
            row["interest_invoice_status"],
            row["default_status"],
            row["recommended_action"],
            row["region"],
            row["crop"],
            row["security_type"],
        )
        for row in snapshot.rows_json
    ]
    sheet_rows = []
    for row_number, row in enumerate(rows, start=1):
        cells = []
        for column_number, value in enumerate(row, start=1):
            reference = f"{_column_name(column_number)}{row_number}"
            cells.append(
                f'<c r="{reference}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("xl/workbook.xml", _WORKBOOK)
        archive.writestr("xl/_rels/workbook.xml.rels", _WORKBOOK_RELS)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return output.getvalue()

def _column_name(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
_ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
_WORKBOOK = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Quarterly MIS" sheetId="1" r:id="rId1"/></sheets></workbook>"""
_WORKBOOK_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
