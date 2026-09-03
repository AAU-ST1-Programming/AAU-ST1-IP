from pathlib import Path
from textwrap import wrap

import pandas as pd
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "shared_overview.csv"
HTML_PATH_TEMPLATE = "shared_overview_table{table_number}.html"
PNG_PATH_TEMPLATE = "shared_overview_table{table_number}.png"
COLUMN_WIDTHS = [40, 130, 110, 420]
ROW_LINE_HEIGHT = 24
# rough chars-per-line for the widest column, used only to size rows tall enough
LAST_COLUMN_CHARS_PER_LINE = 65


def build_df() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH, sep="|")


def build_html(df: pd.DataFrame) -> dict[int, str]:
    html_by_index: dict[int, str] = {}
    for i in range(0, len(df) + 1):
        styled = (
            df.style.set_uuid("shared_overview")
            .apply(
                lambda row: (
                    ["font-weight: 1000; background-color: #e8f1f5"] * len(row)
                    if str(row["#"]) == str(i)
                    else [""] * len(row)
                ),
                axis=1,
            )
            .hide(axis="index")
        )
        html_by_index[i] = styled.to_html()
    return html_by_index


def path_from_template(table_number: str) -> Path:
    return BASE_DIR / HTML_PATH_TEMPLATE.format(table_number=table_number)


def png_path_from_template(table_number: str) -> Path:
    return BASE_DIR / PNG_PATH_TEMPLATE.format(table_number=table_number)


def build_png(df: pd.DataFrame, highlighted_row: int = -1) -> bytes:
    is_highlighted = (df["#"].astype(str) == str(highlighted_row)).to_numpy()
    row_fill = ["#e8f1f5" if flag else "white" for flag in is_highlighted]

    topics_column = df.columns[-1]
    line_counts = [
        max(1, len(wrap(str(value), width=LAST_COLUMN_CHARS_PER_LINE)))
        for value in df[topics_column]
    ]
    header_height = 28

    figure = go.Figure(
        data=[
            go.Table(
                columnwidth=COLUMN_WIDTHS,
                header=dict(
                    values=list(df.columns),
                    fill_color="#263238",
                    font=dict(color="white", size=12, weight=700),
                    align="left",
                    height=header_height,
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color=[row_fill],
                    font=dict(color="black", size=11),
                    align="left",
                    height=ROW_LINE_HEIGHT,
                ),
            )
        ]
    )

    figure.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        width=sum(COLUMN_WIDTHS) + 40,
        height=ROW_LINE_HEIGHT * (sum(line_counts) - 1),
    )
    return figure.to_image(format="png", scale=2)


def write_if_changed(output_path: Path, content: str | bytes) -> bool:
    if output_path.exists():
        existing = (
            output_path.read_bytes()
            if isinstance(content, bytes)
            else output_path.read_text(encoding="utf-8")
        )
        if existing == content:
            return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        output_path.write_bytes(content)
    else:
        output_path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    df = build_df()
    png_path = png_path_from_template("")
    changed = write_if_changed(png_path, build_png(df, -1))


if __name__ == "__main__":
    main()
