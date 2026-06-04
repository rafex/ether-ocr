# docker.just — Docker tasks imported by root Justfile

root_dir := justfile_directory() / ".." / ".."

# Run OCR inside Docker container
docker-ocr input output='ocr_output.txt':
    @echo "==> Running OCR in Docker on {{input}} -> {{output}}"
    bash "{{root_dir}}/scripts/shellscript/docker-run.sh" "{{input}}" "{{output}}"

# Start docker-compose services
docker-up:
    @echo "==> Starting Docker services"
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" up -d

# Stop docker-compose services
docker-down:
    @echo "==> Stopping Docker services"
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" down

# View Docker container logs
docker-logs:
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" logs -f

# Open a shell inside the running container
docker-shell:
    docker compose -f "{{root_dir}}/containers/docker-compose.yml" exec ether-ocr /bin/bash
