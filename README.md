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
| -n | --no-hyphenpenalty | omit the `\hyphenpenalty=10000` line. <br> _Default: the line is added just before `\begin{document}` to prevent words from being hyphenated._ |
| -x | --exhyphenpenalty | also add `\exhyphenpenalty=10000`, which additionally prevents line breaks at explicit hyphens, e.g. `state-of-the-art`. <br> _Default: not added, since forbidding those breaks can push long hyphenated words into the margin._ |

---

## Considerations

- The input `.md` file supports a mix of Markdown and LaTeX.
- Any content that is not Markdown is treated as LaTeX.  
  **Note:** Certain characters must be escaped in Markdown to avoid misinterpretation by LaTeX. For example:
  - hash: `#` → `\#`
  - dollar: `$` → `\$`
  - ampersand: `&` → `\&`

---

## Security

The input is a **mix of Markdown and raw LaTeX**, so any LaTeX you write in the
`.md` file is compiled as-is. That is the feature that lets you drop in
`\hfill`, tables, `\footnote`, and so on. Because the LaTeX engine is a full
programming environment, only compile resume files **you trust**. Treat a `.md`
file, or any file you pass to `-e/--extra-header`, the same way you would treat
a script you are about to run.

When you build through Docker, an untrusted document is contained on two levels:

- **Compiler sandbox** (`entry.sh`, applied to every compile). The engine runs
  with `-no-shell-escape`, so `\write18` cannot spawn shell commands (in LuaTeX
  this also disables `os.execute` and `io.popen`). It runs with `openout_any=p`,
  so it can only write inside the working directory, never an absolute or parent
  path. For LuaTeX it also runs with `--nosocket`, so `\directlua` cannot open a
  network connection.
- **Container sandbox** (`docker-resume-latex.sh`). The image runs as a
  non-root user, with `--network none`, and mounts only `./data` (read-write,
  for your output) and `./headers` (read-only).

A LaTeX document can still read a file into the PDF with `\input`, or write a
file inside the output directory. Removing that would mean losing the
Markdown-plus-LaTeX feature, so the container sandbox is what keeps it safe:
reads only reach the public image and the files you mounted, writes stay in your
output directory, and nothing can reach the network or the rest of your machine.
Prefer the Docker path for any resume you did not write yourself. If you run
`lualatex` or `pdflatex` directly on your host instead, you lose that
containment and reads and writes hit your real filesystem, so pass at least
`-no-shell-escape` and treat the input as code.

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
| two empty lines                | extra vertical space between blocks              | `\vspace{\baselineskip}`            |

A single empty line is just a paragraph break, as in Markdown. Each **additional** consecutive empty line adds one `\vspace{\baselineskip}`, so three empty lines produce two of them. Empty lines at the very beginning or the very end of the content are ignored.

Any content not matching the supported Markdown will be passed directly as LaTeX. For example, content following a `%` is treated as a comment in LaTeX and will not be rendered unless escaped as `\%`.

---

## Docker

This tool can be executed using Docker, eliminating the need to install all dependencies locally. The working directory is mounted to `/data` in the container, and any provided arguments are passed directly to the script.

The Docker image includes both `lualatex` and `pdflatex`, which enables immediate conversion of a Markdown file to PDF.

- **Default Compiler:** `lualatex` is used by default.
- **Alternate Compiler:** To use `pdflatex`, the `LATEX_COMPILER` environment variable should be set accordingly.

For example, after cloning the repository, the following command converts the example file `sample.md`:

```sh
docker run --rm -it --network none -v ./data:/data ghcr.io/jfhack/resume-latex sample.md
```

Upon execution, the `./data` directory will contain both `sample.tex` and `sample.pdf`.

This configuration also permits the maintenance of multiple Markdown versions for different job applications or languages e.g., `fr/resume.md`, `ru/resume.md`, `pangeasoftware/resume.md`, etc., allowing for quick updates when required.

Alternatively, the following script can be used to execute the above command in a simplified manner

```sh
./docker-resume-latex.sh sample.md
```

```sh
./docker-resume-latex.sh fr/resume.md
```

```sh
./docker-resume-latex.sh -e /headers/russian.txt ru/resume.md
```

Which will work with the files inside `./data`

> [!TIP]
> If you use any automated tool like ChatGPT to process the content of the Markdown document, it is important to specify that the content is mixed, i.e. Markdown and LaTeX, and that it should preserve escaped characters like `\\`, `\#`, `\&` and so on
