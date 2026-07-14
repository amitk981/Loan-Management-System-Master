import hashlib
import io
import os
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from xml.etree import ElementTree

from django.core.exceptions import ValidationError


WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
RELATIONSHIP_NAMESPACE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
)
_TEXT_TAG = f"{{{WORD_NAMESPACE}}}t"
_PARAGRAPH_TAG = f"{{{WORD_NAMESPACE}}}p"
_PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Za-z][A-Za-z0-9_]*)\s*}}")

MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 256
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_ARCHIVE_ENTRY_BYTES = 8 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
MAX_XML_BYTES = 4 * 1024 * 1024
MAX_TEXT_CHARS = 1 * 1024 * 1024
MAX_PLACEHOLDERS = 200
MAX_REPLACEMENT_BYTES = 16 * 1024
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
MAX_PDF_PAGES = 100

ElementTree.register_namespace("w", WORD_NAMESPACE)
ElementTree.register_namespace("r", RELATIONSHIP_NAMESPACE)


@dataclass(frozen=True)
class RenderedDocument:
    content: bytes
    mime_type: str
    extracted_text: str
    page_count: int | None


def render(*, template_bytes, merge_values, output_format):
    if len(template_bytes) > MAX_SOURCE_BYTES:
        raise ValidationError({"template_file_id": "Template source exceeds the size limit."})
    for field, value in merge_values.items():
        if len(str(value).encode("utf-8")) > MAX_REPLACEMENT_BYTES:
            raise ValidationError({field: "Merge replacement exceeds the size limit."})
    merged_docx, extracted_text = _merge_word_package(template_bytes, merge_values)
    _validate_output_size(merged_docx)
    if output_format == "docx":
        return RenderedDocument(
            content=merged_docx,
            mime_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            extracted_text=extracted_text,
            page_count=None,
        )
    if output_format == "pdf":
        pdf_content, pdf_text, page_count = _convert_to_pdf(merged_docx, merge_values)
        _validate_output_size(pdf_content)
        if page_count > MAX_PDF_PAGES:
            raise ValidationError({"output_format": "Rendered PDF exceeds the page limit."})
        return RenderedDocument(
            content=pdf_content,
            mime_type="application/pdf",
            extracted_text=pdf_text,
            page_count=page_count,
        )
    raise ValidationError({"output_format": "Output format is not supported."})


def _merge_word_package(template_bytes, merge_values):
    source = io.BytesIO(template_bytes)
    if not zipfile.is_zipfile(source):
        raise ValidationError(
            {"template_file_id": "Template source must be a genuine DOCX package."}
        )
    source.seek(0)
    output = io.BytesIO()
    replacements = {field: 0 for field in merge_values}
    extracted_parts = []
    try:
        with zipfile.ZipFile(source) as input_archive, zipfile.ZipFile(
            output, "w", zipfile.ZIP_DEFLATED
        ) as output_archive:
            infos = input_archive.infolist()
            _validate_archive(infos)
            names = [info.filename for info in infos]
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValidationError(
                    {"template_file_id": "Word template package is missing required parts."}
                )
            placeholder_counts = Counter()
            xml_bytes = 0
            text_chars = 0
            for name in names:
                content = input_archive.read(name)
                if name.startswith("word/") and name.endswith(".xml"):
                    xml_bytes += len(content)
                    if xml_bytes > MAX_XML_BYTES:
                        raise ValidationError(
                            {"template_file_id": "Template XML exceeds the size limit."}
                        )
                    content, part_replacements, part_placeholders, part_text = _merge_xml_part(
                        content, merge_values
                    )
                    placeholder_counts.update(part_placeholders)
                    for field, count in part_replacements.items():
                        replacements[field] += count
                    if part_text:
                        text_chars += len(part_text)
                        if text_chars > MAX_TEXT_CHARS:
                            raise ValidationError(
                                {"template_file_id": "Template text exceeds the size limit."}
                            )
                        extracted_parts.append(part_text)
                output_archive.writestr(name, content)
    except (zipfile.BadZipFile, ElementTree.ParseError, UnicodeError) as exc:
        raise ValidationError(
            {"template_file_id": "Template source is not a readable DOCX package."}
        ) from exc

    if sum(placeholder_counts.values()) > MAX_PLACEHOLDERS:
        raise ValidationError(
            {"template_file_id": "Template exceeds the placeholder limit."}
        )
    undeclared = sorted(set(placeholder_counts) - set(merge_values))
    if undeclared:
        raise ValidationError(
            {
                "template_file_id": (
                    "Template contains undeclared placeholders: " + ", ".join(undeclared)
                )
            }
        )
    duplicates = {
        field: "Template contains a duplicate placeholder."
        for field, count in placeholder_counts.items()
        if count > 1
    }
    if duplicates:
        raise ValidationError(duplicates)
    missing = {
        field: "Declared merge field is absent from the retained Word template."
        for field, count in replacements.items()
        if count == 0
    }
    if missing:
        raise ValidationError(missing)
    return output.getvalue(), "\n".join(extracted_parts)


