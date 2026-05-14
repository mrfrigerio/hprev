#!/usr/bin/env python3
"""Generate a visual spreadsheet mockup for the HPrev histogram.

The script writes a small XLSX file using only Python's standard library so the
artifact can be regenerated without installing project dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "hprev_histograma_esboco_visual.xlsx"
ZIP_TIMESTAMP = (2026, 5, 14, 0, 0, 0)


WEEKDAYS_PT = ("seg", "ter", "qua", "qui", "sex", "sab", "dom")
MONTHS_PT = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)


def xml(value: Any) -> str:
    return escape(str(value), {'"': "&quot;"})


def col_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def cell_ref(row: int, col: int) -> str:
    return f"{col_name(col)}{row}"


@dataclass(frozen=True)
class Formula:
    expression: str
    cached_value: int | float | None = None


@dataclass
class Worksheet:
    name: str
    cells: dict[tuple[int, int], tuple[Any, int]] = field(default_factory=dict)
    merges: list[str] = field(default_factory=list)
    col_widths: dict[int, float] = field(default_factory=dict)
    row_heights: dict[int, float] = field(default_factory=dict)
    frozen_cell: str | None = None
    x_split: int = 0
    y_split: int = 0
    data_validations: list[tuple[str, str]] = field(default_factory=list)

    def set(self, row: int, col: int, value: Any, style: int = 0) -> None:
        self.cells[(row, col)] = (value, style)

    def merge(self, start_row: int, start_col: int, end_row: int, end_col: int) -> None:
        self.merges.append(f"{cell_ref(start_row, start_col)}:{cell_ref(end_row, end_col)}")

    def set_row_height(self, row: int, height: float) -> None:
        self.row_heights[row] = height

    def set_col_width(self, col: int, width: float) -> None:
        self.col_widths[col] = width

    def freeze(self, row: int, col: int) -> None:
        self.frozen_cell = cell_ref(row, col)
        self.x_split = col - 1
        self.y_split = row - 1

    @property
    def max_row(self) -> int:
        rows = [row for row, _ in self.cells] + [
            int("".join(ch for ch in merge.split(":")[1] if ch.isdigit())) for merge in self.merges
        ]
        return max(rows) if rows else 1

    @property
    def max_col(self) -> int:
        cols = [col for _, col in self.cells]
        for merge in self.merges:
            end_ref = merge.split(":")[1]
            letters = "".join(ch for ch in end_ref if ch.isalpha())
            total = 0
            for char in letters:
                total = total * 26 + ord(char) - 64
            cols.append(total)
        return max(cols) if cols else 1


class Styles:
    """Stable style indexes used by the generated workbook."""

    DEFAULT = 0
    TITLE = 1
    SUBTITLE = 2
    INFO = 3
    FORM_LABEL = 4
    FORM_VALUE = 5
    RESOURCE_TITLE = 6
    CONTENT_HEADER = 7
    BUSINESS_HEADER = 8
    PHASE_HEADER = 9
    PHASE_COUNT = 10
    MONTH_HEADER = 11
    WEEKDAY = 12
    WEEKEND_HEADER = 13
    LEFT_HEADER = 14
    SECTION = 15
    RESOURCE = 16
    QUANTITY = 17
    WEEKEND_QUANTITY = 18
    TOTAL_LABEL = 19
    TOTAL = 20
    NOTE = 21
    TABLE_HEADER = 22
    WARNING = 23
    OK = 24
    SECTION_LABOR = 25
    SECTION_EQUIPMENT = 26
    PARTIAL_TOTAL = 27


def styles_xml() -> str:
    fonts = [
        {"size": 11, "color": "FF1F2937", "bold": False},
        {"size": 16, "color": "FFFFFFFF", "bold": True},
        {"size": 12, "color": "FFFFFFFF", "bold": False},
        {"size": 11, "color": "FFFFFFFF", "bold": True},
        {"size": 11, "color": "FF111827", "bold": True},
        {"size": 10, "color": "FF374151", "bold": False},
        {"size": 10, "color": "FF92400E", "bold": True},
    ]
    fills = [
        None,
        "gray125",
        "FF1F4E78",
        "FF5B9BD5",
        "FFD9EAF7",
        "FFE2F0D9",
        "FF7030A0",
        "FFBFBFBF",
        "FFFCE4D6",
        "FFF3F4F6",
        "FF404040",
        "FFEDF2F7",
        "FFE2E8F0",
        "FFFFF2CC",
        "FFDCFCE7",
        "FF0F766E",
        "FF7C2D12",
        "FFDBEAFE",
    ]
    border_none = "<border><left/><right/><top/><bottom/><diagonal/></border>"
    border_thin = (
        '<border><left style="thin"><color rgb="FFCBD5E1"/></left>'
        '<right style="thin"><color rgb="FFCBD5E1"/></right>'
        '<top style="thin"><color rgb="FFCBD5E1"/></top>'
        '<bottom style="thin"><color rgb="FFCBD5E1"/></bottom><diagonal/></border>'
    )
    xfs = [
        (0, 0, 0, {}),
        (1, 2, 1, {"horizontal": "center", "vertical": "center"}),
        (2, 3, 1, {"horizontal": "center", "vertical": "center", "wrapText": "1"}),
        (5, 4, 1, {"horizontal": "left", "vertical": "center", "wrapText": "1"}),
        (4, 4, 1, {"horizontal": "left", "vertical": "center", "wrapText": "1"}),
        (0, 0, 1, {"horizontal": "left", "vertical": "center", "wrapText": "1"}),
        (3, 2, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 4, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 5, 1, {"horizontal": "center", "vertical": "center"}),
        (3, 6, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 9, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 7, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 9, 1, {"horizontal": "center", "vertical": "center"}),
        (6, 8, 1, {"horizontal": "center", "vertical": "center"}),
        (4, 11, 1, {"horizontal": "center", "vertical": "center", "wrapText": "1"}),
        (3, 10, 1, {"horizontal": "left", "vertical": "center"}),
        (0, 0, 1, {"horizontal": "left", "vertical": "center", "wrapText": "1"}),
        (0, 0, 1, {"horizontal": "center", "vertical": "center"}),
        (0, 8, 1, {"horizontal": "center", "vertical": "center"}),
        (3, 2, 1, {"horizontal": "left", "vertical": "center"}),
        (4, 12, 1, {"horizontal": "center", "vertical": "center"}),
        (5, 13, 1, {"horizontal": "left", "vertical": "top", "wrapText": "1"}),
        (4, 12, 1, {"horizontal": "center", "vertical": "center", "wrapText": "1"}),
        (6, 13, 1, {"horizontal": "left", "vertical": "top", "wrapText": "1"}),
        (4, 14, 1, {"horizontal": "left", "vertical": "top", "wrapText": "1"}),
        (3, 15, 1, {"horizontal": "left", "vertical": "center"}),
        (3, 16, 1, {"horizontal": "left", "vertical": "center"}),
        (4, 17, 1, {"horizontal": "center", "vertical": "center"}),
    ]

    font_xml = []
    for font in fonts:
        font_xml.append(
            "<font>"
            f'<sz val="{font["size"]}"/>'
            f'<color rgb="{font["color"]}"/>'
            '<name val="Calibri"/>'
            '<family val="2"/>'
            + ("<b/>" if font["bold"] else "")
            + "</font>"
        )

    fill_xml = []
    for fill in fills:
        if fill is None:
            fill_xml.append("<fill><patternFill patternType=\"none\"/></fill>")
        elif fill == "gray125":
            fill_xml.append("<fill><patternFill patternType=\"gray125\"/></fill>")
        else:
            fill_xml.append(
                f'<fill><patternFill patternType="solid"><fgColor rgb="{fill}"/>'
                f'<bgColor rgb="{fill}"/></patternFill></fill>'
            )

    xf_xml = []
    for font_id, fill_id, border_id, alignment in xfs:
        attrs = (
            f'numFmtId="0" fontId="{font_id}" fillId="{fill_id}" borderId="{border_id}" '
            'xfId="0" applyFont="1" applyFill="1" applyBorder="1"'
        )
        if alignment:
            align_attrs = " ".join(f'{key}="{value}"' for key, value in alignment.items())
            xf_xml.append(f"<xf {attrs} applyAlignment=\"1\"><alignment {align_attrs}/></xf>")
        else:
            xf_xml.append(f"<xf {attrs}/>")

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<fonts count="{len(font_xml)}">{"".join(font_xml)}</fonts>'
        f'<fills count="{len(fill_xml)}">{"".join(fill_xml)}</fills>'
        f'<borders count="2">{border_none}{border_thin}</borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        f'<cellXfs count="{len(xf_xml)}">{"".join(xf_xml)}</cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '<dxfs count="0"/>'
        '<tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>'
        "</styleSheet>"
    )


def worksheet_xml(sheet: Worksheet) -> str:
    rows: dict[int, list[tuple[int, Any, int]]] = {}
    for (row, col), (value, style) in sheet.cells.items():
        rows.setdefault(row, []).append((col, value, style))

    sheet_views = ""
    if sheet.frozen_cell:
        sheet_views = (
            "<sheetViews><sheetView workbookViewId=\"0\">"
            f'<pane xSplit="{sheet.x_split}" ySplit="{sheet.y_split}" topLeftCell="{sheet.frozen_cell}" '
            'activePane="bottomRight" state="frozen"/>'
            '<selection pane="bottomRight"/>'
            "</sheetView></sheetViews>"
        )

    cols = ""
    if sheet.col_widths:
        col_items = []
        for col, width in sorted(sheet.col_widths.items()):
            col_items.append(f'<col min="{col}" max="{col}" width="{width}" customWidth="1"/>')
        cols = f"<cols>{''.join(col_items)}</cols>"

    row_items = []
    for row_num in range(1, sheet.max_row + 1):
        values = rows.get(row_num, [])
        if not values and row_num not in sheet.row_heights:
            continue
        height = ""
        if row_num in sheet.row_heights:
            height = f' ht="{sheet.row_heights[row_num]}" customHeight="1"'
        cell_items = []
        for col, value, style in sorted(values):
            ref = cell_ref(row_num, col)
            style_attr = f' s="{style}"' if style else ""
            if isinstance(value, Formula):
                cached = "" if value.cached_value is None else f"<v>{value.cached_value}</v>"
                cell_items.append(f'<c r="{ref}"{style_attr}><f>{xml(value.expression)}</f>{cached}</c>')
            elif isinstance(value, (int, float)):
                cell_items.append(f'<c r="{ref}"{style_attr}><v>{value}</v></c>')
            elif value is None:
                cell_items.append(f'<c r="{ref}"{style_attr}/>')
            else:
                cell_items.append(
                    f'<c r="{ref}" t="inlineStr"{style_attr}><is><t xml:space="preserve">'
                    f"{xml(value)}</t></is></c>"
                )
        row_items.append(f'<row r="{row_num}"{height}>{"".join(cell_items)}</row>')

    merge_xml = ""
    if sheet.merges:
        merge_xml = (
            f'<mergeCells count="{len(sheet.merges)}">'
            + "".join(f'<mergeCell ref="{merge}"/>' for merge in sheet.merges)
            + "</mergeCells>"
        )

    validation_xml = ""
    if sheet.data_validations:
        items = []
        for sqref, formula in sheet.data_validations:
            items.append(
                '<dataValidation type="list" allowBlank="1" showErrorMessage="1" '
                f'sqref="{sqref}"><formula1>{xml(formula)}</formula1></dataValidation>'
            )
        validation_xml = f'<dataValidations count="{len(items)}">{"".join(items)}</dataValidations>'

    dimension = f'A1:{cell_ref(sheet.max_row, sheet.max_col)}'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dimension}"/>'
        f"{sheet_views}{cols}"
        f'<sheetData>{"".join(row_items)}</sheetData>'
        f"{merge_xml}{validation_xml}"
        '<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>'
        "</worksheet>"
    )


def build_visual_sheet() -> Worksheet:
    sheet = Worksheet("Histograma Visual")
    start = date(2026, 1, 1)
    days = [date(2026, 1, day) for day in range(1, 32)]
    day_col = {day: index + 6 for index, day in enumerate(days)}
    last_col = day_col[days[-1]]

    for col, width in {1: 24, 2: 15, 3: 18, 4: 14, 5: 22}.items():
        sheet.set_col_width(col, width)
    for col in range(6, last_col + 1):
        sheet.set_col_width(col, 5.2)
    for row, height in {1: 26, 2: 34, 3: 32, 4: 30, 6: 25, 7: 25, 8: 25, 12: 34}.items():
        sheet.set_row_height(row, height)

    sheet.set(1, 1, "HPrev - Histograma de Mao de Obra e Equipamentos", Styles.TITLE)
    sheet.merge(1, 1, 1, last_col)
    sheet.set(2, 1, "Esboco visual da tabela: cadastro, fases, recursos, quantitativos diarios e totais", Styles.SUBTITLE)
    sheet.merge(2, 1, 2, last_col)
    sheet.set(
        3,
        1,
        "Formulario do histograma: Nome unico | Descricao/subtitulo | Inicio 01/01/2026 | Termino 31/01/2026 | Step 1 dia",
        Styles.INFO,
    )
    sheet.merge(3, 1, 3, last_col)
    sheet.set(
        4,
        1,
        "Legenda: colunas de fim de semana usam fundo diferente; fases nao se sobrepoem; colunas da esquerda podem ser customizadas.",
        Styles.NOTE,
    )
    sheet.merge(4, 1, 4, last_col)
    sheet.set(
        5,
        1,
        "Cabecalho direito: linha 6=dias corridos, 7=dias uteis, 8=fase, 9=dia da fase, 10=mes/ano, 11=dia semana, 12=dia do mes.",
        Styles.NOTE,
    )
    sheet.merge(5, 1, 5, last_col)

    sheet.set(6, 1, "RECURSOS", Styles.RESOURCE_TITLE)
    sheet.merge(6, 1, 6, 5)
    sheet.set(
        7,
        1,
        "+ adicionar secao quando nao houver secoes. Apos criar uma secao, o + aparece no canto direito dela para adicionar recurso.",
        Styles.NOTE,
    )
    sheet.merge(7, 1, 11, 5)

    business_days = 0
    phase_ranges = [
        ("Mobilizacao", date(2026, 1, 1), date(2026, 1, 8)),
        ("Obra Civil", date(2026, 1, 9), date(2026, 1, 23)),
        ("Desmobilizacao", date(2026, 1, 24), date(2026, 1, 31)),
    ]

    for index, day in enumerate(days, start=1):
        col = day_col[day]
        is_weekend = day.weekday() >= 5
        if not is_weekend:
            business_days += 1
        header_style = Styles.WEEKEND_HEADER if is_weekend else Styles.CONTENT_HEADER
        business_style = Styles.WEEKEND_HEADER if is_weekend else Styles.BUSINESS_HEADER
        sheet.set(6, col, index, header_style)
        sheet.set(7, col, business_days, business_style)

    for name, phase_start, phase_end in phase_ranges:
        start_col = day_col[phase_start]
        end_col = day_col[phase_end]
        sheet.set(8, start_col, name, Styles.PHASE_HEADER)
        sheet.merge(8, start_col, 8, end_col)
        for index, day in enumerate(
            [item for item in days if phase_start <= item <= phase_end], start=1
        ):
            sheet.set(9, day_col[day], index, Styles.PHASE_COUNT)

    sheet.set(10, 6, f"{MONTHS_PT[start.month - 1]}/{str(start.year)[-2:]}", Styles.MONTH_HEADER)
    sheet.merge(10, 6, 10, last_col)
    for day in days:
        col = day_col[day]
        style = Styles.WEEKEND_HEADER if day.weekday() >= 5 else Styles.WEEKDAY
        sheet.set(11, col, WEEKDAYS_PT[day.weekday()], style)
        sheet.set(12, col, f"{day.day:02d}", style)

    left_headers = ["Nome do recurso *", "Tipo", "Disciplina", "Turno", "Tags"]
    for col, value in enumerate(left_headers, start=1):
        sheet.set(12, col, value, Styles.LEFT_HEADER)

    resources = [
        (13, "section", "SECAO: MAO DE OBRA                                      [+ recurso]", Styles.SECTION_LABOR),
        (14, "resource", "Encarregado Civil", "Mao de obra", "Civil", "Diurno", "lideranca,campo"),
        (15, "resource", "Pedreiro", "Mao de obra", "Civil", "Diurno", "alvenaria"),
        (16, "resource", "Servente", "Mao de obra", "Civil", "Diurno", "apoio,campo"),
        (17, "partial", "TOTAL PARCIAL - MAO DE OBRA", (14, 16)),
        (18, "section", "SECAO: EQUIPAMENTOS                                  [+ recurso]", Styles.SECTION_EQUIPMENT),
        (19, "resource", "Guindaste 30t", "Equipamento", "Icar", "Diurno", "locado"),
        (20, "resource", "Escavadeira hidraulica", "Equipamento", "Terraplenagem", "Diurno", "proprio"),
        (21, "partial", "TOTAL PARCIAL - EQUIPAMENTOS", (19, 20)),
    ]
    quantity_rows: dict[int, list[int]] = {}
    for item in resources:
        row = item[0]
        row_type = item[1]
        if row_type == "section":
            _, _, label, section_style = item
            sheet.set(row, 1, label, section_style)
            sheet.merge(row, 1, row, 5)
            sheet.set(row, 6, " ", section_style)
            sheet.merge(row, 6, row, last_col)
            continue

        if row_type == "partial":
            _, _, label, (start_row, end_row) = item
            sheet.set(row, 1, label, Styles.TOTAL_LABEL)
            sheet.merge(row, 1, row, 5)
            for index, day in enumerate(days):
                col = day_col[day]
                col_letter = col_name(col)
                cached_total = sum(quantity_rows[resource_row][index] for resource_row in range(start_row, end_row + 1))
                sheet.set(
                    row,
                    col,
                    Formula(f"SUM({col_letter}{start_row}:{col_letter}{end_row})", cached_total),
                    Styles.WEEKEND_QUANTITY if day.weekday() >= 5 else Styles.PARTIAL_TOTAL,
                )
            continue

        _, _, name, kind, discipline, shift, tags = item
        for col, value in enumerate([name, kind, discipline, shift, tags], start=1):
            sheet.set(row, col, value, Styles.RESOURCE)

        values: list[int] = []
        for day in days:
            is_weekend = day.weekday() >= 5
            if name == "Encarregado Civil":
                value = 0 if is_weekend else 1
            elif name == "Pedreiro":
                value = 0 if is_weekend else (4 if day.day < 9 else 8 if day.day < 24 else 3)
            elif name == "Servente":
                value = 0 if is_weekend else (6 if day.day < 9 else 10 if day.day < 24 else 4)
            elif name == "Guindaste 30t":
                value = 0 if is_weekend or day.day < 9 or day.day > 23 else 1
            else:
                value = 0 if is_weekend or day.day > 20 else 1
            values.append(value)
            sheet.set(row, day_col[day], value, Styles.WEEKEND_QUANTITY if is_weekend else Styles.QUANTITY)
        quantity_rows[row] = values

    total_row = 22
    sheet.set(total_row, 1, "TOTAL DE RECURSOS POR DIA", Styles.TOTAL_LABEL)
    sheet.merge(total_row, 1, total_row, 5)
    for index, day in enumerate(days):
        col = day_col[day]
        col_letter = col_name(col)
        cached_total = sum(values[index] for values in quantity_rows.values())
        sheet.set(
            total_row,
            col,
            Formula(f"SUM({col_letter}17,{col_letter}21)", cached_total),
            Styles.WEEKEND_QUANTITY if day.weekday() >= 5 else Styles.TOTAL,
        )

    sheet.set(
        24,
        1,
        "Observacao: o step define o intervalo de exibicao das colunas de dias. Este exemplo usa step=1 para mostrar todos os dias.",
        Styles.NOTE,
    )
    sheet.merge(24, 1, 24, last_col)
    sheet.freeze(13, 6)
    return sheet


def build_registration_sheet() -> Worksheet:
    sheet = Worksheet("Cadastro Histograma")
    for col, width in {1: 26, 2: 28, 3: 18, 4: 18, 5: 44}.items():
        sheet.set_col_width(col, width)
    sheet.set_row_height(1, 26)
    sheet.set(1, 1, "Formulario de Cadastro do Histograma", Styles.TITLE)
    sheet.merge(1, 1, 1, 5)

    fields = [
        ("Nome do histograma *", "HPrev - Histograma Exemplo", "Deve ser unique no sistema."),
        ("Descricao / subtitulo", "Esboco visual para validacao do produto", "Aparece abaixo do titulo."),
        ("Data de inicio", "01/01/2026", "Inicio do periodo do histograma."),
        ("Data de termino", "31/01/2026", "Fim do periodo do histograma."),
        ("Step (dias)", 1, "Intervalo de dias exibido na tabela gerada."),
    ]
    for row, (label, value, note) in enumerate(fields, start=3):
        sheet.set(row, 1, label, Styles.FORM_LABEL)
        sheet.set(row, 2, value, Styles.FORM_VALUE)
        sheet.set(row, 3, note, Styles.NOTE)
        sheet.merge(row, 3, row, 5)

    sheet.set(10, 1, "Fases do Projeto", Styles.RESOURCE_TITLE)
    sheet.merge(10, 1, 10, 5)
    headers = ["Nome da fase *", "Data inicio", "Data fim", "Validacao", "Observacoes"]
    for col, value in enumerate(headers, start=1):
        sheet.set(11, col, value, Styles.TABLE_HEADER)
    phases = [
        ("Mobilizacao", "01/01/2026", "08/01/2026", "OK", "Dentro do periodo e sem sobreposicao."),
        ("Obra Civil", "09/01/2026", "23/01/2026", "OK", "Nome unico no escopo do histograma."),
        ("Desmobilizacao", "24/01/2026", "31/01/2026", "OK", "Contagem da fase reinicia no cabecalho."),
    ]
    for row, phase in enumerate(phases, start=12):
        for col, value in enumerate(phase, start=1):
            sheet.set(row, col, value, Styles.OK if col == 4 else Styles.FORM_VALUE)

    sheet.set(17, 1, "Secoes de Recursos", Styles.RESOURCE_TITLE)
    sheet.merge(17, 1, 17, 5)
    section_headers = ["Nome da secao *", "Cor do header", "Ordem", "Validacao", "Observacoes"]
    for col, value in enumerate(section_headers, start=1):
        sheet.set(18, col, value, Styles.TABLE_HEADER)
    section_rows = [
        ("MAO DE OBRA", "#0F766E", 1, "OK", "Cor configuravel pelo usuario no cadastro/edicao da secao."),
        ("EQUIPAMENTOS", "#7C2D12", 2, "OK", "Cada secao deve ter header visualmente distinto."),
    ]
    for row, section in enumerate(section_rows, start=19):
        for col, value in enumerate(section, start=1):
            sheet.set(row, col, value, Styles.OK if col == 4 else Styles.FORM_VALUE)

    sheet.set(23, 1, "Colunas Customizaveis dos Recursos", Styles.RESOURCE_TITLE)
    sheet.merge(23, 1, 23, 5)
    custom_headers = ["Nome da coluna", "Tipo", "Obrigatoria?", "Opcoes pre-definidas", "Exemplo"]
    for col, value in enumerate(custom_headers, start=1):
        sheet.set(24, col, value, Styles.TABLE_HEADER)
    custom_rows = [
        ("Tipo", "dropdown", "Nao", "Mao de obra; Equipamento", "Mao de obra"),
        ("Disciplina", "dropdown", "Nao", "Civil; Icar; Terraplenagem", "Civil"),
        ("Turno", "dropdown", "Nao", "Diurno; Noturno", "Diurno"),
        ("Tags", "tags", "Nao", "Lista livre de tags", "lideranca,campo"),
        ("Observacoes", "string", "Nao", "", "Texto ou numero livre"),
    ]
    for row, values in enumerate(custom_rows, start=25):
        for col, value in enumerate(values, start=1):
            sheet.set(row, col, value, Styles.FORM_VALUE)
    sheet.data_validations.append(("B25:B36", '"string,dropdown,tags"'))
    sheet.data_validations.append(("C25:C36", '"Sim,Nao"'))

    sheet.set(
        32,
        1,
        "Regra: a coluna Nome do recurso e fixa, obrigatoria e nao pode ser alterada. As demais podem ser adicionadas/removidas pelo usuario.",
        Styles.WARNING,
    )
    sheet.merge(32, 1, 32, 5)
    return sheet


def build_auxiliary_sheet() -> Worksheet:
    sheet = Worksheet("Dados Auxiliares")
    for col, width in {1: 24, 2: 24, 3: 30, 4: 38}.items():
        sheet.set_col_width(col, width)
    sheet.set(1, 1, "Dados auxiliares para prototipacao", Styles.TITLE)
    sheet.merge(1, 1, 1, 4)
    headers = ["Secao", "Recurso", "Tipo", "Notas"]
    for col, value in enumerate(headers, start=1):
        sheet.set(3, col, value, Styles.TABLE_HEADER)
    rows = [
        ("MAO DE OBRA", "Encarregado Civil", "Mao de obra", "Exemplo de recurso com quantidade diaria 1 em dias uteis."),
        ("MAO DE OBRA", "Pedreiro", "Mao de obra", "Quantidade varia por fase."),
        ("MAO DE OBRA", "Servente", "Mao de obra", "Quantidade varia por fase."),
        ("EQUIPAMENTOS", "Guindaste 30t", "Equipamento", "Ativo apenas durante a fase Obra Civil."),
        ("EQUIPAMENTOS", "Escavadeira hidraulica", "Equipamento", "Exemplo de equipamento proprio."),
    ]
    for row, values in enumerate(rows, start=4):
        for col, value in enumerate(values, start=1):
            sheet.set(row, col, value, Styles.FORM_VALUE)

    sheet.set(11, 1, "Cores customizaveis por secao", Styles.RESOURCE_TITLE)
    sheet.merge(11, 1, 11, 4)
    color_rows = [
        ("MAO DE OBRA", "#0F766E", "Verde petroleo", "Exemplo de cor inicial configurada pelo usuario."),
        ("EQUIPAMENTOS", "#7C2D12", "Marrom", "Exemplo de cor inicial configurada pelo usuario."),
    ]
    for row, values in enumerate(color_rows, start=12):
        for col, value in enumerate(values, start=1):
            sheet.set(row, col, value, Styles.FORM_VALUE if col > 1 else Styles.FORM_LABEL)

    sheet.set(16, 1, "Opcoes de dropdown sugeridas", Styles.RESOURCE_TITLE)
    sheet.merge(16, 1, 16, 4)
    options = [
        ("Tipo", "Mao de obra", "Equipamento", ""),
        ("Disciplina", "Civil", "Icar", "Terraplenagem"),
        ("Turno", "Diurno", "Noturno", ""),
        ("Tags", "lideranca", "campo", "locado; proprio; apoio"),
    ]
    for row, values in enumerate(options, start=17):
        for col, value in enumerate(values, start=1):
            sheet.set(row, col, value, Styles.FORM_VALUE if col > 1 else Styles.FORM_LABEL)
    return sheet


def build_rules_sheet() -> Worksheet:
    sheet = Worksheet("Regras e Validacoes")
    for col, width in {1: 28, 2: 92}.items():
        sheet.set_col_width(col, width)
    sheet.set(1, 1, "Regras funcionais representadas na planilha", Styles.TITLE)
    sheet.merge(1, 1, 1, 2)
    rules = [
        ("Histograma", "Nome do histograma deve ser unico e usado como titulo; descricao aparece como subtitulo."),
        ("Periodo", "Data de inicio e data de termino definem o range permitido para todo o cabecalho de dias."),
        ("Fases", "Cada fase possui nome unico dentro do histograma, fica dentro do periodo e nao pode sobrepor outra fase."),
        ("Step", "Controla de quantos em quantos dias a tabela exibe colunas no histograma gerado."),
        ("Cabecalho direito", "Exibe dias corridos, dias uteis decorridos, fase, contagem do dia da fase, mes/ano, dia da semana e dia do mes."),
        ("Recursos", "Recursos pertencem a secoes. O botao + cria a primeira secao ou adiciona recurso dentro de uma secao existente."),
        ("Colunas fixas", "Nome do recurso e fixo, obrigatorio e nao editavel."),
        ("Colunas customizadas", "Usuario pode adicionar/remover colunas string, dropdown com opcoes pre-definidas ou tags."),
        ("Quantitativos", "Cada recurso recebe uma quantidade por dia no corpo direito do histograma."),
        ("Totais parciais", "Cada secao possui uma linha de total parcial que soma os quantitativos diarios dos recursos daquela secao."),
        ("Total geral", "Linha final soma os totais parciais das secoes para cada dia."),
        ("Cores de secao", "Cada header de secao possui cor de fundo distinta e customizavel pelo usuario."),
        ("Fim de semana", "Colunas de sabado e domingo usam fundo levemente diferente."),
    ]
    sheet.set(3, 1, "Area", Styles.TABLE_HEADER)
    sheet.set(3, 2, "Regra", Styles.TABLE_HEADER)
    for row, (area, rule) in enumerate(rules, start=4):
        sheet.set(row, 1, area, Styles.FORM_LABEL)
        sheet.set(row, 2, rule, Styles.NOTE)

    sheet.set(20, 1, "Legenda visual", Styles.RESOURCE_TITLE)
    sheet.merge(20, 1, 20, 2)
    legend = [
        ("Azul escuro", "Titulo, RECURSOS e totais/secoes principais."),
        ("Roxo", "Linha de nome das fases."),
        ("Laranja claro", "Fim de semana."),
        ("Verde claro", "Dias uteis decorridos e status OK."),
        ("Amarelo claro", "Avisos e observacoes de validacao."),
    ]
    for row, (color, meaning) in enumerate(legend, start=21):
        sheet.set(row, 1, color, Styles.FORM_LABEL)
        sheet.set(row, 2, meaning, Styles.NOTE)
    return sheet


def workbook_xml(sheets: list[Worksheet]) -> str:
    sheet_entries = []
    for index, sheet in enumerate(sheets, start=1):
        sheet_entries.append(
            f'<sheet name="{xml(sheet.name)}" sheetId="{index}" r:id="rId{index}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<bookViews><workbookView xWindow="0" yWindow="0" windowWidth="20000" windowHeight="12000"/></bookViews>'
        f'<sheets>{"".join(sheet_entries)}</sheets>'
        '<calcPr calcId="0" fullCalcOnLoad="1"/>'
        "</workbook>"
    )


def workbook_rels_xml(sheets: list[Worksheet]) -> str:
    rels = []
    for index, _ in enumerate(sheets, start=1):
        rels.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    rels.append(
        f'<Relationship Id="rId{len(sheets) + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{"".join(rels)}</Relationships>'
    )


def content_types_xml(sheets: list[Worksheet]) -> str:
    overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for index, _ in enumerate(sheets, start=1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'{"".join(overrides)}</Types>'
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def core_xml() -> str:
    timestamp = datetime(*ZIP_TIMESTAMP, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:creator>Cursor Cloud Agent</dc:creator>"
        "<cp:lastModifiedBy>Cursor Cloud Agent</cp:lastModifiedBy>"
        "<dc:title>HPrev - Esboco Visual de Histograma</dc:title>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>'
        "</cp:coreProperties>"
    )


def app_xml(sheets: list[Worksheet]) -> str:
    titles = "".join(f"<vt:lpstr>{xml(sheet.name)}</vt:lpstr>" for sheet in sheets)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        "<Application>Python</Application>"
        "<DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop>"
        '<HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>'
        f'<vt:variant><vt:i4>{len(sheets)}</vt:i4></vt:variant></vt:vector></HeadingPairs>'
        f'<TitlesOfParts><vt:vector size="{len(sheets)}" baseType="lpstr">{titles}</vt:vector></TitlesOfParts>'
        "</Properties>"
    )


def write_xlsx(sheets: list[Worksheet]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    def write_part(archive: ZipFile, filename: str, content: str) -> None:
        info = ZipInfo(filename, ZIP_TIMESTAMP)
        info.compress_type = ZIP_DEFLATED
        archive.writestr(info, content)

    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        write_part(archive, "[Content_Types].xml", content_types_xml(sheets))
        write_part(archive, "_rels/.rels", root_rels_xml())
        write_part(archive, "docProps/core.xml", core_xml())
        write_part(archive, "docProps/app.xml", app_xml(sheets))
        write_part(archive, "xl/workbook.xml", workbook_xml(sheets))
        write_part(archive, "xl/_rels/workbook.xml.rels", workbook_rels_xml(sheets))
        write_part(archive, "xl/styles.xml", styles_xml())
        for index, sheet in enumerate(sheets, start=1):
            write_part(archive, f"xl/worksheets/sheet{index}.xml", worksheet_xml(sheet))


def main() -> None:
    sheets = [
        build_visual_sheet(),
        build_registration_sheet(),
        build_auxiliary_sheet(),
        build_rules_sheet(),
    ]
    write_xlsx(sheets)
    print(f"Planilha gerada em: {OUTPUT}")


if __name__ == "__main__":
    main()
