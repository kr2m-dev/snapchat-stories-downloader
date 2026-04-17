@echo off
chcp 65001 >nul
echo =======================================
echo  Snapchat Stories Downloader
echo =======================================
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python depuis https://python.org
    echo Assurez-vous de cocher "Add Python to PATH" pendant l'installation
    pause
    exit /b 1
)

echo [OK] Python detecte

:: Vérifier les dependances
echo [INFO] Verification des dependances...
python -c "import requests, aiohttp, aiofiles, beautifulsoup4" 2>nul
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    pip install -r requirements.txt
)

:: Lancer l'interface graphique
echo.
echo [INFO] Lancement de l'application...
echo.
python gui.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Une erreur s'est produite
    pause
)

exit /b 0