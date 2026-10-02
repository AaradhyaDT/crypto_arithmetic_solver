@echo off
setlocal
REM ============================================================================
REM sync.bat - Zero-Friction Execution Wrapper for sync.ps1
REM Automatically bypasses PowerShell ExecutionPolicy across fresh clones/devices.
REM ============================================================================

where pwsh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1" %*
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync.ps1" %*
)
exit /b %ERRORLEVEL%