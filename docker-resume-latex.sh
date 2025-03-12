#!/bin/bash

docker run --rm -it -v ./headers:/headers -v ./data:/data ghcr.io/jfhack/resume-latex "$@"
