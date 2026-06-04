# dev.just — Development tasks imported by root Justfile

root_dir := justfile_directory() / ".." / ".."

# Watch for file changes and run tests
watch:
    @echo "==> Watching for changes..."
    @while true; do
        inotifywait -r -e modify python/src python/tests 2>/dev/null || \
        fswatch -1 python/src python/tests 2>/dev/null || \
        { echo "Install inotify-tools or fswatch for watch mode"; exit 1; }
        python3 "{{root_dir}}/scripts/python/test.py"
    done

# Format code with black + isort
format:
    @echo "==> Formatting code"
    python3 -m black python/src python/tests python/scripts 2>/dev/null || \
        { echo "black not installed. Run: pip install black"; exit 1; }
    python3 -m isort python/src python/tests python/scripts 2>/dev/null || \
        { echo "isort not installed. Run: pip install isort"; exit 1; }
