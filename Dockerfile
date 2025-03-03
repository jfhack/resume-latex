FROM python:3.11-slim-bookworm
LABEL org.opencontainers.image.source=https://github.com/jfhack/resume-latex

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install texlive-full -y

RUN useradd -rm -s /bin/bash -G sudo -u 1000 dev
RUN mkdir /data
ADD headers /headers
RUN chown dev:dev /data
ADD resume_converter.py /bin/resume_converter
ADD entry.sh /entry.sh
RUN chmod +x /entry.sh
USER dev
RUN luaotfload-tool --update
WORKDIR /data
ENTRYPOINT ["/entry.sh"]
