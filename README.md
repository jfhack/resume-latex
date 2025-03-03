# Resume Markdown To LaTeX

A simple Python script to convert Markdown files into LaTeX documents with resume/CV formatting.  
This approach keeps your resume in an easy-to-edit format that is also simpler to translate and process.

---

## Usage

To convert a Markdown file into a LaTeX file, run:

```sh
./resume_converter.py ./data/sample.md
```

This command creates a `./data/sample.tex` file. Next, compile the LaTeX file with `lualatex` or `pdflatex`:

```sh
cd ./data
lualatex sample.tex
```

The resulting output will be a `sample.pdf` file

---

## Arguments

| Argument | | Description |
|---|---|---|
| (Required) || path to the input Markdown (`.md`) file |
| -o OUTPUT | --output OUTPUT | specify the output LaTeX file path. <br> _Default: Uses the input filename with a `.tex` extension._ |
| -e INPUT  | --extra-header INPUT | path to a file whose contents will be inserted as extra lines in the final LaTeX document before the `\begin{document}` command |

---

## Considerations

- The input `.md` file supports a mix of Markdown and LaTeX.
- Any content that is not Markdown is treated as LaTeX.  
  **Note:** Certain characters must be escaped in Markdown to avoid misinterpretation by LaTeX. For example:
  - hash: `#` → `\#`
  - dollar: `$` → `\$`
  - ampersand: `&` → `\&`

---

## Supported Markdown

The following Markdown syntax is supported and converted into LaTeX commands:

| Markdown Syntax                | Description                                      | LaTeX Command       |
|--------------------------------|--------------------------------------------------|---------------------|
| `**text in bold**`             | bold text                                        | `\textbf{...}`      |
| `*text in italic*`             | italic text                                      | `\emph{...}`        |
| `[link text](https://the.url)` | hyperlink                                        | `\href{...}{...}`   |
| `# user name`                  | resume title & name (only one, at the beginning) | `\Huge{...}`        |
| `## section`                   | section header                                   | `\section{...}`     |
| `- item` or `* item`           | bullet list (supports nesting)                   | `\begin{itemize} ... \end{itemize}` |
| `\|----\|:----:\|`             | table with column alignment                      | `\begin{tabular} ... \end{tabular}` |

Any content not matching the supported Markdown will be passed directly as LaTeX. For example, content following a `%` is treated as a comment in LaTeX and will not be rendered unless escaped as `\%`.

---

## Docker

This tool can be executed using Docker, eliminating the need to install all dependencies locally. The working directory is mounted to `/data` in the container, and any provided arguments are passed directly to the script.

The Docker image includes both `lualatex` and `pdflatex`, which enables immediate conversion of a Markdown file to PDF.

- **Default Compiler:** `lualatex` is used by default.
- **Alternate Compiler:** To use `pdflatex`, the `LATEX_COMPILER` environment variable should be set accordingly.

For example, after cloning the repository, the following command converts the example file `sample.md`:

```sh
docker run --rm -it -v ./data:/data ghcr.io/jfhack/resume-latex sample.md
```

Upon execution, the `./data` directory will contain both `sample.tex` and `sample.pdf`.

This configuration also permits the maintenance of multiple Markdown versions for different job applications or languages (e.g., `resume.fr.md`, `resume.ru.md`, `resume.pangeasoftware.md`, etc.), allowing for quick updates when required.
