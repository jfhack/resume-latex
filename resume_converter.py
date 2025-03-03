#!/usr/bin/env python3
import argparse, re
from pathlib import Path

class Converter:
    def convert_inline(self, text):
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'\*(.+?)\*', r'\\emph{\1}', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\\href{\2}{\1}', text)
        return text

    def extract_header_and_content(self, md_lines):
        header_name = ""
        header_details = []
        content_lines = []
        in_header = True
        for line in md_lines:
            stripped = line.strip()
            if in_header:
                if not header_name and stripped.startswith("# "):
                    header_name = stripped[2:].strip()
                elif stripped.startswith("##"):
                    in_header = False
                    content_lines.append(line)
                elif stripped != "":
                    header_details.append(stripped)
                elif not stripped and header_details:
                    in_header = False
            else:
                content_lines.append(line)
        return header_name, header_details, content_lines

    def convert_table(self, table_lines):
        def split_row(row):
            row = row.strip()
            if row.startswith("|"): row = row[1:]
            if row.endswith("|"): row = row[:-1]
            return [cell.strip() for cell in row.split("|")]
        
        if len(table_lines) < 2: return table_lines

        header_cells = [self.convert_inline(cell) for cell in split_row(table_lines[0])]
        alignment_cells = split_row(table_lines[1])
        data_rows = [[self.convert_inline(cell) for cell in split_row(row)] for row in table_lines[2:]]
        col_align = []

        for cell in alignment_cells:
            if cell.startswith(":") and cell.endswith(":"): col_align.append("c")
            elif cell.endswith(":"): col_align.append("r")
            elif cell.startswith(":"): col_align.append("l")
            else: col_align.append("l")

        col_spec = "".join(col_align)
        latex_table = ["\\begin{tabular}{" + col_spec + "}", "\\hline"]
        latex_table.append(" & ".join(header_cells) + " \\\\")
        latex_table.append("\\hline")

        for row in data_rows:
            latex_table.append(" & ".join(row) + " \\\\")

        latex_table.append("\\hline")
        latex_table.append("\\end{tabular}")

        return latex_table

    def convert_content_lines(self, md_lines):
        latex_lines = []
        list_stack = []
        i, n = 0, len(md_lines)

        while i < n:
            line = md_lines[i].rstrip("\n")
            if line.strip() == "":
                while list_stack:
                    latex_lines.append("  " * len(list_stack) + "\\end{itemize}")
                    list_stack.pop()
                latex_lines.append("")
                i += 1
                continue
            if line.lstrip().startswith("|") and (i+1 < n):
                next_line = md_lines[i+1].rstrip("\n")
                if re.match(r'^\s*\|?[\s:-]+\|[\s|:-]*$', next_line):
                    table_lines = []
                    while i < n and md_lines[i].lstrip().startswith("|"):
                        table_lines.append(md_lines[i].rstrip("\n"))
                        i += 1
                    latex_lines.extend(self.convert_table(table_lines))
                    continue
            heading_match = re.match(r'^(#{2,6})\s*(.+)$', line)
            if heading_match:
                while list_stack:
                    latex_lines.append("  " * len(list_stack) + "\\end{itemize}")
                    list_stack.pop()
                level = len(heading_match.group(1))
                header_text = self.convert_inline(heading_match.group(2).strip())
                if level == 2:
                    latex_lines.append("\\section*{" + header_text + "}")
                elif level == 3:
                    latex_lines.append("\\subsection*{" + header_text + "}")
                else:
                    latex_lines.append("\\paragraph{" + header_text + "}")
                i += 1
                continue
            bullet_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)

            if bullet_match:
                indent_str = bullet_match.group(1)
                item_text = bullet_match.group(2).strip()
                current_indent = len(indent_str)
                if not list_stack:
                    list_stack.append(current_indent)
                    latex_lines.append("  " * len(list_stack) + "\\begin{itemize}")
                else:
                    if current_indent > list_stack[-1]:
                        list_stack.append(current_indent)
                        latex_lines.append("  " * len(list_stack) + "\\begin{itemize}")
                    elif current_indent < list_stack[-1]:
                        while list_stack and current_indent < list_stack[-1]:
                            latex_lines.append("  " * len(list_stack) + "\\end{itemize}")
                            list_stack.pop()
                latex_lines.append("  " * len(list_stack) + "\\item " + self.convert_inline(item_text))
                i += 1
                continue
            while list_stack:
                latex_lines.append("  " * len(list_stack) + "\\end{itemize}")
                list_stack.pop()
            latex_lines.append(self.convert_inline(line))
            i += 1
        while list_stack:
            latex_lines.append("  " * len(list_stack) + "\\end{itemize}")
            list_stack.pop()
        return latex_lines

    def convert(self, input_path, output_path, extra_header_path=None):
        try:
            md_lines = input_path.read_text(encoding='utf-8').splitlines()
        except IOError:
            print("Error reading file:", input_path)
            exit(1)
        header_name, header_details, content_lines = self.extract_header_and_content(md_lines)
        content_latex = self.convert_content_lines(content_lines)
        extra_header_lines = []
        if extra_header_path:
            try:
                extra_header_lines = extra_header_path.read_text(encoding='utf-8').splitlines()
            except IOError:
                print("Error reading file:", extra_header_path)
                exit(2)
        preamble = [
            "\\documentclass[12pt,a4paper]{article}",
            "\\usepackage[margin=1in]{geometry}",
            "\\usepackage{parskip}",
            "\\usepackage[hidelinks]{hyperref}",
            *extra_header_lines,
            "\\begin{document}"
        ]
        header_block = ["\\begin{center}",
                        "    \\textbf{\\Huge " + header_name + "} \\\\[0.2cm]"]
        header_detail_lines = []
        for detail in header_details:
            if "@" in detail and not detail.startswith("\\href"):
                detail = "\\href{mailto:" + detail + "}{" + detail + "}"
            header_detail_lines.append(detail)
        header_block.append("    " + " \\\\[0.2cm]\n    ".join(header_detail_lines))
        header_block.append("\\end{center}")
        ending = ["\\end{document}"]

        with output_path.open('w', encoding='utf-8') as f:
            for line in preamble: f.write(line + "\n")
            for line in header_block: f.write(line + "\n")
            for line in content_latex: f.write(line + "\n")
            for line in ending: f.write(line + "\n")

        print(f"Converted \n{output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output LaTeX file")
    parser.add_argument("-e", "--extra-header", help="File that contains extra LaTeX lines before \\begin{document}")

    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix('.tex')
    extra_header_path = Path(args.extra_header) if args.extra_header else None
    converter = Converter()
    converter.convert(input_path, output_path, extra_header_path)

if __name__ == '__main__':
    main()
