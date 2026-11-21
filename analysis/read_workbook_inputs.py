"""Read saved editable inputs without evaluating or changing Excel formulas."""
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
NS={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def main():
    with (ROOT/"data/assumptions.csv").open(newline="") as stream:
        rows=list(csv.DictReader(stream))
    with ZipFile(ROOT/"models/5G_Investment_Financial_Model.xlsx") as book:
        # The final workbook's second sheet is Assumptions; verify before reading.
        workbook=ET.fromstring(book.read("xl/workbook.xml"))
        names=[s.attrib["name"] for s in workbook.find("s:sheets",NS)]
        assert names[1]=="Assumptions", "Unexpected workbook order"
        sheet=ET.fromstring(book.read("xl/worksheets/sheet2.xml"))
        cells={c.attrib["r"]:c for c in sheet.findall(".//s:c",NS)}
        for row in rows:
            cell=cells[f"B{row['excel_row']}"]
            assert cell.find("s:f",NS) is None, "Expected an editable numeric input"
            row["value"]=float(cell.find("s:v",NS).text)
    target=ROOT/"outputs/workbook_inputs.csv"
    with target.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print(f"Saved {target.relative_to(ROOT)}. Review before changing the baseline CSV.")


if __name__=="__main__":main()
