$sevenZip = "C:\Program Files\7-Zip\7z.exe"
$base = "C:\Users\Barre\松尾研\LLMATCH\USPTO_data_analysis\data\IMPACT"

Write-Host "IMPACT auto-extractor started. Checking every 60s..."

while ($true) {
    $zips = Get-ChildItem $base -Filter "*.zip" | Where-Object { $_.Name -match "^\d{4}\.zip$" }
    foreach ($zip in $zips) {
        $year = $zip.BaseName
        $outDir = Join-Path $base $year
        $innerDir = Join-Path $outDir $year
        $lockFile = Join-Path $base "${year}.extracting"

        # すでに展開済み or 展開中はスキップ
        if ((Test-Path $innerDir) -or (Test-Path $lockFile)) { continue }

        # zipがまだダウンロード中でないか（サイズが変化していないか）を確認
        $size1 = $zip.Length
        Start-Sleep -Seconds 5
        $size2 = (Get-Item $zip.FullName).Length
        if ($size1 -ne $size2) {
            Write-Host "${year}: still downloading, skipping"
            continue
        }

        New-Item $lockFile -ItemType File -Force | Out-Null
        Write-Host "${year}: extracting..."
        & $sevenZip x $zip.FullName -o"$outDir" -y
        if ($LASTEXITCODE -eq 0) {
            Write-Host "${year}: extraction done"
            $macosx = Join-Path $outDir "__MACOSX"
            if (Test-Path $macosx) {
                Remove-Item $macosx -Recurse -Force -Confirm:$false
                Write-Host "${year}: __MACOSX removed"
            }
        } else {
            Write-Host "${year}: extraction FAILED (exit $LASTEXITCODE)"
        }
        Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 60
}
