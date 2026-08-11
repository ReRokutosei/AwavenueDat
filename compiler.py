#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AWAvenue Geosite TXT -> Xray GeoSite DAT compiler.

This project is an independent converter for AWAvenue Ads Rule.
The upstream AWAvenue rule data remains subject to its own license.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    if value < 0:
        raise ValueError("Varint value cannot be negative.")

    result = bytearray()

    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7

    result.append(value)
    return bytes(result)


def encode_length_delimited(field_number: int, data: bytes) -> bytes:
    """Encode a protobuf length-delimited field."""
    tag = (field_number << 3) | 2

    return (
        encode_varint(tag)
        + encode_varint(len(data))
        + data
    )


def encode_domain(domain_type: int, value: str) -> bytes:
    """
    Encode a GeoSite Domain message.

    Field 1: type (varint)
    Field 2: value (string)
    """
    type_field = (
        encode_varint(1 << 3)
        + encode_varint(domain_type)
    )

    value_field = encode_length_delimited(
        2,
        value.encode("utf-8"),
    )

    return type_field + value_field


def parse_rule_line(line: str) -> tuple[int, str] | None:
    """
    Parse one V2Fly/Xray GeoSite rule.

    Types:
        0 = Substr / keyword
        1 = Regex
        2 = Domain
        3 = Full
    """
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line.startswith("full:"):
        return 3, line[5:]

    if line.startswith("regexp:"):
        return 1, line[7:]

    if line.startswith("regex:"):
        return 1, line[6:]

    if line.startswith("domain:"):
        return 2, line[7:]

    if line.startswith("keyword:"):
        return 0, line[8:]

    # Rules without an explicit prefix are treated as domains.
    return 2, line


def compile_geosite(
    input_path: Path,
    output_path: Path,
    code: str = "ADS",
) -> int:
    """
    Compile a GeoSite TXT file into a GeoSite DAT file.

    Returns the number of compiled rules.
    """
    domains = bytearray()
    count = 0

    with input_path.open(
        "r",
        encoding="utf-8-sig",
        newline=None,
    ) as file:
        for line in file:
            parsed = parse_rule_line(line)

            if parsed is None:
                continue

            domain_type, value = parsed

            if not value:
                continue

            domain_message = encode_domain(
                domain_type,
                value,
            )

            domains.extend(
                encode_length_delimited(
                    2,
                    domain_message,
                )
            )

            count += 1

    code_field = encode_length_delimited(
        1,
        code.upper().encode("utf-8"),
    )

    geosite_message = code_field + domains

    geosite_list_message = encode_length_delimited(
        1,
        geosite_message,
    )

    output_path.write_bytes(geosite_list_message)

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile AWAvenue GeoSite TXT rules into Xray DAT."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input GeoSite TXT file.",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Output GeoSite DAT file.",
    )

    parser.add_argument(
        "--code",
        default="ADS",
        help="GeoSite tag. Default: ADS",
    )

    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input file not found: {args.input}")

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    count = compile_geosite(
        args.input,
        args.output,
        args.code,
    )

    size = args.output.stat().st_size

    print(f"Compiled rules : {count}")
    print(f"Output file    : {args.output}")
    print(f"Output size    : {size:,} bytes")


if __name__ == "__main__":
    main()