def _merge_xml_part(content, merge_values):
    root = ElementTree.fromstring(content)
    replacements = {field: 0 for field in merge_values}
    placeholders = Counter()
    for paragraph in root.iter(_PARAGRAPH_TAG):
        text_nodes = list(paragraph.iter(_TEXT_TAG))
        if not text_nodes:
            continue
        original = "".join(node.text or "" for node in text_nodes)
        matches = list(_PLACEHOLDER_PATTERN.finditer(original))
        placeholders.update(match.group(1) for match in matches)
        unmatched_markup = _PLACEHOLDER_PATTERN.sub("", original)
        if "{{" in unmatched_markup or "}}" in unmatched_markup:
            raise ValidationError(
                {"template_file_id": "Template contains a malformed placeholder."}
            )
        merged = original
        for field, value in merge_values.items():
            pattern = re.compile(r"{{\s*" + re.escape(field) + r"\s*}}")
            merged, count = pattern.subn(lambda _match, value=str(value): value, merged)
            replacements[field] += count
        if merged != original:
            text_nodes[0].text = merged
            for node in text_nodes[1:]:
                node.text = ""
    text = " ".join(node.text or "" for node in root.iter(_TEXT_TAG))
    return (
        ElementTree.tostring(root, encoding="utf-8", xml_declaration=True),
        replacements,
        placeholders,
        text,
    )


def _validate_archive(infos):
    if len(infos) > MAX_ARCHIVE_ENTRIES:
        raise ValidationError({"template_file_id": "Template has too many archive entries."})
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        raise ValidationError({"template_file_id": "Template has duplicate archive entries."})
    expanded = 0
    for info in infos:
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
            raise ValidationError({"template_file_id": "Template has an unsafe archive path."})
        if info.flag_bits & 0x1:
            raise ValidationError({"template_file_id": "Encrypted templates are not supported."})
        if info.file_size > MAX_ARCHIVE_ENTRY_BYTES:
            raise ValidationError({"template_file_id": "Template archive entry is too large."})
        expanded += info.file_size
        if expanded > MAX_EXPANDED_BYTES:
            raise ValidationError({"template_file_id": "Template expands beyond the size limit."})
        if info.file_size and (
            not info.compress_size
            or info.file_size / info.compress_size > MAX_COMPRESSION_RATIO
        ):
            raise ValidationError(
                {"template_file_id": "Template archive compression ratio is unsafe."}
            )


def _validate_output_size(content):
    if not content or len(content) > MAX_OUTPUT_BYTES:
        raise ValidationError({"output_format": "Rendered output size is invalid."})


