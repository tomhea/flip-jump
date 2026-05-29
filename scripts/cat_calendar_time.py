"""Phase 3: calendar_time category — date/time arithmetic and formatting.

Implements 20 of the 22 APPROVED calendar_time programs (#0847-#0868). Each is a
small read-decimal / read-fixed-field + branch + bit.div/bit.add transform:
leap-year and days-in-month tables, Zeller's-congruence day-of-week (weekend,
business days, day-of-week-from-date), day-of-year both directions, an
epoch-2000 day counter both directions, HMS<->seconds, 12h<->24h time
formatting, ISO date format/validate, month-abbreviation lookup, quarter, and
time-of-day period.

Two specs are DEFERRED because their CATALOG description contains a non-ASCII
character (the convention forbids editing the shared catalog_desc matcher to
accommodate them, and emit byte-matches the .fj header against CATALOG.md):
  * #0851 dec_year_2digit_to_4digit   — desc has `->` rendered as a non-ASCII arrow
  * #0861 days_between_dates_same_year — desc has a non-ASCII `>=`

Run from the repo root:  python scripts/cat_calendar_time.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog_arith import emit  # noqa: E402


def _collapse_def_headers(text: str) -> str:
    """Join multi-line `def ...` headers onto one line.

    FlipJump's parser requires a macro's `def name @ labels < data {` header to
    sit on a single physical line. We author the long ones across several Python
    source lines (to respect flake8's 120-col limit) and fold them back here.
    """
    out: list[str] = []
    lines = text.split("\n")
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if line.lstrip().startswith("def ") and "{" not in line:
            parts = [line.rstrip()]
            idx += 1
            while idx < len(lines) and "{" not in lines[idx]:
                parts.append(lines[idx].strip())
                idx += 1
            if idx < len(lines):
                parts.append(lines[idx].strip())
            out.append(" ".join(parts))
        else:
            out.append(line)
        idx += 1
    return "\n".join(out)


def C(nnnn, slug, name, *, main_body, extra_helpers=None, **kw):
    main_body = _collapse_def_headers(main_body)
    if extra_helpers:
        extra_helpers = [_collapse_def_headers(h) for h in extra_helpers]
    emit("calendar_time", nnnn, slug, name, main_body=main_body, extra_helpers=extra_helpers, **kw)


# ---------------------------------------------------------------------------
# Shared helper macros (passed via extra_helpers) and their data (extra_data).
# Every global is uniquely named (never n/i/w/dw/dbit) and listed in `<`.
# `sep` is a scratch byte for swallowing fixed separators ('-', ':', ' ', '\n').
# ---------------------------------------------------------------------------

SEP_DATA = ["sep: bit.vec 8, 0"]

# flag[:1] = 1 if year[:16] is a Gregorian leap year, else 0.
IS_LEAP_INTO = """
// flag[:1] = 1 if year[:16] is a Gregorian leap year, else 0.
def is_leap_into flag, year @ chk100, chk400, yes, no, done < ly_four, ly_hundred, ly_400, ly_q, ly_r {
    bit.div 16, year, ly_four, ly_q, ly_r
    bit.if1 16, ly_r, no
  chk100:
    bit.div 16, year, ly_hundred, ly_q, ly_r
    bit.if1 16, ly_r, yes
  chk400:
    bit.div 16, year, ly_400, ly_q, ly_r
    bit.if0 16, ly_r, yes
    ;no
  yes:
    bit.one flag
    ;done
  no:
    bit.zero flag
  done:
}
""".strip()

IS_LEAP_DATA = [
    "ly_four: bit.vec 16, 4",
    "ly_hundred: bit.vec 16, 100",
    "ly_400: bit.vec 16, 400",
    "ly_q: bit.vec 16, 0",
    "ly_r: bit.vec 16, 0",
]

# dst[:16] = number of days in (year, month); month assumed 1-12.
DAYS_IN_MONTH_INTO = """
// dst[:16] = number of days in (year[:16], month[:16]); month assumed 1-12.
def days_in_month_into dst, year, month
        @ feb, short, leap_feb, done, t2, t4, t6, t9, t11
        < dim_m2, dim_m4, dim_m6, dim_m9, dim_m11, dim_28, dim_29, dim_30, dim_31, dim_leap {
    bit.cmp 16, month, dim_m2, t2, feb, t2
  t2:
    bit.cmp 16, month, dim_m4, t4, short, t4
  t4:
    bit.cmp 16, month, dim_m6, t6, short, t6
  t6:
    bit.cmp 16, month, dim_m9, t9, short, t9
  t9:
    bit.cmp 16, month, dim_m11, t11, short, t11
  t11:
    bit.mov 16, dst, dim_31
    ;done
  short:
    bit.mov 16, dst, dim_30
    ;done
  feb:
    is_leap_into dim_leap, year
    bit.if1 dim_leap, leap_feb
    bit.mov 16, dst, dim_28
    ;done
  leap_feb:
    bit.mov 16, dst, dim_29
  done:
}
""".strip()

DAYS_IN_MONTH_DATA = IS_LEAP_DATA + [
    "dim_m2: bit.vec 16, 2",
    "dim_m4: bit.vec 16, 4",
    "dim_m6: bit.vec 16, 6",
    "dim_m9: bit.vec 16, 9",
    "dim_m11: bit.vec 16, 11",
    "dim_28: bit.vec 16, 28",
    "dim_29: bit.vec 16, 29",
    "dim_30: bit.vec 16, 30",
    "dim_31: bit.vec 16, 31",
    "dim_leap: bit.bit",
]

# Print value[:16] (assumed 0-99) as exactly two decimal digits (zero-padded).
PRINT_TWO_DIGITS = """
// Print value[:16] (assumed 0-99) as exactly two decimal digits (zero-padded).
def print_two_digits value < td_q, td_r, td_ten, td_hi, td_lo, td_off0 {
    bit.div 16, value, td_ten, td_q, td_r
    bit.zero 8, td_hi
    bit.mov 4, td_hi, td_q
    bit.add 8, td_hi, td_off0
    bit.print td_hi
    bit.zero 8, td_lo
    bit.mov 4, td_lo, td_r
    bit.add 8, td_lo, td_off0
    bit.print td_lo
}
""".strip()

PRINT_TWO_DIGITS_DATA = [
    "td_q: bit.vec 16, 0",
    "td_r: bit.vec 16, 0",
    "td_ten: bit.vec 16, 10",
    "td_hi: bit.vec 8, 0",
    "td_lo: bit.vec 8, 0",
    "td_off0: bit.vec 8, 0x30",
]

# acc[:16] += floor((a[:16] * b[:16]) / c[:16]); a*b by repeated addition (small).
# acc[:16] += floor(a[:16] / c[:16]).
ADD_MUL_HELPERS = """
// acc[:16] += floor((a[:16] * b[:16]) / c[:16]); a*b via repeated addition.
def add_mul acc, a, b, c @ loop, end < am_prod, am_ctr, am_q, am_r {
    bit.zero 16, am_prod
    bit.mov 16, am_ctr, b
  loop:
    bit.if0 16, am_ctr, end
    bit.add 16, am_prod, a
    bit.dec 16, am_ctr
    ;loop
  end:
    bit.div 16, am_prod, c, am_q, am_r
    bit.add 16, acc, am_q
}

// acc[:16] += floor(a[:16] / c[:16]).
def div_add acc, a, c < da_q, da_r {
    bit.div 16, a, c, da_q, da_r
    bit.add 16, acc, da_q
}
""".strip()

ADD_MUL_DATA = [
    "am_prod: bit.vec 16, 0",
    "am_ctr: bit.vec 16, 0",
    "am_q: bit.vec 16, 0",
    "am_r: bit.vec 16, 0",
    "da_q: bit.vec 16, 0",
    "da_r: bit.vec 16, 0",
]

# acc[:24] += addend[:24] added `times[:24]` times (24-bit repeated-addition
# multiply; `times` is small, e.g. an hour or minute count).
ADD_TIMES_24 = """
// acc[:24] += addend[:24], repeated `times[:24]` times (times is small).
def add_times24 acc, addend, times @ loop, end < at_ctr {
    bit.mov 24, at_ctr, times
  loop:
    bit.if0 24, at_ctr, end
    bit.add 24, acc, addend
    bit.dec 24, at_ctr
    ;loop
  end:
}
""".strip()

ADD_TIMES_24_DATA = ["at_ctr: bit.vec 24, 0"]

# Read an unsigned decimal (digits until \n or \0) into value[:24]. Self-
# contained 24-bit reader (the shared read_decimal's `digit` scratch is 16-bit,
# so it cannot be called at width 24).
READ_DECIMAL_24 = """
// Read an unsigned decimal (digits until `\\n` or `\\0`) into value[:24].
def read_decimal24 value @ loop, add_digit, end < rd_ch, rd_nl, rd_digit, rd_err {
    bit.zero 24, value
  loop:
    bit.input rd_ch
    bit.if0 8, rd_ch, end
    bit.cmp 8, rd_ch, rd_nl, add_digit, end, add_digit
  add_digit:
    bit.mul10 24, value
    bit.zero 24, rd_digit
    bit.ascii2dec rd_err, rd_digit, rd_ch
    bit.add 24, value, rd_digit
    ;loop
  end:
}
""".strip()

READ_DECIMAL_24_DATA = [
    "rd_ch: bit.vec 8, 0",
    "rd_nl: bit.vec 8, '\\n'",
    "rd_digit: bit.vec 24, 0",
    "rd_err: bit.bit",
]

# dow[:16] = day-of-week of (year, month, day) with Sunday=0, via Zeller's
# congruence. Zeller yields h with 0=Saturday; we compute (h+6) mod 7 to remap
# to Sunday=0 .. Saturday=6. Jan/Feb are treated as months 13/14 of prior year.
ZELLER_INTO = """
// dow[:16] = day-of-week of (year[:16], month[:16], day[:16]); Sunday=0 (Zeller).
def zeller_into dow, year, month, day
        @ shift, no_shift
        < z_y, z_m, z_d, z_one, z_three, z_four, z_five, z_seven, z_12, z_13, z_100,
          z_K, z_J, z_term, z_q, z_r, z_acc {
    bit.mov 16, z_y, year
    bit.mov 16, z_m, month
    bit.mov 16, z_d, day
    bit.cmp 16, z_m, z_three, shift, no_shift, no_shift
  shift:
    bit.add 16, z_m, z_12
    bit.dec 16, z_y
  no_shift:
    bit.div 16, z_y, z_100, z_J, z_K
    bit.mov 16, z_acc, z_d
    bit.mov 16, z_term, z_m
    bit.add 16, z_term, z_one
    bit.mov 16, z_q, z_13
    add_mul z_acc, z_q, z_term, z_five
    bit.add 16, z_acc, z_K
    bit.mov 16, z_q, z_K
    div_add z_acc, z_q, z_four
    bit.mov 16, z_q, z_J
    div_add z_acc, z_q, z_four
    bit.mov 16, z_q, z_J
    add_mul z_acc, z_q, z_five, z_one
    bit.div 16, z_acc, z_seven, z_q, z_r
    bit.add 16, z_r, z_seven
    bit.dec 16, z_r
    bit.div 16, z_r, z_seven, z_q, dow
}
""".strip()

ZELLER_DATA = ADD_MUL_DATA + [
    "z_y: bit.vec 16, 0",
    "z_m: bit.vec 16, 0",
    "z_d: bit.vec 16, 0",
    "z_one: bit.vec 16, 1",
    "z_three: bit.vec 16, 3",
    "z_four: bit.vec 16, 4",
    "z_five: bit.vec 16, 5",
    "z_seven: bit.vec 16, 7",
    "z_12: bit.vec 16, 12",
    "z_13: bit.vec 16, 13",
    "z_100: bit.vec 16, 100",
    "z_K: bit.vec 16, 0",
    "z_J: bit.vec 16, 0",
    "z_term: bit.vec 16, 0",
    "z_q: bit.vec 16, 0",
    "z_r: bit.vec 16, 0",
    "z_acc: bit.vec 16, 0",
]

# dst[:16] = day-of-year of (year, month, day): sum lengths of months before
# `month`, then add `day`. Uses days_in_month_into for each prior month.
DAY_OF_YEAR_INTO = """
// dst[:16] = day-of-year of (year[:16], month[:16], day[:16]); 1-based.
def day_of_year_into dst, year, month, day @ loop, body, end < doy_m, doy_one, doy_len {
    bit.zero 16, dst
    bit.mov 16, doy_m, doy_one
  loop:
    bit.cmp 16, doy_m, month, body, end, end
  body:
    days_in_month_into doy_len, year, doy_m
    bit.add 16, dst, doy_len
    bit.inc 16, doy_m
    ;loop
  end:
    bit.add 16, dst, day
}
""".strip()

DAY_OF_YEAR_DATA = [
    "doy_m: bit.vec 16, 0",
    "doy_one: bit.vec 16, 1",
    "doy_len: bit.vec 16, 0",
]

# Read exactly two ASCII decimal digits from stdin into value[:16] (0-99).
READ_TWO_DIGITS = """
// Read exactly two ASCII decimal digits from stdin into value[:16] (0-99).
def read_two_digits value < r2_ch, r2_digit, r2_err {
    bit.zero 16, value
    bit.input r2_ch
    bit.ascii2dec r2_err, r2_digit, r2_ch
    bit.add 16, value, r2_digit
    bit.mul10 16, value
    bit.input r2_ch
    bit.ascii2dec r2_err, r2_digit, r2_ch
    bit.add 16, value, r2_digit
}
""".strip()

READ_TWO_DIGITS_DATA = [
    "r2_ch: bit.vec 8, 0",
    "r2_digit: bit.vec 16, 0",
    "r2_err: bit.bit",
]


# ===========================================================================
# Programs
# ===========================================================================

# ---- quarter_of_year: (m-1)/3 + 1 ----
C(
    "0864",
    "quarter_of_year",
    "Quarter Of Year",
    unsigned=True,
    value_data=[
        "q_month: bit.vec 16, 0",
        "q_one: bit.vec 16, 1",
        "q_three: bit.vec 16, 3",
        "q_q: bit.vec 16, 0",
        "q_r: bit.vec 16, 0",
    ],
    main_body="""
def main < q_month, q_one, q_three, q_q, q_r {
    stl.startup
    read_decimal 16, q_month
    bit.sub 16, q_month, q_one
    bit.div 16, q_month, q_three, q_q, q_r
    bit.add 16, q_q, q_one
    bit.print_dec_uint 16, q_q
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"5\n\0",
    out_bytes=b"2\n",
)

# ---- days_to_next_weekday: (target - today + 7) mod 7 ----
C(
    "0868",
    "days_to_next_weekday",
    "Days To Next Weekday",
    unsigned=True,
    value_data=[
        "dn_today: bit.vec 16, 0",
        "dn_target: bit.vec 16, 0",
        "dn_seven: bit.vec 16, 7",
        "dn_q: bit.vec 16, 0",
        "dn_r: bit.vec 16, 0",
    ],
    main_body="""
def main < dn_today, dn_target, dn_seven, dn_q, dn_r {
    stl.startup
    read_decimal 16, dn_today
    read_decimal 16, dn_target
    bit.add 16, dn_target, dn_seven
    bit.sub 16, dn_target, dn_today
    bit.div 16, dn_target, dn_seven, dn_q, dn_r
    bit.print_dec_uint 16, dn_r
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3\n1\n\0",
    out_bytes=b"5\n",
)

# ---- time_of_day_period: hour -> word ----
# morning 5-11, afternoon 12-16, evening 17-20, night 21-4.
C(
    "0867",
    "time_of_day_period",
    "Time Of Day Period",
    unsigned=True,
    value_data=[
        "tp_hour: bit.vec 16, 0",
        "tp_5: bit.vec 16, 5",
        "tp_12: bit.vec 16, 12",
        "tp_17: bit.vec 16, 17",
        "tp_21: bit.vec 16, 21",
    ],
    main_body="""
def main @ chk_after, chk_eve, chk_night, morning, afternoon, evening, night, done
        < tp_hour, tp_5, tp_12, tp_17, tp_21 {
    stl.startup
    read_decimal 16, tp_hour
    bit.cmp 16, tp_hour, tp_5, night, morning, chk_after
  chk_after:
    bit.cmp 16, tp_hour, tp_12, morning, afternoon, chk_eve
  chk_eve:
    bit.cmp 16, tp_hour, tp_17, afternoon, evening, chk_night
  chk_night:
    bit.cmp 16, tp_hour, tp_21, evening, night, night
  morning:
    stl.output "morning\\n"
    ;done
  afternoon:
    stl.output "afternoon\\n"
    ;done
  evening:
    stl.output "evening\\n"
    ;done
  night:
    stl.output "night\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"14\n\0",
    out_bytes=b"afternoon\n",
)

# ---- days_in_year: 366 if leap else 365 ----
C(
    "0849",
    "days_in_year",
    "Days In Year",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO],
    value_data=["dy_year: bit.vec 16, 0", "dy_flag: bit.bit"] + IS_LEAP_DATA,
    main_body="""
def main @ leap, done < dy_year, dy_flag {
    stl.startup
    read_decimal 16, dy_year
    is_leap_into dy_flag, dy_year
    bit.if1 dy_flag, leap
    stl.output "365\\n"
    ;done
  leap:
    stl.output "366\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"2000\n\0",
    out_bytes=b"366\n",
)

# ---- days_in_month ----
C(
    "0848",
    "days_in_month",
    "Days In Month",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO],
    value_data=["dm_year: bit.vec 16, 0", "dm_month: bit.vec 16, 0", "dm_days: bit.vec 16, 0"] + DAYS_IN_MONTH_DATA,
    main_body="""
def main < dm_year, dm_month, dm_days {
    stl.startup
    read_decimal 16, dm_year
    read_decimal 16, dm_month
    days_in_month_into dm_days, dm_year, dm_month
    bit.print_dec_uint 16, dm_days
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n2\n\0",
    out_bytes=b"29\n",
)

# ---- day_of_week_from_date (Zeller, Sunday=0) ----
C(
    "0847",
    "day_of_week_from_date",
    "Day Of Week From Date",
    unsigned=True,
    extra_helpers=[ADD_MUL_HELPERS, ZELLER_INTO],
    value_data=["dw_year: bit.vec 16, 0", "dw_month: bit.vec 16, 0", "dw_day: bit.vec 16, 0", "dw_dow: bit.vec 16, 0"]
    + ZELLER_DATA,
    main_body="""
def main < dw_year, dw_month, dw_day, dw_dow {
    stl.startup
    read_decimal 16, dw_year
    read_decimal 16, dw_month
    read_decimal 16, dw_day
    zeller_into dw_dow, dw_year, dw_month, dw_day
    bit.print_dec_uint 16, dw_dow
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n1\n1\n\0",
    out_bytes=b"6\n",
)

# ---- weekend_check (Zeller -> Sat(6) or Sun(0)) ----
C(
    "0862",
    "weekend_check",
    "Weekend Check",
    unsigned=True,
    extra_helpers=[ADD_MUL_HELPERS, ZELLER_INTO],
    value_data=[
        "wk_year: bit.vec 16, 0",
        "wk_month: bit.vec 16, 0",
        "wk_day: bit.vec 16, 0",
        "wk_dow: bit.vec 16, 0",
        "wk_six: bit.vec 16, 6",
    ]
    + ZELLER_DATA,
    main_body="""
def main @ yes, no, done < wk_year, wk_month, wk_day, wk_dow, wk_six {
    stl.startup
    read_decimal 16, wk_year
    read_decimal 16, wk_month
    read_decimal 16, wk_day
    zeller_into wk_dow, wk_year, wk_month, wk_day
    bit.if0 16, wk_dow, yes
    bit.cmp 16, wk_dow, wk_six, no, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"2000\n1\n1\n\0",
    out_bytes=b"1\n",
)

# ---- business_days_in_month: count Mon-Fri in month ----
# Compute dow of day 1 via Zeller, then walk days 1..len, counting weekdays
# (dow 1-5) and advancing dow mod 7.
C(
    "0863",
    "business_days_in_month",
    "Business Days In Month",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO, ADD_MUL_HELPERS, ZELLER_INTO],
    value_data=[
        "bd_year: bit.vec 16, 0",
        "bd_month: bit.vec 16, 0",
        "bd_len: bit.vec 16, 0",
        "bd_dow: bit.vec 16, 0",
        "bd_day: bit.vec 16, 0",
        "bd_count: bit.vec 16, 0",
        "bd_one: bit.vec 16, 1",
        "bd_six: bit.vec 16, 6",
    ]
    + DAYS_IN_MONTH_DATA
    + ZELLER_DATA,
    main_body="""
def main @ loop, body, weekday, advance, wrap, skip_wrap, end
        < bd_year, bd_month, bd_len, bd_dow, bd_day, bd_count, bd_one, bd_six {
    stl.startup
    read_decimal 16, bd_year
    read_decimal 16, bd_month
    days_in_month_into bd_len, bd_year, bd_month
    zeller_into bd_dow, bd_year, bd_month, bd_one
    bit.zero 16, bd_count
    bit.mov 16, bd_day, bd_one
  loop:
    bit.cmp 16, bd_day, bd_len, body, body, end
  body:
    bit.if0 16, bd_dow, advance
    bit.cmp 16, bd_dow, bd_six, weekday, advance, advance
  weekday:
    bit.inc 16, bd_count
  advance:
    bit.inc 16, bd_dow
    bit.cmp 16, bd_dow, bd_six, skip_wrap, skip_wrap, wrap
  wrap:
    bit.zero 16, bd_dow
  skip_wrap:
    bit.inc 16, bd_day
    ;loop
  end:
    bit.print_dec_uint 16, bd_count
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n1\n\0",
    out_bytes=b"21\n",
)

# ---- day_of_year ----
C(
    "0859",
    "day_of_year",
    "Day Of Year",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO, DAY_OF_YEAR_INTO],
    value_data=[
        "dyr_year: bit.vec 16, 0",
        "dyr_month: bit.vec 16, 0",
        "dyr_day: bit.vec 16, 0",
        "dyr_out: bit.vec 16, 0",
    ]
    + DAYS_IN_MONTH_DATA
    + DAY_OF_YEAR_DATA,
    main_body="""
def main < dyr_year, dyr_month, dyr_day, dyr_out {
    stl.startup
    read_decimal 16, dyr_year
    read_decimal 16, dyr_month
    read_decimal 16, dyr_day
    day_of_year_into dyr_out, dyr_year, dyr_month, dyr_day
    bit.print_dec_uint 16, dyr_out
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n3\n1\n\0",
    out_bytes=b"61\n",
)

# ---- date_from_day_of_year ----
# Walk months; subtract each month length until the remaining count fits.
C(
    "0860",
    "date_from_day_of_year",
    "Date From Day Of Year",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO],
    value_data=[
        "df_year: bit.vec 16, 0",
        "df_rem: bit.vec 16, 0",
        "df_month: bit.vec 16, 0",
        "df_len: bit.vec 16, 0",
        "df_one: bit.vec 16, 1",
    ]
    + DAYS_IN_MONTH_DATA,
    main_body="""
def main @ loop, fits, advance < df_year, df_rem, df_month, df_len, df_one {
    stl.startup
    read_decimal 16, df_year
    read_decimal 16, df_rem
    bit.mov 16, df_month, df_one
  loop:
    days_in_month_into df_len, df_year, df_month
    bit.cmp 16, df_rem, df_len, fits, fits, advance
  advance:
    bit.sub 16, df_rem, df_len
    bit.inc 16, df_month
    ;loop
  fits:
    bit.print_dec_uint 16, df_month
    stl.output ' '
    bit.print_dec_uint 16, df_rem
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n61\n\0",
    out_bytes=b"3 1\n",
)

# ---- is_valid_date ----
C(
    "0850",
    "is_valid_date",
    "Is Valid Date",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO],
    value_data=[
        "vd_year: bit.vec 16, 0",
        "vd_month: bit.vec 16, 0",
        "vd_day: bit.vec 16, 0",
        "vd_len: bit.vec 16, 0",
        "vd_one: bit.vec 16, 1",
        "vd_12: bit.vec 16, 12",
    ]
    + DAYS_IN_MONTH_DATA,
    main_body="""
def main @ chk_month_hi, chk_day, yes, no, done < vd_year, vd_month, vd_day, vd_len, vd_one, vd_12 {
    stl.startup
    read_decimal 16, vd_year
    read_decimal 16, vd_month
    read_decimal 16, vd_day
    bit.cmp 16, vd_month, vd_one, no, chk_month_hi, chk_month_hi
  chk_month_hi:
    bit.cmp 16, vd_month, vd_12, chk_day, chk_day, no
  chk_day:
    bit.if0 16, vd_day, no
    days_in_month_into vd_len, vd_year, vd_month
    bit.cmp 16, vd_day, vd_len, yes, yes, no
  yes:
    stl.output "1\\n"
    ;done
  no:
    stl.output "0\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"2000\n2\n29\n\0",
    out_bytes=b"1\n",
)

# ---- format_date_iso: YYYY-MM-DD ----
C(
    "0852",
    "format_date_iso",
    "Format Date Iso",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS],
    value_data=["fi_year: bit.vec 16, 0", "fi_month: bit.vec 16, 0", "fi_day: bit.vec 16, 0"] + PRINT_TWO_DIGITS_DATA,
    main_body="""
def main < fi_year, fi_month, fi_day {
    stl.startup
    read_decimal 16, fi_year
    read_decimal 16, fi_month
    read_decimal 16, fi_day
    bit.print_dec_uint 16, fi_year
    stl.output '-'
    print_two_digits fi_month
    stl.output '-'
    print_two_digits fi_day
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n3\n7\n\0",
    out_bytes=b"2000-03-07\n",
)

# ---- parse_date_iso_validate: read YYYY-MM-DD\n, validate ----
C(
    "0853",
    "parse_date_iso_validate",
    "Parse Date Iso Validate",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO, READ_TWO_DIGITS],
    value_data=[
        "pi_year: bit.vec 16, 0",
        "pi_month: bit.vec 16, 0",
        "pi_day: bit.vec 16, 0",
        "pi_len: bit.vec 16, 0",
        "pi_one: bit.vec 16, 1",
        "pi_12: bit.vec 16, 12",
        "pi_1900: bit.vec 16, 1900",
        "pi_2099: bit.vec 16, 2099",
        "pi_hi: bit.vec 16, 0",
        "pi_lo: bit.vec 16, 0",
    ]
    + DAYS_IN_MONTH_DATA
    + READ_TWO_DIGITS_DATA
    + SEP_DATA,
    main_body="""
def main @ chk_year_hi, chk_month_lo, chk_month_hi, chk_day, eat, yes, no, done
        < pi_year, pi_month, pi_day, pi_len, pi_one, pi_12, pi_1900, pi_2099, pi_hi, pi_lo, sep {
    stl.startup
    read_two_digits pi_hi
    read_two_digits pi_lo
    bit.input sep
    read_two_digits pi_month
    bit.input sep
    read_two_digits pi_day
    bit.zero 16, pi_year
    bit.mov 16, pi_year, pi_hi
    bit.mul10 16, pi_year
    bit.mul10 16, pi_year
    bit.add 16, pi_year, pi_lo
    bit.cmp 16, pi_year, pi_1900, no, chk_year_hi, chk_year_hi
  chk_year_hi:
    bit.cmp 16, pi_year, pi_2099, chk_month_lo, chk_month_lo, no
  chk_month_lo:
    bit.cmp 16, pi_month, pi_one, no, chk_month_hi, chk_month_hi
  chk_month_hi:
    bit.cmp 16, pi_month, pi_12, chk_day, chk_day, no
  chk_day:
    bit.if0 16, pi_day, no
    days_in_month_into pi_len, pi_year, pi_month
    bit.cmp 16, pi_day, pi_len, yes, yes, no
  yes:
    stl.output "1\\n"
    ;eat
  no:
    stl.output "0\\n"
  eat:
    bit.input sep
  done:
    stl.loop
}
""",
    in_bytes=b"2000-02-29\n\0",
    out_bytes=b"1\n",
)

# ---- seconds_to_clock_hms: HH:MM:SS ----
C(
    "0856",
    "seconds_to_clock_hms",
    "Seconds To Clock Hms",
    extra_helpers=[READ_DECIMAL_24, PRINT_TWO_DIGITS],
    value_data=[
        "sc_total: bit.vec 24, 0",
        "sc_3600: bit.vec 24, 3600",
        "sc_60: bit.vec 24, 60",
        "sc_h: bit.vec 24, 0",
        "sc_m: bit.vec 24, 0",
        "sc_s: bit.vec 24, 0",
        "sc_rem: bit.vec 24, 0",
    ]
    + READ_DECIMAL_24_DATA
    + PRINT_TWO_DIGITS_DATA,
    main_body="""
def main < sc_total, sc_3600, sc_60, sc_h, sc_m, sc_s, sc_rem {
    stl.startup
    read_decimal24 sc_total
    bit.div 24, sc_total, sc_3600, sc_h, sc_rem
    bit.div 24, sc_rem, sc_60, sc_m, sc_s
    print_two_digits sc_h
    stl.output ':'
    print_two_digits sc_m
    stl.output ':'
    print_two_digits sc_s
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"3661\n\0",
    out_bytes=b"01:01:01\n",
)

# ---- clock_hms_to_seconds: read HH:MM:SS\n -> total seconds ----
C(
    "0857",
    "clock_hms_to_seconds",
    "Clock Hms To Seconds",
    unsigned=True,
    extra_helpers=[ADD_TIMES_24, READ_TWO_DIGITS],
    value_data=[
        "hs_h: bit.vec 24, 0",
        "hs_m: bit.vec 24, 0",
        "hs_s: bit.vec 24, 0",
        "hs_total: bit.vec 24, 0",
        "hs_3600: bit.vec 24, 3600",
        "hs_60: bit.vec 24, 60",
    ]
    + ADD_TIMES_24_DATA
    + READ_TWO_DIGITS_DATA
    + SEP_DATA,
    main_body="""
def main < hs_h, hs_m, hs_s, hs_total, hs_3600, hs_60, sep {
    stl.startup
    read_two_digits hs_h
    bit.input sep
    read_two_digits hs_m
    bit.input sep
    read_two_digits hs_s
    bit.input sep
    bit.zero 24, hs_total
    add_times24 hs_total, hs_3600, hs_h
    add_times24 hs_total, hs_60, hs_m
    bit.add 24, hs_total, hs_s
    bit.print_dec_uint 24, hs_total
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"01:01:01\n\0",
    out_bytes=b"3661\n",
)

# ---- short_name_to_month: 3-char abbrev -> 1-12 ----
# Pack the 3 ASCII bytes into a 24-bit vector and compare against each key.
# Keys are little-endian byte order: 'Jan' -> 0x6e_61_4a (n,a,J at bytes 2,1,0).
C(
    "0858",
    "short_name_to_month",
    "Short Name To Month",
    unsigned=True,
    value_data=[
        "sn_c0: bit.vec 8, 0",
        "sn_c1: bit.vec 8, 0",
        "sn_c2: bit.vec 8, 0",
        "sn_in: bit.vec 24, 0",
        "kjan: bit.vec 24, 0x6e614a",
        "kfeb: bit.vec 24, 0x626546",
        "kmar: bit.vec 24, 0x72614d",
        "kapr: bit.vec 24, 0x727041",
        "kmay: bit.vec 24, 0x79614d",
        "kjun: bit.vec 24, 0x6e754a",
        "kjul: bit.vec 24, 0x6c754a",
        "kaug: bit.vec 24, 0x677541",
        "ksep: bit.vec 24, 0x706553",
        "koct: bit.vec 24, 0x74634f",
        "knov: bit.vec 24, 0x766f4e",
    ]
    + SEP_DATA,
    main_body="""
def main @ t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11,
          m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, eat, done
        < sn_c0, sn_c1, sn_c2, sn_in, sep,
          kjan, kfeb, kmar, kapr, kmay, kjun, kjul, kaug, ksep, koct, knov {
    stl.startup
    bit.input sn_c0
    bit.input sn_c1
    bit.input sn_c2
    bit.zero 24, sn_in
    bit.mov 8, sn_in, sn_c0
    bit.mov 8, sn_in + 8*dw, sn_c1
    bit.mov 8, sn_in + 16*dw, sn_c2
    bit.cmp 24, sn_in, kjan, t1, m1, t1
  t1:
    bit.cmp 24, sn_in, kfeb, t2, m2, t2
  t2:
    bit.cmp 24, sn_in, kmar, t3, m3, t3
  t3:
    bit.cmp 24, sn_in, kapr, t4, m4, t4
  t4:
    bit.cmp 24, sn_in, kmay, t5, m5, t5
  t5:
    bit.cmp 24, sn_in, kjun, t6, m6, t6
  t6:
    bit.cmp 24, sn_in, kjul, t7, m7, t7
  t7:
    bit.cmp 24, sn_in, kaug, t8, m8, t8
  t8:
    bit.cmp 24, sn_in, ksep, t9, m9, t9
  t9:
    bit.cmp 24, sn_in, koct, t10, m10, t10
  t10:
    bit.cmp 24, sn_in, knov, t11, m11, t11
  t11:
    ;m12
  m1:
    stl.output "1\\n"
    ;eat
  m2:
    stl.output "2\\n"
    ;eat
  m3:
    stl.output "3\\n"
    ;eat
  m4:
    stl.output "4\\n"
    ;eat
  m5:
    stl.output "5\\n"
    ;eat
  m6:
    stl.output "6\\n"
    ;eat
  m7:
    stl.output "7\\n"
    ;eat
  m8:
    stl.output "8\\n"
    ;eat
  m9:
    stl.output "9\\n"
    ;eat
  m10:
    stl.output "10\\n"
    ;eat
  m11:
    stl.output "11\\n"
    ;eat
  m12:
    stl.output "12\\n"
  eat:
    bit.input sep
  done:
    stl.loop
}
""",
    in_bytes=b"Mar\n\0",
    out_bytes=b"3\n",
)

# ---- format_time_12_hour: HH:MM -> <H>:<MM> AM/PM ----
C(
    "0854",
    "format_time_12_hour",
    "Format Time 12 Hour",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS, READ_TWO_DIGITS],
    value_data=[
        "ft_h: bit.vec 16, 0",
        "ft_m: bit.vec 16, 0",
        "ft_12: bit.vec 16, 12",
        "ft_h12: bit.vec 16, 0",
        "ft_is_pm: bit.bit",
    ]
    + PRINT_TWO_DIGITS_DATA
    + READ_TWO_DIGITS_DATA
    + SEP_DATA,
    main_body="""
def main @ am_block, set_pm, make_12, sub_12, have_h12, ampm_am, ampm_pm, done
        < ft_h, ft_m, ft_12, ft_h12, ft_is_pm, sep {
    stl.startup
    read_two_digits ft_h
    bit.input sep
    read_two_digits ft_m
    bit.input sep
    bit.zero ft_is_pm
    bit.cmp 16, ft_h, ft_12, am_block, set_pm, set_pm
  set_pm:
    bit.one ft_is_pm
  am_block:
    bit.mov 16, ft_h12, ft_h
    bit.if0 16, ft_h12, make_12
    bit.cmp 16, ft_h12, ft_12, have_h12, have_h12, sub_12
  sub_12:
    bit.sub 16, ft_h12, ft_12
    ;have_h12
  make_12:
    bit.add 16, ft_h12, ft_12
  have_h12:
    bit.print_dec_uint 16, ft_h12
    stl.output ':'
    print_two_digits ft_m
    stl.output ' '
    bit.if1 ft_is_pm, ampm_pm
  ampm_am:
    stl.output "AM\\n"
    ;done
  ampm_pm:
    stl.output "PM\\n"
  done:
    stl.loop
}
""",
    in_bytes=b"13:05\n\0",
    out_bytes=b"1:05 PM\n",
)

# ---- format_time_24_hour: <H>:<MM> AM/PM -> HH:MM ----
# Read variable-width hour digits until ':', MM as two digits, ' ', AM/PM marker.
C(
    "0855",
    "format_time_24_hour",
    "Format Time 24 Hour",
    unsigned=True,
    extra_helpers=[PRINT_TWO_DIGITS, READ_TWO_DIGITS],
    value_data=[
        "fh_h: bit.vec 16, 0",
        "fh_m: bit.vec 16, 0",
        "fh_12: bit.vec 16, 12",
        "fh_marker: bit.vec 8, 0",
        "fh_P: bit.vec 8, 'P'",
        "fh_colon: bit.vec 8, ':'",
        "fh_digit: bit.vec 16, 0",
        "fh_ch: bit.vec 8, 0",
        "fh_err: bit.bit",
    ]
    + PRINT_TWO_DIGITS_DATA
    + READ_TWO_DIGITS_DATA
    + SEP_DATA,
    main_body="""
def main @ hloop, hdigit, hdone, is_pm, is_am, pm_adjust, am_twelve, do_print, done
        < fh_h, fh_m, fh_12, fh_marker, fh_P, fh_colon, fh_digit, fh_ch, fh_err, sep {
    stl.startup
    bit.zero 16, fh_h
  hloop:
    bit.input fh_ch
    bit.cmp 8, fh_ch, fh_colon, hdigit, hdone, hdigit
  hdigit:
    bit.ascii2dec fh_err, fh_digit, fh_ch
    bit.mul10 16, fh_h
    bit.add 16, fh_h, fh_digit
    ;hloop
  hdone:
    read_two_digits fh_m
    bit.input sep
    bit.input fh_marker
    bit.input sep
    bit.input sep
    bit.cmp 8, fh_marker, fh_P, is_am, is_pm, is_am
  is_pm:
    bit.cmp 16, fh_h, fh_12, pm_adjust, do_print, pm_adjust
  pm_adjust:
    bit.add 16, fh_h, fh_12
    ;do_print
  is_am:
    bit.cmp 16, fh_h, fh_12, do_print, am_twelve, do_print
  am_twelve:
    bit.zero 16, fh_h
  do_print:
    print_two_digits fh_h
    stl.output ':'
    print_two_digits fh_m
    stl.output '\\n'
  done:
    stl.loop
}
""",
    in_bytes=b"1:05 PM\n\0",
    out_bytes=b"13:05\n",
)

# ---- days_since_epoch_2000 ----
# Sum full years 2000..year-1 (365/366), then add (day_of_year - 1).
C(
    "0865",
    "days_since_epoch_2000",
    "Days Since Epoch 2000",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO, DAY_OF_YEAR_INTO],
    value_data=[
        "ep_year: bit.vec 16, 0",
        "ep_month: bit.vec 16, 0",
        "ep_day: bit.vec 16, 0",
        "ep_total: bit.vec 16, 0",
        "ep_y: bit.vec 16, 0",
        "ep_2000: bit.vec 16, 2000",
        "ep_flag: bit.bit",
        "ep_365: bit.vec 16, 365",
        "ep_366: bit.vec 16, 366",
        "ep_doy: bit.vec 16, 0",
        "ep_one: bit.vec 16, 1",
    ]
    + DAYS_IN_MONTH_DATA
    + DAY_OF_YEAR_DATA,
    main_body="""
def main @ yloop, ybody, yleap, yadd, yend
        < ep_year, ep_month, ep_day, ep_total, ep_y, ep_2000, ep_flag, ep_365, ep_366, ep_doy, ep_one {
    stl.startup
    read_decimal 16, ep_year
    read_decimal 16, ep_month
    read_decimal 16, ep_day
    bit.zero 16, ep_total
    bit.mov 16, ep_y, ep_2000
  yloop:
    bit.cmp 16, ep_y, ep_year, ybody, yend, yend
  ybody:
    is_leap_into ep_flag, ep_y
    bit.if1 ep_flag, yleap
    bit.add 16, ep_total, ep_365
    ;yadd
  yleap:
    bit.add 16, ep_total, ep_366
  yadd:
    bit.inc 16, ep_y
    ;yloop
  yend:
    day_of_year_into ep_doy, ep_year, ep_month, ep_day
    bit.add 16, ep_total, ep_doy
    bit.sub 16, ep_total, ep_one
    bit.print_dec_uint 16, ep_total
    stl.output '\\n'
    stl.loop
}
""",
    in_bytes=b"2000\n1\n1\n\0",
    out_bytes=b"0\n",
)

# ---- epoch_to_date_2000 ----
# Subtract whole years (365/366) until the remaining count is a valid 0-based
# day-of-year; +1 makes it 1-based, then walk months subtracting lengths.
C(
    "0866",
    "epoch_to_date_2000",
    "Epoch To Date 2000",
    unsigned=True,
    extra_helpers=[IS_LEAP_INTO, DAYS_IN_MONTH_INTO],
    value_data=[
        "et_rem: bit.vec 16, 0",
        "et_year: bit.vec 16, 0",
        "et_2000: bit.vec 16, 2000",
        "et_flag: bit.bit",
        "et_ylen: bit.vec 16, 0",
        "et_365: bit.vec 16, 365",
        "et_366: bit.vec 16, 366",
        "et_month: bit.vec 16, 0",
        "et_len: bit.vec 16, 0",
        "et_one: bit.vec 16, 1",
    ]
    + DAYS_IN_MONTH_DATA,
    main_body="""
def main @ yloop, yleap, yhave, yfits, yadvance, mloop, mfits, madvance, done
        < et_rem, et_year, et_2000, et_flag, et_ylen, et_365, et_366, et_month, et_len, et_one {
    stl.startup
    read_decimal 16, et_rem
    bit.mov 16, et_year, et_2000
  yloop:
    is_leap_into et_flag, et_year
    bit.if1 et_flag, yleap
    bit.mov 16, et_ylen, et_365
    ;yhave
  yleap:
    bit.mov 16, et_ylen, et_366
  yhave:
    bit.cmp 16, et_rem, et_ylen, yfits, yadvance, yadvance
  yadvance:
    bit.sub 16, et_rem, et_ylen
    bit.inc 16, et_year
    ;yloop
  yfits:
    bit.inc 16, et_rem
    bit.mov 16, et_month, et_one
  mloop:
    days_in_month_into et_len, et_year, et_month
    bit.cmp 16, et_rem, et_len, mfits, mfits, madvance
  madvance:
    bit.sub 16, et_rem, et_len
    bit.inc 16, et_month
    ;mloop
  mfits:
    bit.print_dec_uint 16, et_year
    stl.output ' '
    bit.print_dec_uint 16, et_month
    stl.output ' '
    bit.print_dec_uint 16, et_rem
    stl.output '\\n'
  done:
    stl.loop
}
""",
    in_bytes=b"0\n\0",
    out_bytes=b"2000 1 1\n",
)


print("---")
print("CALENDAR_TIME DONE")
