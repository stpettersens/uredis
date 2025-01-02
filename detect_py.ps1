# Detect a Python intepreter.
$python = "python"
$python3 = "python3"
$pypy3 = "pypy3"
$pypy = "pypy"

if (Get-Command -Name $python -ErrorAction SilentlyContinue) {
    Write-Host $python
}

if (Get-Command -Name $python3 -ErrorAction SilentlyContinue) {
    Write-Host $python3
}

if (Get-Command -Name $pypy3 -ErrorAction SilentlyContinue) {
    Write-Host $pypy3
}

if (Get-Command -Name $pypy -ErrorAction SilentlyContinue) {
    Write-Host $pypy
}

Write-Host "Error: Cannot find a Python interpreter."