def _convert_to_pdf(merged_docx, merge_values):
    try:
        from pypdf import PdfReader
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        from xml.sax.saxutils import escape
    except ImportError as exc:
        raise ValidationError(
            {"output_format": "Pinned PDF renderer dependencies are unavailable."}
        ) from exc

    fonts = _register_unicode_fonts(pdfmetrics=pdfmetrics, font_class=TTFont)
    font_name = fonts[0].fontName
    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="SFPCL retained legal document",
        author="SFPCL",
        pageCompression=1,
    )
    style = ParagraphStyle(
        "SFPCLLegalBody",
        fontName=font_name,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        shaping=True,
        splitLongWords=True,
        allowWidows=0,
        allowOrphans=0,
    )
    story = []
    for line in (line.strip() for line in _docx_text_lines(merged_docx)):
        if not line:
            continue
        story.extend(
            (
                Paragraph(_pdf_markup(line, fonts=fonts, escape=escape), style),
                Spacer(1, 2 * mm),
            )
        )
    if not story:
        raise ValidationError(
            {"template_file_id": "Word template has no readable legal content."}
        )
    document.build(story)
    pdf_content = output.getvalue()
    try:
        reader = PdfReader(io.BytesIO(pdf_content), strict=True)
        text = "\n".join(
            page.extract_text(extraction_mode="layout") or "" for page in reader.pages
        )
    except Exception as exc:
        raise ValidationError(
            {"output_format": "Rendered PDF output is not structurally readable."}
        ) from exc
    normalized_pdf_text = " ".join(text.split())
    missing_values = [
        field
        for field, value in merge_values.items()
        if " ".join(str(value).split()) not in normalized_pdf_text
    ]
    if missing_values:
        raise ValidationError(
            {
                field: "Merged authoritative text is not readable in the rendered PDF."
                for field in missing_values
            }
        )
    return pdf_content, text, len(reader.pages)


def _register_unicode_fonts(*, pdfmetrics, font_class):
    configured = os.environ.get("LEGAL_DOCUMENT_PDF_FONT_PATH")
    candidates = [
        configured,
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc",
    ]
    fonts = []
    seen = set()
    for candidate in candidates:
        if not candidate or not os.path.isfile(candidate):
            continue
        real_path = os.path.realpath(candidate)
        if real_path in seen:
            continue
        seen.add(real_path)
        font_name = (
            "SFPCLLegalUnicode"
            + hashlib.sha256(real_path.encode("utf-8")).hexdigest()[:12]
        )
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(font_class(font_name, real_path))
        fonts.append(pdfmetrics.getFont(font_name))
    if not fonts:
        raise ValidationError(
            {
                "output_format": (
                    "A Unicode TrueType font is required; configure "
                    "LEGAL_DOCUMENT_PDF_FONT_PATH."
                )
            }
        )
    return fonts


def _pdf_markup(line, *, fonts, escape):
    primary_font = fonts[0]
    markup = []
    for token in re.split(r"(\s+)", line):
        if not token:
            continue
        if token.isspace():
            markup.append(escape(token))
            continue
        font = next(
            (
                candidate
                for candidate in fonts
                if all(ord(character) in candidate.face.charToGlyph for character in token)
            ),
            None,
        )
        if font is None:
            raise ValidationError(
                {
                    "output_format": (
                        "Configured Unicode fonts do not cover the retained legal text."
                    )
                }
            )
        escaped = escape(token)
        if font is primary_font:
            markup.append(escaped)
        else:
            markup.append(f'<font name="{font.fontName}">{escaped}</font>')
    return "".join(markup)


def _docx_text_lines(content):
    lines = []
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for name in archive.namelist():
            if name == "word/document.xml" or name.startswith(
                ("word/header", "word/footer")
            ):
                root = ElementTree.fromstring(archive.read(name))
                for paragraph in root.iter(_PARAGRAPH_TAG):
                    lines.append("".join(node.text or "" for node in paragraph.iter(_TEXT_TAG)))
    return lines
