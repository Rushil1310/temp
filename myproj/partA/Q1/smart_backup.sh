#!/bin/bash

SOURCE_DIR="$1"
BACKUP_DIR="$2"
DRY_RUN=false

# Check for --dry flag
[[ "$3" == "--dry" ]] && DRY_RUN=true

# Validate arguments
if [[ -z "$SOURCE_DIR" || -z "$BACKUP_DIR" ]]; then
    echo "Usage: $0 <source_dir> <backup_dir> [--dry]"
    exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: Source directory does not exist"
    exit 1
fi

if ! $DRY_RUN; then
    mkdir -p "$BACKUP_DIR"
    touch "$BACKUP_DIR/backup.log"
fi

log() {
    # Args: $1=message
    # TODO: Implement logging function
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"

    # if else statements

    echo "$msg"
    if ! $DRY_RUN; then 
        echo "$msg" >> "$BACKUP_DIR/backup.log"
    fi
}

copy_file() {
    # Args: $1=source, $2=destination, $3=reason (NEW/MODIFIED)
    local src="$1" dest="$2" reason="$3"
    # TODO: Log the action
    log "$src - $reason"

    local filename="$(basename "$src")" #this is extra so that i get only file name
    # TODO: If not dry run, create parent dir and copy file
    if ! $DRY_RUN; then
        mkdir -p "$(dirname "$dest")"
        cp -p "$src" "$dest"  #copy
    fi
}

backup_files() {
    # TODO: Iterate through all files in SOURCE_DIR
    # For each file:
    #   - Calculate relative path
    #   - Calculate destination path
    #   - If dest doesn't exist: copy_file with reason "NEW"
    #   - If source is newer than dest: copy_file with reason "MODIFIED"

    [[ ! -d "$BACKUP_DIR" ]] && return

    find "$SOURCE_DIR" -type f | while IFS= read -r src_file; do
        rel_path="${src_file#$SOURCE_DIR/}"
        dest_file="$BACKUP_DIR/$rel_path"

        if [[ ! -f "$dest_file" ]]; then
            copy_file "$src_file" "$dest_file" "NEW"

        elif [[ "$src_file" -nt "$dest_file" ]]; then
            copy_file "$src_file" "$dest_file" "MODIFIED"
        fi
    done

    find "$SOURCE_DIR" -type d -empty | while IFS= read -r src_dir; do
        rel_path="${src_dir#$SOURCE_DIR/}"
        dest_dir="$BACKUP_DIR/$rel_path"

        if [[ ! -d "$dest_dir" ]]; then
            dirname_only="$(basename "$src_dir")"

            if ! $DRY_RUN; then
                mkdir -p "$dest_dir"
            fi

            log "$dirname_only/ - EMPTY_DIR_NEW"
        fi
    done
}

detect_ghosts() {
    # TODO: Find files in backup that no longer exist in source
    # These are "ghost files" - files deleted from source but kept in backup
    # Log them with reason "DELETED_IN_SOURCE (KEPT)"
    [[ ! -d "$BACKUP_DIR" ]] && return
            
            # TODO: Check if original source file exists
            # If not, log as ghost file
    find "$BACKUP_DIR" -type f ! -name "backup.log" | while IFS= read -r backup_file; do
        rel_path="${backup_file#$BACKUP_DIR/}"
        src_file="$SOURCE_DIR/$rel_path"

        if [[ ! -f "$src_file" ]]; then
            log "$src_file - DELETED_IN_SOURCE (KEPT)"
        fi
    done
}

dry_run() {
    echo "=== DRY RUN MODE ==="
    backup_files
    detect_ghosts
    echo "=== END DRY RUN ==="
}

# Main execution
if $DRY_RUN; then
    dry_run
else
    backup_files
    detect_ghosts
fi

echo "Backup complete!"
