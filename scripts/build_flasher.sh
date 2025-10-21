#!/bin/bash
docker build -t nuitka .
docker run -it -v "$(pwd):/src/" -w "/src" -e LDFLAGS="-static " nuitka nuitka --standalone --onefile --include-module=yaml flash.py
