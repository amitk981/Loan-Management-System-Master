#!/usr/bin/env bash

ralph_trusted_browser_acceptance_entries() {
  local slice_file="${1:?slice file is required}"

  awk '
    $0 == "## Trusted Browser Acceptance" { in_acceptance = 1; next }
    in_acceptance && /^## / { exit }
    in_acceptance {
      line = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      gsub(/`/, "", line)
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (length(line) > 0) print line
    }
  ' "$slice_file"
}

ralph_trusted_e2e_specs() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Spec: "*) printf '%s\n' "${entry#Spec: }" ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")
}

ralph_trusted_e2e_screenshots() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Screenshot: "*) printf '%s\n' "${entry#Screenshot: }" ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")
}

ralph_validate_trusted_browser_acceptance() {
  local slice_file="${1:?slice file is required}"
  local project_dir="${2:?project directory is required}"
  local entry=""
  local value=""
  local spec_count=0
  local screenshot_count=0
  local seen_specs=""
  local seen_screenshots=""
  local problem_count=0

  while IFS= read -r entry; do
    case "$entry" in
      "Spec: "*)
        value="${entry#Spec: }"
        if [[ ! "$value" =~ ^e2e/[A-Za-z0-9._/-]+\.spec\.ts$ \
              || "$value" == *".."* \
              || "$value" == *"//"* ]]; then
          echo "Invalid trusted browser spec path '$value' in $slice_file; use a relative e2e/*.spec.ts path." >&2
          problem_count=$((problem_count + 1))
        elif [[ ! -f "$project_dir/$value" ]]; then
          echo "Trusted browser spec '$value' does not exist under $project_dir." >&2
          problem_count=$((problem_count + 1))
        elif printf '%s\n' "$seen_specs" | grep -Fxq "$value"; then
          echo "Duplicate trusted browser spec '$value' in $slice_file." >&2
          problem_count=$((problem_count + 1))
        else
          spec_count=$((spec_count + 1))
          seen_specs="${seen_specs}${seen_specs:+$'\n'}${value}"
        fi
        ;;
      "Screenshot: "*)
        value="${entry#Screenshot: }"
        if [[ ! "$value" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*\.png$ ]]; then
          echo "Invalid trusted browser screenshot '$value' in $slice_file; use a PNG basename only." >&2
          problem_count=$((problem_count + 1))
        elif printf '%s\n' "$seen_screenshots" | grep -Fxq "$value"; then
          echo "Duplicate trusted browser screenshot '$value' in $slice_file." >&2
          problem_count=$((problem_count + 1))
        else
          screenshot_count=$((screenshot_count + 1))
          seen_screenshots="${seen_screenshots}${seen_screenshots:+$'\n'}${value}"
        fi
        ;;
      *)
        echo "Unknown trusted browser acceptance entry '$entry' in $slice_file." >&2
        problem_count=$((problem_count + 1))
        ;;
    esac
  done < <(ralph_trusted_browser_acceptance_entries "$slice_file")

  if (( spec_count == 0 )); then
    echo "Slice $slice_file declares localhost-e2e-server but no valid trusted browser Spec entry." >&2
    problem_count=$((problem_count + 1))
  fi
  if (( screenshot_count == 0 )); then
    echo "Slice $slice_file declares localhost-e2e-server but no valid trusted browser Screenshot entry." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
}

ralph_validate_png_file() {
  local screenshot_path="${1:?screenshot path is required}"
  python3 - "$screenshot_path" <<'PY'
import struct
import sys
import zlib
from pathlib import Path


def reject(message: str) -> None:
    raise SystemExit(f"invalid PNG: {message}")


path = Path(sys.argv[1])
try:
    data = path.read_bytes()
except OSError as error:
    reject(str(error))

signature = b"\x89PNG\r\n\x1a\n"
if not data.startswith(signature):
    reject("signature mismatch")

offset = len(signature)
chunk_index = 0
ihdr = None
idat_parts = []
seen_plte = False
seen_idat = False
idat_closed = False
seen_iend = False
known_critical = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}

while offset < len(data):
    if seen_iend:
        reject("trailing bytes after IEND")
    if offset + 12 > len(data):
        reject("truncated chunk header")
    length = struct.unpack(">I", data[offset:offset + 4])[0]
    kind = data[offset + 4:offset + 8]
    end = offset + 12 + length
    if end > len(data):
        reject("truncated chunk payload")
    if not all(65 <= value <= 90 or 97 <= value <= 122 for value in kind):
        reject("invalid chunk type")
    payload = data[offset + 8:offset + 8 + length]
    stored_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
    actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    if stored_crc != actual_crc:
        reject(f"CRC mismatch in {kind.decode('ascii', errors='replace')}")
    if chunk_index == 0 and kind != b"IHDR":
        reject("IHDR is not first")
    if kind[0] & 0x20 == 0 and kind not in known_critical:
        reject("unknown critical chunk")

    if kind == b"IHDR":
        if chunk_index != 0 or ihdr is not None or length != 13:
            reject("invalid or duplicate IHDR")
        ihdr = struct.unpack(">IIBBBBB", payload)
    elif kind == b"PLTE":
        if ihdr is None or seen_idat or seen_plte or length == 0 or length % 3 != 0:
            reject("invalid PLTE")
        seen_plte = True
    elif kind == b"IDAT":
        if ihdr is None or idat_closed:
            reject("non-consecutive or premature IDAT")
        seen_idat = True
        idat_parts.append(payload)
    else:
        if seen_idat:
            idat_closed = True
        if kind == b"IEND":
            if length != 0 or not seen_idat:
                reject("invalid IEND")
            seen_iend = True
            if end != len(data):
                reject("trailing bytes after IEND")

    offset = end
    chunk_index += 1

if ihdr is None or not seen_idat or not seen_iend:
    reject("missing IHDR, IDAT, or IEND")

width, height, bit_depth, color_type, compression, filter_method, interlace = ihdr
valid_depths = {
    0: {1, 2, 4, 8, 16},
    2: {8, 16},
    3: {1, 2, 4, 8},
    4: {8, 16},
    6: {8, 16},
}
channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
if not (1 <= width <= 32768 and 1 <= height <= 32768):
    reject("invalid dimensions")
if width * height > 50_000_000:
    reject("pixel count exceeds evidence limit")
if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
    reject("invalid color type/bit depth")
if compression != 0 or filter_method != 0 or interlace not in (0, 1):
    reject("unsupported compression, filter, or interlace method")
if color_type == 3 and not seen_plte:
    reject("indexed image has no palette")

passes = [(0, 0, 1, 1)] if interlace == 0 else [
    (0, 0, 8, 8),
    (4, 0, 8, 8),
    (0, 4, 4, 8),
    (2, 0, 4, 4),
    (0, 2, 2, 4),
    (1, 0, 2, 2),
    (0, 1, 1, 2),
]
row_layout = []
expected_size = 0
for x_start, y_start, x_step, y_step in passes:
    pass_width = 0 if width <= x_start else (width - x_start + x_step - 1) // x_step
    pass_height = 0 if height <= y_start else (height - y_start + y_step - 1) // y_step
    if pass_width == 0 or pass_height == 0:
        continue
    row_bytes = (pass_width * channels[color_type] * bit_depth + 7) // 8
    row_layout.append((pass_height, row_bytes))
    expected_size += pass_height * (1 + row_bytes)
if expected_size <= 0 or expected_size > 256 * 1024 * 1024:
    reject("decoded image size exceeds evidence limit")

decoder = zlib.decompressobj()
try:
    raw = decoder.decompress(b"".join(idat_parts), expected_size + 1)
    if decoder.unconsumed_tail:
        reject("decoded data exceeds declared dimensions")
    raw += decoder.flush()
except zlib.error as error:
    reject(f"IDAT decompression failed: {error}")
if not decoder.eof or decoder.unused_data or len(raw) != expected_size:
    reject("IDAT stream does not match declared dimensions")

position = 0
for row_count, row_bytes in row_layout:
    for _ in range(row_count):
        if raw[position] > 4:
            reject("invalid row filter")
        position += 1 + row_bytes
if position != len(raw):
    reject("decoded row layout mismatch")
PY
}

ralph_write_trusted_browser_screenshot_manifest() {
  local slice_file="${1:?slice file is required}"
  local evidence_dir="${2:?browser evidence directory is required}"
  local manifest_file="${3:?screenshot manifest path is required}"
  local screenshot=""
  local screenshot_path=""
  local hash=""
  local screenshot_count=0
  local problem_count=0
  local manifest_tmp="${manifest_file}.tmp.$$"

  mkdir -p "$(dirname "$manifest_file")"
  : > "$manifest_tmp"

  while IFS= read -r screenshot; do
    [[ -n "$screenshot" ]] || continue
    screenshot_count=$((screenshot_count + 1))
    screenshot_path="$evidence_dir/$screenshot"
    if [[ -L "$screenshot_path" || ! -f "$screenshot_path" || ! -s "$screenshot_path" ]]; then
      echo "Missing, empty, or symlinked trusted browser screenshot for this run: $screenshot_path" >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    if ! ralph_validate_png_file "$screenshot_path"; then
      echo "Trusted browser evidence is not a structurally valid decodable PNG: $screenshot_path" >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    if command -v shasum >/dev/null 2>&1; then
      hash="$(shasum -a 256 "$screenshot_path" | awk '{print $1}')"
    elif command -v sha256sum >/dev/null 2>&1; then
      hash="$(sha256sum "$screenshot_path" | awk '{print $1}')"
    else
      echo "Neither shasum nor sha256sum is available for screenshot evidence." >&2
      problem_count=$((problem_count + 1))
      continue
    fi
    printf '%s  %s\n' "$hash" "$screenshot" >> "$manifest_tmp"
  done < <(ralph_trusted_e2e_screenshots "$slice_file")

  if (( screenshot_count == 0 )); then
    echo "No trusted browser screenshots were declared for $slice_file." >&2
    problem_count=$((problem_count + 1))
  fi
  if (( problem_count > 0 )); then
    rm -f "$manifest_tmp"
    return 1
  fi
  mv "$manifest_tmp" "$manifest_file"
}
