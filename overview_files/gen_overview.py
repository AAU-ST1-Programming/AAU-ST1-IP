from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "shared_overview.csv"
HTML_PATH_TEMPLATE = "shared_overview_table{table_name}.html"
PNG_PATH_TEMPLATE = "shared_overview_table{table_name}.png"


def build_df() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH, sep="|")


def build_html(df: pd.DataFrame) -> dict[int, str]:
    html_by_index: dict[int, str] = {}
    for i in range(1, len(df) + 1):
        styled = (
            df.style.set_uuid("shared_overview")
            .apply(
                lambda row: (
                    ["font-weight: 1000"] * len(row)
                    if row["#"] == i
                    else [""] * len(row)
                ),
                axis=1,
            )
            .hide(axis="index")
        )
        html_by_index[i] = styled.to_html()
    return html_by_index


def path_from_template(table_name: str) -> Path:
    return BASE_DIR / HTML_PATH_TEMPLATE.format(table_name=table_name)


def png_path_from_template(table_name: str) -> Path:
    return BASE_DIR / PNG_PATH_TEMPLATE.format(table_name=table_name)


def build_png(df: pd.DataFrame, highlighted_row: int) -> bytes:
    figure, axis = plt.subplots(figsize=(14, 1.35), dpi=180)
    axis.axis("off")
    table = axis.table(
        cellText=df.astype(str).values.tolist(),
        colLabels=list(df.columns),
        colWidths=[0.06, 0.18, 0.16, 0.60],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)

    for column in range(len(df.columns)):
        header = table[0, column]
        header.set_facecolor("#263238")
        header.set_text_props(color="white", weight="bold")

    for row in range(1, len(df) + 1):
        for column in range(len(df.columns)):
            cell = table[row, column]
            is_highlighted = df.iloc[row - 1]["#"] == highlighted_row
            cell.set_facecolor("#e8f1f5" if is_highlighted else "white")
            if is_highlighted:
                cell.set_text_props(weight="bold")
            cell.set_edgecolor("#b0bec5")

    output = BytesIO()
    figure.savefig(output, format="png", bbox_inches="tight", pad_inches=0.08)
    plt.close(figure)
    return output.getvalue()


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
    html_by_index = build_html(df)

    for i, html_content in html_by_index.items():
        table_name = str(i)
        html_path = path_from_template(table_name)
        changed = write_if_changed(html_path, html_content)

        if changed:
            print(f"Updated {html_path}")
        else:
            print(f"No changes in {html_path}")

        png_path = png_path_from_template(table_name)
        changed = write_if_changed(png_path, build_png(df, i))

        if changed:
            print(f"Updated {png_path}")
        else:
            print(f"No changes in {png_path}")


if __name__ == "__main__":
    main()
