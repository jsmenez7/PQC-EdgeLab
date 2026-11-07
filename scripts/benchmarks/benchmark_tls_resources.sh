
#!/usr/bin/env bash

set -u

CONDITION="${1:-bt_on}"
REPETITIONS="${2:-10}"

DIR="$HOME/PQC-EdgeLab/results/system/tls_resources"
mkdir -p "$DIR"

if [[ "$CONDITION" != "bt_on" && "$CONDITION" != "bt_off" ]]; then
    echo "Error: usa bt_on o bt_off"
    exit 1
fi

BT_STATE=$(systemctl is-active bluetooth.service || true)
WIFI_STATE=$(iw dev wlan0 get power_save)

if [[ "$CONDITION" == "bt_on" && "$BT_STATE" != "active" ]] ||
   [[ "$CONDITION" == "bt_off" && "$BT_STATE" == "active" ]]; then
    echo "Error: estado Bluetooth no coincide con $CONDITION"
    exit 1
fi

CSV="$DIR/${CONDITION}_$(date +%Y%m%d_%H%M%S_%N).csv"

echo "repetition,group,user_s,system_s,elapsed_s,maxrss_kib,exit_code,verified" > "$CSV"

echo "=== BENCHMARK TLS RECURSOS ==="
echo "Condicion: $CONDITION"
echo "Bluetooth: $BT_STATE"
echo "Wi-Fi: $WIFI_STATE"
echo "Repeticiones por grupo: $REPETITIONS"

for ((i=1; i<=REPETITIONS; i++)); do

    if ((i % 2 == 1)); then
        TLS_GROUPS=(X25519 X25519MLKEM768)
    else
        TLS_GROUPS=(X25519MLKEM768 X25519)
    fi

    for GROUP in "${TLS_GROUPS[@]}"; do

        LOG=$(mktemp)
        TM=$(mktemp)

        printf 'GET / HTTP/1.0\r\nHost: pqc-server.local\r\n\r\n' |
        /usr/bin/time -f '%U,%S,%e,%M' -o "$TM" \
        timeout 15 openssl s_client \
            -connect pqc-server.local:4433 \
            -servername pqc-server.local \
            -tls1_3 \
            -groups "$GROUP" \
            -ciphersuites TLS_AES_256_GCM_SHA384 \
            -CAfile "$HOME/pqc-tls/server-cert.pem" \
            -verify_hostname pqc-server.local \
            -verify_return_error \
            -brief > "$LOG" 2>&1

        STATUS=$?
        VERIFIED=0

        if [[ "$STATUS" -eq 0 ]] &&
           grep -q "Verification: OK" "$LOG" &&
           grep -q "Protocol version: TLSv1.3" "$LOG"; then

            if [[ "$GROUP" == "X25519" ]] &&
               grep -q "Peer Temp Key: X25519," "$LOG"; then
                VERIFIED=1
            elif [[ "$GROUP" == "X25519MLKEM768" ]] &&
                 grep -q "Negotiated TLS1.3 group: X25519MLKEM768" "$LOG"; then
                VERIFIED=1
            fi
        fi

        VALUES=$(tail -n 1 "$TM")

        if [[ ! "$VALUES" =~ ^[0-9.]+,[0-9.]+,[0-9.]+,[0-9]+$ ]]; then
            VALUES=",,,"
            VERIFIED=0
        fi

        echo "$i,$GROUP,$VALUES,$STATUS,$VERIFIED" >> "$CSV"

        echo "$GROUP | Repeticion $i | Verificado: $VERIFIED"

        if [[ "$VERIFIED" -ne 1 ]]; then
            cp "$LOG" "$DIR/error_${GROUP}_${i}_$(date +%s%N).log"
        fi

        rm -f "$LOG" "$TM"

    done
done

echo "=== FINALIZADO ==="
echo "CSV guardado en: $CSV"
echo "Filas totales: $(wc -l < "$CSV")"
