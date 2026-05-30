#!/usr/bin/env python3
"""
Tax Invoice Excel template generator for Maverick Infra and Engineers Pvt. Ltd.
Generates a professional, print-ready .xlsx template with auto-calculated totals.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.worksheet.page import PageMargins


# ── PALETTE ─────────────────────────────────────────────────────────────────
TEAL        = "1A5276"
TEAL_LIGHT  = "D6EAF8"
SUBTOT_BG   = "EBF5FB"
WHITE       = "FFFFFF"
BLACK       = "000000"
GRAY_FOOT   = "7F8C8D"
LOGO_BG     = "EAF4FB"
GRAY_MID    = "555555"
BORDER_CLR  = "AAAAAA"


# ── STYLE HELPERS ───────────────────────────────────────────────────────────
def _fnt(bold=False, sz=9, col=BLACK, italic=False, name="Calibri"):
    return Font(name=name, bold=bold, size=sz, color=col, italic=italic)


def _bg(col):
    return PatternFill("solid", fgColor=col)


def _aln(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


def _side(style="thin", color=BORDER_CLR):
    return Side(style=style, color=color)


def _border(left=False, right=False, top=False, bottom=False,
            style="thin", color=BORDER_CLR):
    s = _side(style, color)
    n = None
    return Border(
        left=s if left else n,
        right=s if right else n,
        top=s if top else n,
        bottom=s if bottom else n,
    )


THIN_ALL = Border(
    left=_side(), right=_side(), top=_side(), bottom=_side()
)
TEAL_BOT_MED = Border(bottom=_side("medium", TEAL))
TEAL_TOP_MED = Border(top=_side("medium", TEAL))
TEAL_ALL_MED = Border(
    left=_side("medium", TEAL), right=_side("medium", TEAL),
    top=_side("medium", TEAL),  bottom=_side("medium", TEAL),
)


def _set(ws, ref, value=None, font=None, fill=None,
         border=None, alignment=None, num_fmt=None):
    cell = ws[ref] if isinstance(ref, str) else ref
    if value is not None:
        cell.value = value
    if font:
        cell.font = font
    if fill:
        cell.fill = fill
    if border:
        cell.border = border
    if alignment:
        cell.alignment = alignment
    if num_fmt:
        cell.number_format = num_fmt
    return cell


def _full_border_range(ws, min_row, max_row, min_col, max_col, border=THIN_ALL):
    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            ws.cell(row=row, column=col).border = border


def _row_bottom_border(ws, row, min_col=1, max_col=7, style="medium", color=TEAL):
    b = Border(bottom=_side(style, color))
    for col in range(min_col, max_col + 1):
        ws.cell(row=row, column=col).border = b


# ── MAIN BUILDER ────────────────────────────────────────────────────────────
def create_tax_invoice(output_path="Tax_Invoice_Maverick.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tax Invoice"

    # ── Column widths (A–G)
    # A=S.NO.  B=HS CODE  C=DESCRIPTION  D=QTY num  E=UNIT  F=RATE  G=AMOUNT
    for col, w in [("A", 6.5), ("B", 11.5), ("C", 34),
                   ("D", 9.5), ("E", 8.5), ("F", 13.5), ("G", 15)]:
        ws.column_dimensions[col].width = w

    # ── Row heights
    rh = {
        1: 5,  2: 33, 3: 13, 4: 13, 5: 13, 6: 10,
        7: 15, 8: 15, 9: 14, 10: 14, 11: 14, 12: 14, 13: 10,
        14: 22,
        **{r: 18 for r in range(15, 30)},
        30: 15, 31: 15, 32: 20, 33: 12, 34: 8,
        35: 16, 36: 15, 37: 15, 38: 15, 39: 15,
        40: 15, 41: 22, 42: 22, 43: 16,
        44: 36, 45: 6, 46: 13, 47: 12, 48: 12,
    }
    for r, h in rh.items():
        ws.row_dimensions[r].height = h

    m = ws.merge_cells  # shorthand alias

    # ════════════════════════════════════════════════════════════
    # 1. HEADER  (rows 1–5)
    # ════════════════════════════════════════════════════════════

    # Logo placeholder  A1:B5
    m("A1:B5")
    _set(ws, "A1", "[  LOGO  ]",
         font=_fnt(bold=True, sz=11, col=TEAL),
         fill=_bg(LOGO_BG),
         alignment=_aln("center", "center"))
    _full_border_range(ws, 1, 5, 1, 2,
                       border=Border(left=_side("thin", "CCCCCC"),
                                     right=_side("thin", "CCCCCC"),
                                     top=_side("thin", "CCCCCC"),
                                     bottom=_side("thin", "CCCCCC")))

    # Company name  C2:E2
    m("C2:E2")
    _set(ws, "C2", "MAVERICK INFRA AND ENGINEERS PVT. LTD.",
         font=_fnt(bold=True, sz=14, col=TEAL),
         alignment=_aln("left", "center"))

    # Tagline  C3:E3
    m("C3:E3")
    _set(ws, "C3", "‘Model  •  Innovate  •  Elevate’",
         font=_fnt(italic=True, sz=9, col=GRAY_MID),
         alignment=_aln("left", "center"))

    # Address  C4:E4
    m("C4:E4")
    _set(ws, "C4", "Pokhara-15, Kaski District, Gandaki Province, Nepal",
         font=_fnt(sz=9),
         alignment=_aln("left", "center"))

    # Company PAN  C5:E5
    m("C5:E5")
    _set(ws, "C5", "PAN: 622501XXX",
         font=_fnt(bold=True, sz=9, col=TEAL),
         alignment=_aln("left", "center"))

    # "TAX INVOICE" title  F1:G5
    m("F1:G5")
    _set(ws, "F1", "TAX\nINVOICE",
         font=Font(name="Calibri", bold=True, size=27, color=TEAL),
         alignment=Alignment(horizontal="right", vertical="center",
                             wrap_text=True))

    # Separator below header
    _row_bottom_border(ws, 6)

    # ════════════════════════════════════════════════════════════
    # 2. BILL TO  +  INVOICE METADATA  (rows 7–12)
    # ════════════════════════════════════════════════════════════

    # ── Left: Bill To (A:C) ──────────────────────────────────
    bill_rows = [
        ("A7:C7",  "BILL TO:",                          True,  TEAL),
        ("A8:C8",  "M/S. CLIENT COMPANY NAME",          True,  TEAL),
        ("A9:C9",  "Client Address Line",               False, BLACK),
        ("A10:C10","Phone: (977) XXXXX XXXXX",          False, BLACK),
        ("A11:C11","Email: client@example.com",         False, BLACK),
        ("A12:C12","PAN: XXXXXXXXX",                    True,  TEAL),
    ]
    for rng, txt, bold, col in bill_rows:
        m(rng)
        ref = rng.split(":")[0]
        _set(ws, ref, txt,
             font=_fnt(bold=bold, sz=9, col=col),
             alignment=_aln("left", "center"))

    # ── Right: Invoice metadata (D:G) ──────────────────────
    meta = [
        (7,  "Tax Invoice No.",  "TI-001-082/83"),
        (8,  "Issue Date",       "2082/01/24"),
        (9,  "Due Date",         "2082/02/08"),
        (10, "Payment Mode",     "Bank Account"),
        (11, "Reference",        ""),
    ]
    for row, label, val in meta:
        m(f"D{row}:E{row}")
        _set(ws, f"D{row}", f"{label}   :",
             font=_fnt(sz=9, col=TEAL),
             alignment=_aln("right", "center"))
        m(f"F{row}:G{row}")
        _set(ws, f"F{row}", val,
             font=_fnt(sz=9),
             alignment=_aln("left", "center"))

    # Separator above table
    _row_bottom_border(ws, 13)

    # ════════════════════════════════════════════════════════════
    # 3. TABLE HEADER  (row 14)
    # ════════════════════════════════════════════════════════════

    tbl_headers = [
        ("A14", None,   "S.NO."),
        ("B14", None,   "HS CODE"),
        ("C14", None,   "DESCRIPTION"),
        ("D14", "E14",  "QTY."),
        ("F14", None,   "RATE"),
        ("G14", None,   "AMOUNT"),
    ]
    for start, end, label in tbl_headers:
        if end:
            m(f"{start}:{end}")
        _set(ws, start, label,
             font=_fnt(bold=True, sz=9, col=WHITE),
             fill=_bg(TEAL),
             border=TEAL_ALL_MED,
             alignment=_aln("center", "center"))

    # ════════════════════════════════════════════════════════════
    # 4. ITEM ROWS  (rows 15–29)
    # ════════════════════════════════════════════════════════════

    for idx, row in enumerate(range(15, 30), start=1):
        # S.NO.
        _set(ws, f"A{row}", idx,
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("center", "center"))

        # HS CODE  – user fills (default "-")
        _set(ws, f"B{row}", "-",
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("center", "center"))

        # DESCRIPTION
        _set(ws, f"C{row}", "",
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("left", "center"))

        # QTY number  (D)
        _set(ws, f"D{row}", None,
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("right", "center"),
             num_fmt="#,##0.##")

        # UNIT  (E)  e.g. "Job", "m", "pcs"
        _set(ws, f"E{row}", "",
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("left", "center"))

        # RATE
        _set(ws, f"F{row}", None,
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("right", "center"),
             num_fmt="#,##0.00")

        # AMOUNT  = QTY × RATE
        _set(ws, f"G{row}", f"=IFERROR(D{row}*F{row},\"\")",
             font=_fnt(sz=9),
             border=THIN_ALL,
             alignment=_aln("right", "center"),
             num_fmt="#,##0.00")

    # ════════════════════════════════════════════════════════════
    # 5. SUBTOTAL / VAT / TOTAL  (rows 30–33)
    # ════════════════════════════════════════════════════════════

    # IN WORDS  A30:D32  (spans 3 rows)
    m("A30:D32")
    _set(ws, "A30", "IN WORDS:\n\n",
         font=_fnt(bold=True, sz=9),
         border=THIN_ALL,
         alignment=_aln("left", "top", wrap=True))

    # ── SUBTOTAL
    m("E30:F30")
    _set(ws, "E30", "SUBTOTAL  :",
         font=_fnt(bold=True, sz=9),
         fill=_bg(SUBTOT_BG),
         border=THIN_ALL,
         alignment=_aln("right", "center"))
    _set(ws, "G30", "=SUM(G15:G29)",
         font=_fnt(bold=True, sz=9),
         fill=_bg(SUBTOT_BG),
         border=THIN_ALL,
         alignment=_aln("right", "center"),
         num_fmt="#,##0.00")

    # ── 13% VAT
    m("E31:F31")
    _set(ws, "E31", "13% VAT  :",
         font=_fnt(sz=9),
         fill=_bg(SUBTOT_BG),
         border=THIN_ALL,
         alignment=_aln("right", "center"))
    _set(ws, "G31", "=ROUND(G30*0.13,2)",
         font=_fnt(sz=9),
         fill=_bg(SUBTOT_BG),
         border=THIN_ALL,
         alignment=_aln("right", "center"),
         num_fmt="#,##0.00")

    # ── TOTAL AMOUNT
    m("E32:F32")
    _set(ws, "E32", "TOTAL AMOUNT :    NPR",
         font=_fnt(bold=True, sz=10, col=WHITE),
         fill=_bg(TEAL),
         border=TEAL_ALL_MED,
         alignment=_aln("right", "center"))
    _set(ws, "G32", "=G30+G31",
         font=_fnt(bold=True, sz=11, col=WHITE),
         fill=_bg(TEAL),
         border=TEAL_ALL_MED,
         alignment=_aln("right", "center"),
         num_fmt="#,##0.00")

    # ── E & OE note
    m("E33:G33")
    _set(ws, "E33", "(E. & E. O.)",
         font=_fnt(italic=True, sz=8, col="888888"),
         alignment=_aln("right", "center"))

    # ════════════════════════════════════════════════════════════
    # 6. BANK DETAILS + SIGNATURE  (rows 35–43)
    # ════════════════════════════════════════════════════════════

    # ── Bank details header  A35:C35
    m("A35:C35")
    _set(ws, "A35", "BANK DETAILS",
         font=_fnt(bold=True, sz=9, col=TEAL),
         fill=_bg(TEAL_LIGHT),
         border=THIN_ALL,
         alignment=_aln("left", "center"))

    bank_rows = [
        (36, "Account Name:",  "MAVERICK INFRA AND ENGINEERS PVT. LTD."),
        (37, "Bank Name:",     "Machhapuchhre Bank Ltd."),
        (38, "Branch:",        "Nayabazar, Pokhara"),
        (39, "Account No.:",   "00109943171XXXXX"),
    ]
    for row, lbl, val in bank_rows:
        _set(ws, f"A{row}", lbl,
             font=_fnt(bold=True, sz=9, col=TEAL),
             fill=_bg(TEAL_LIGHT),
             border=THIN_ALL,
             alignment=_aln("left", "center"))
        m(f"B{row}:C{row}")
        _set(ws, f"B{row}", val,
             font=_fnt(bold=True, sz=9),
             border=THIN_ALL,
             alignment=_aln("left", "center"))

    # Remarks header  A40:C40
    m("A40:C40")
    _set(ws, "A40", "REMARKS",
         font=_fnt(bold=True, sz=9, col=TEAL),
         fill=_bg(TEAL_LIGHT),
         border=THIN_ALL,
         alignment=_aln("left", "center"))

    # Remarks text area  A41:C42
    m("A41:C42")
    _set(ws, "A41", "",
         border=THIN_ALL,
         alignment=_aln("left", "top", wrap=True))

    # Left blank row 43
    m("A43:C43")
    ws["A43"].border = THIN_ALL

    # ── Right side: certification + signature  D35:G43
    # Certification text
    m("D35:G35")
    _set(ws, "D35",
         "Certified that the particulars given above are true and correct.",
         font=_fnt(italic=True, sz=8),
         border=THIN_ALL,
         alignment=_aln("left", "center", wrap=True))

    # Company name in signature block
    m("D36:G36")
    _set(ws, "D36", "FOR MAVERICK INFRA AND ENGINEERS PVT. LTD.",
         font=_fnt(bold=True, sz=9, col=TEAL),
         border=THIN_ALL,
         alignment=_aln("left", "center"))

    # Computer generated note / signature space
    m("D37:G42")
    _set(ws, "D37",
         "This is a computer generated\ninvoice, no signature required.",
         font=Font(name="Calibri", italic=True, size=11, color="BBBBBB"),
         border=THIN_ALL,
         alignment=_aln("center", "center", wrap=True))

    # Authorized signatory label
    m("D43:G43")
    _set(ws, "D43", "Authorized Signatory",
         font=_fnt(sz=9, col=TEAL),
         border=THIN_ALL,
         alignment=_aln("center", "center"))

    # ════════════════════════════════════════════════════════════
    # 7. FOOTER  (rows 46–48)
    # ════════════════════════════════════════════════════════════

    # Thin top rule
    _row_bottom_border(ws, 45, style="thin", color=TEAL)

    m("A46:D48")
    footer_left = (
        "MAVERICK INFRA AND ENGINEERS PVT. LTD.\n"
        "Address: Pokhara-15, Kaski District, Gandaki Province, Nepal\n"
        "Phone: (977) 98028 58556,  98028 23544  |  Web: www.maverickinfra.com.np"
    )
    _set(ws, "A46", footer_left,
         font=_fnt(sz=8, col=GRAY_FOOT),
         alignment=_aln("left", "top", wrap=True))

    m("E46:G48")
    _set(ws, "E46", "✉  accounts@maverickinfra.com.np",
         font=_fnt(sz=9, col=TEAL),
         alignment=_aln("right", "bottom"))

    # ════════════════════════════════════════════════════════════
    # 8. PRINT & SHEET SETTINGS
    # ════════════════════════════════════════════════════════════

    ws.print_area = "A1:G48"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = 9          # A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToHeight = 1
    ws.page_setup.fitToWidth = 1
    ws.page_margins = PageMargins(
        left=0.5, right=0.5, top=0.75, bottom=0.75,
        header=0.3, footer=0.3
    )

    # Freeze rows 1-14 so header stays visible while scrolling items
    ws.freeze_panes = "A15"

    # Tab color matching brand
    ws.sheet_properties.tabColor = TEAL

    wb.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    create_tax_invoice()
