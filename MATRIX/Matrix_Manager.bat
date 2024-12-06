@echo off
title MATRIX Browser Manager
setlocal EnableDelayedExpansion

:: Define error log file
set "error_log=matrix_error.log"

:main_menu
cls
echo ============================================
echo        MATRIX Browser Manager
echo ============================================
echo          Welcome to MATRIX Browser Manager
echo ============================================
echo 1. Install Dependencies (On first install)
echo 2. Update MATRIX (Replace files with the latest version)
echo 3. Delete MATRIX (Removes all files and stops scripts)
echo 4. View Running Directory
echo 5. Uninstall MATRIX Dependencies
echo 6. Exit
echo ============================================
choice /c 123456 /m "Select an option:"

:: Handle user's choice
if %errorlevel%==1 goto install_dependencies
if %errorlevel%==2 goto update_matrix
if %errorlevel%==3 goto delete_matrix
if %errorlevel%==4 goto view_directory
if %errorlevel%==5 goto uninstall_dependencies
if %errorlevel%==6 goto exit

:install_dependencies
cls
echo ============================================
echo Installing dependencies for MATRIX Browser...
echo ============================================

:: Check for Python 3.11
echo Searching for Python 3.11 installation...
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i

"%PYTHON_PATH%" --version 2>nul | findstr "3.11" >nul
if errorlevel 1 (
    echo [ERROR] Python 3.11 not found. Please install Python 3.11.
    echo [ERROR] Python 3.11 not found. >> %error_log%
    timeout /t 5
    goto main_menu
)

echo Python 3.11 detected at: %PYTHON_PATH%
echo Installing dependencies...

"%PYTHON_PATH%" -m pip install --upgrade pip >> %error_log% 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip. Check %error_log% for details.
    timeout /t 5
    goto main_menu
)

"%PYTHON_PATH%" -m pip install PyQt5 PyQtWebEngine >> %error_log% 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install required dependencies. Check %error_log% for details.
    timeout /t 5
    goto main_menu
)

echo [SUCCESS] All dependencies installed successfully!
pause
goto main_menu

:update_matrix
cls
echo ============================================
echo Updating MATRIX Browser to the latest version...
echo ============================================

:: Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git and try again.
    timeout /t 5
    goto main_menu
)

:: Clone or pull the latest version
if exist MATRIX (
    echo Pulling the latest version from GitHub...
    cd MATRIX
    git pull
    cd ..
) else (
    echo Cloning the MATRIX Browser repository...
    git clone https://github.com/BeanArtStuffs/Matrix-Browser
)

echo MATRIX Browser has been updated to the latest version.
pause
goto main_menu

:delete_matrix
cls
echo ============================================
echo Deleting MATRIX Browser...
echo ============================================

:: Stop all MATRIX scripts
taskkill /im python.exe /f >nul 2>&1

:: Delete the MATRIX folder
if exist MATRIX (
    rmdir /s /q MATRIX
    echo MATRIX Browser files have been deleted.
) else (
    echo No MATRIX Browser files found to delete.
)

pause
goto main_menu

:view_directory
cls
echo ============================================
echo Current Running Directory:
echo ============================================
echo %cd%
echo ============================================
pause
goto main_menu

:uninstall_dependencies
cls
echo ============================================
echo Uninstalling MATRIX Dependencies...
echo ============================================

:: Check for Python 3.11
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i

"%PYTHON_PATH%" -m pip uninstall PyQt5 PyQtWebEngine -y
if errorlevel 1 (
    echo [ERROR] Failed to uninstall dependencies. Check %error_log% for details.
    timeout /t 5
    goto main_menu
)

echo [SUCCESS] MATRIX dependencies uninstalled successfully!
pause
goto main_menu

:exit
exit
