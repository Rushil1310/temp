#!/bin/bash
SOURCE_IMAGE="key.png"  
ENC_FILE1="secret.enc"
OUT_FILE1="secret_revealed.jpg"

calculate_128bit_checksum() {
    local file="$1"
    
    local hex_chunks=$(hexdump -v -e '/1 "%02X"' "$file" | fold -w32)
    
    {
        echo "obase=16"
        echo "ibase=16"
        echo "mod=100000000000000000000000000000000"
        echo "sum=0"
        
        while read -r chunk; do
            local len=${#chunk}
            if (( len < 32 )); then
                local padding=$((32 - len))
                chunk="${chunk}$(printf '%0*d' $padding 0)"
            fi
            echo "sum=(sum + $chunk) % mod"
        done <<< "$hex_chunks"
        
        echo "sum"
    } | BC_LINE_LENGTH=0 bc | tr -d '\\\n ' | awk '{printf "%032s\n", $0}' | tr ' ' '0'
}

decrypt_file() {
    local key="$1"
    local enc_file="$2"
    local out_file="$3"
    openssl enc -d -aes-128-cbc -in "$enc_file" -out "$out_file" -K "$key" -iv 0
    echo "Decrypted: $out_file"
}

if [[ ! -f "$SOURCE_IMAGE" ]]; then
    echo "Error: $SOURCE_IMAGE not found!"
    exit 1
fi

KEY=$(calculate_128bit_checksum "$SOURCE_IMAGE")
echo "128-bit Key: $KEY"

decrypt_file "$KEY" "$ENC_FILE1" "$OUT_FILE1"
echo "Images decrypted! Copy $OUT_FILE1 to partB/q5/ for ASCII art conversion."