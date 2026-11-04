#!/bin/bash

docker run --rm -it --network none -v ./headers:/headers:ro -v ./data:/data ghcr.io/jfhack/resume-latex "$@"
