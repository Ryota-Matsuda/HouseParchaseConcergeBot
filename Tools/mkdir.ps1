<#
.SYNOPSIS
  list.txt の内容を読み取って、フォルダとファイルを一括作成するスクリプト。

.DESCRIPTION
  - 行末が "/" の項目はフォルダとして作成
  - それ以外はファイルとして作成（空ファイル）
  - 行頭のスペース数（2スペース = 1階層）でネストを判定

.EXAMPLE
  .\create-structure.ps1
  .\create-structure.ps1 -ListFile .\list.txt -OutputRoot .\my-project
#>

param(
    [string]$ListFile = ".\list.txt",
    [string]$OutputRoot = ".",
    [int]$IndentSize = 2
)

#引き数チェック
if(-not(Test-Path $ListFile)){
    Write-Error"リストファイルが見つかりません：$ListFile"
}

if(-not(Test-Path $OutputRoot)){
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
}
$OutputRoot = (Resolve-Path $OutputRoot).Path

#各階層の現在のパスを保持するスタック
$pathStack = @{}
$pathStack[-1] = $OutputRoot

#ファイル読み込み
$lines = Get-Content -Path $ListFile -Encoding UTF8

foreach($line in $lines){
    if([string]::IsNullOrWhiteSpace($line)){continue}

    #タブをスペースに変換する(階層確認のため)
    $expanded = $line -replace "`t",(" " * $IndentSize)

    #先頭スペース数からインデントレベルを計算
    $leadingSpaces = ($expanded -replace  '^( *).*$', '$1').Length
    $level = [int]($leadingSpaces / $IndentSize)

    $name = $expanded.Trim()

    # 親パスを取得
    $parent = $pathStack[$level - 1]
    if (-not $parent) { $parent = $OutputRoot }

    if ($name.EndsWith("/")) {
        # フォルダ作成
        $folderName = $name.TrimEnd("/")
        $fullPath = Join-Path $parent $folderName

        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
            Write-Host "[DIR ] $fullPath"
        } else {
            Write-Host "[SKIP] $fullPath (already exists)"
        }

        # このレベルの現在パスとして登録
        $pathStack[$level] = $fullPath
    }
    else {
        # ファイル作成（空ファイル）
        $fullPath = Join-Path $parent $name

        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType File -Path $fullPath -Force | Out-Null
            Write-Host "[FILE] $fullPath"
        } else {
            Write-Host "[SKIP] $fullPath (already exists)"
        }
    }
Write-Host "`n完了しました。" -ForegroundColor Green
}
