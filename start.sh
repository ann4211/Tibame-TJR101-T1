set -e
rm -rf /tmp/unique_user_data_*
echo "開始執行所有 Python 程式"

for file in $(find /app -type f -name "*.py" | sort); do
    echo "執行 $file"
    python3 "$file"
done

echo "所有 Python 程式執行完畢"

