#!/bin/bash

if [ -z "$LATEX_COMPILER" ]; then
    LATEX_COMPILER="lualatex"
fi

output_path=$(resume_converter "$@" | tail -n 1)

if [ -f "$output_path" ]; then
    dir=$(dirname "$output_path")
    file=$(basename "$output_path")
    
    if [ "$dir" != "." ]; then
        cd "$dir" || { echo "Failed to change directory to $dir"; exit 1; }
        output_path="$file"
    fi

    "$LATEX_COMPILER" "$output_path"
    if [ $? -eq 0 ]; then
        echo "The file '$output_path' was successfully compiled."

        output_path_no_ext="${output_path%.tex}"
        extensions_to_remove=("aux" "log" "out" "synctex.gz")
        for ext in "${extensions_to_remove[@]}"; do
            if [ -f "$output_path_no_ext.$ext" ]; then
                rm "$output_path_no_ext.$ext"
                echo "The file '$output_path_no_ext.$ext' was removed."
            fi
        done
        
    else
        echo "An error occurred while compiling the file '$output_path'."
    fi
else
    echo "The file '$output_path' does not exist."
fi
