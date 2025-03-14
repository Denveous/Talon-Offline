""" Import necessary modules for the program to work """
import sys
import ctypes
import os
import tempfile
import subprocess
import requests
import winreg
import shutil
import time
import logging
import json
from pathlib import Path

""" Set up the log file """
LOG_FILE = "talon.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

""" Utility function to log outputs """
def log(message):
    logging.info(message)
    print(message)

""" Utility function to check if the program is running as administrator """
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

""" If the program is not running as administrator, attempt to elevate """
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)



""" Run a script to remove Edge, and prevent reinstallation """
def run_edge_vanisher():
    log("Starting Edge Vanisher script execution...")
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_path, "components\\edge_vanisher.ps1" if "__compiled__" in globals() else "edge_vanisher.ps1")

        log(f"Loading Edge Vanisher script from: {script_path}")
        
        if not os.path.exists(script_path):
            log("Script not found, please ensure it exists in the current directory.")
            return
        
        powershell_command = (
            f"Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}'; exit" 
        )
        log(f"Executing PowerShell command: {powershell_command}")
        
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            log("Edge Vanisher execution completed successfully")
            log(f"Process output: {process.stdout}")
            run_oouninstall() 
        else:
            log(f"Edge Vanisher execution failed with return code: {process.returncode}")
            log(f"Process error: {process.stderr}")
            run_oouninstall() 
            
    except IOError as e:
        log(f"File I/O error while accessing Edge Vanisher script: {str(e)}")
        run_oouninstall()  
    except Exception as e:
        log(f"Unexpected error during Edge Vanisher execution: {str(e)}")
        run_oouninstall()  


""" Run a script to remove OneDrive and Outlook """
def run_oouninstall():
    log("Starting Office Online uninstallation process...")
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_path, "components\\uninstall_oo.ps1" if "__compiled__" in globals() else "uninstall_oo.ps1")

        log(f"Loading OO uninstall script from: {script_path}")
        
        if not os.path.exists(script_path):
            log("Script not found, please ensure it exists in the current directory.")
            return
        
        powershell_command = f"Set-ExecutionPolicy Bypass -Scope Process -Force; & '{script_path}'"
        log(f"Executing PowerShell command: {powershell_command}")
        
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            log("Office Online uninstallation completed successfully")
            log(f"Process stdout: {process.stdout}")
            run_tweaks()
        else:
            log(f"Office Online uninstallation failed with return code: {process.returncode}")
            log(f"Process stderr: {process.stderr}")
            log(f"Process stdout: {process.stdout}")
            run_tweaks()
            
    except Exception as e:
        log(f"Unexpected error during OO uninstallation: {str(e)}")
        run_tweaks()

""" Run ChrisTitusTech's WinUtil to debloat the system (Thanks Chris, you're a legend! https://christitus.com/win) """
def run_tweaks():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if not is_admin():
        log("Must be run as an administrator.")
        sys.exit(1)

    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_path, "components\\barebones.json" if "__compiled__" in globals() else "barebones.json")
        script_path = os.path.join(base_path, "components\\winutil.ps1" if "__compiled__" in globals() else "winutil.ps1")
        log(f"Json Path {json_path}")
        log(f"Script Path {script_path}")

        log(f"Using config from: {json_path}")

        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, "cttwinutil.log")


        command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            f"$ErrorActionPreference = 'SilentlyContinue'; " +
            f"iex \"& {{ $(irm '{script_path}') }} -Config '{json_path}' -Run\" *>&1 | " +
            "Tee-Object -FilePath '" + log_file + "'"
        ]
                
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        while True:
            output = process.stdout.readline()
            if output:
                output = output.strip()
                log(f"CTT Output: {output}")
                if "Tweaks are Finished" in output:
                    log("Detected completion message. Terminating...")

                    subprocess.run(
                        ["powershell", "-Command", "Stop-Process -Name powershell -Force"],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    run_winconfig()
                    os._exit(0)
            
            if process.poll() is not None:
                run_winconfig()
                os._exit(1)

        return False

    except Exception as e:
        log(f"Error: {str(e)}")
        run_winconfig()
        os._exit(1)


""" Run Raphi's Win11Debloat script to further debloat the system (Thanks Raphire! Source: https://win11debloat.raphi.re/Win11Debloat.ps1) """
def run_winconfig():
    log("Starting Windows configuration process...")
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_path, "components\\winutil.ps1" if "__compiled__" in globals() else "run_debloat.ps1")
        log(f"Debloat Target script path: {script_path}")
        components_path = os.path.join(base_path, "components")
        powershell_command = (
            f"Set-ExecutionPolicy Bypass -Scope Process -Force; "
            f"& '{script_path}' -Silent -RemoveApps -RemoveGamingApps -DisableTelemetry "
            f"-DisableBing -DisableSuggestions -DisableLockscreenTips -RevertContextMenu "
            f"-TaskbarAlignLeft -HideSearchTb -DisableWidgets -DisableCopilot -ExplorerToThisPC "
            f"-ClearStartAllUsers -DisableDVR -DisableStartRecommended -ExplorerToThisPC "
            f"-DisableMouseAcceleration -ScriptPath '{os.path.dirname(components_path)}'"
        )

        log(f"Executing PowerShell command with parameters:")
        log(f"Command: {powershell_command}")

        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True
        )

        if process.returncode == 0:
            log("Windows configuration completed successfully")
            log(f"Process stdout: {process.stdout}")
            log("Preparing to transition to UpdatePolicyChanger...")
            try:
                log("Initiating UpdatePolicyChanger process...")
                run_updatepolicychanger()
            except Exception as e:
                log(f"Failed to start UpdatePolicyChanger: {e}")
                log("Attempting to continue with installation despite UpdatePolicyChanger failure")
                run_updatepolicychanger()
        else:
            log(f"Windows configuration failed with return code: {process.returncode}")
            log(f"Process stderr: {process.stderr}")
            log(f"Process stdout: {process.stdout}")
            log("Attempting to continue with UpdatePolicyChanger despite WinConfig failure")
            try:
                log("Initiating UpdatePolicyChanger after WinConfig failure...")
                run_updatepolicychanger()
            except Exception as e:
                log(f"Failed to start UpdatePolicyChanger after WinConfig failure: {e}")
                log("Proceeding to finalize installation...")
                run_updatepolicychanger()
            
    except requests.exceptions.RequestException as e:
        log(f"Network error during Windows configuration script download: {str(e)}")
        log("Attempting to continue with UpdatePolicyChanger despite network error")
        try:
            run_updatepolicychanger()
        except Exception as inner_e:
            log(f"Failed to start UpdatePolicyChanger after network error: {inner_e}")
            run_updatepolicychanger()
    except IOError as e:
        log(f"File I/O error while saving Windows configuration script: {str(e)}")
        log("Attempting to continue with UpdatePolicyChanger despite I/O error")
        try:
            run_updatepolicychanger()
        except Exception as inner_e:
            log(f"Failed to start UpdatePolicyChanger after I/O error: {inner_e}")
            run_updatepolicychanger()
    except Exception as e:
        log(f"Unexpected error during Windows configuration: {str(e)}")
        log("Attempting to continue with UpdatePolicyChanger despite unexpected error")
        try:
            run_updatepolicychanger()
        except Exception as inner_e:
            log(f"Failed to start UpdatePolicyChanger after unexpected error: {inner_e}")
            run_updatepolicychanger()


""" Run a script to establish an update policy which only accepts security updates """
def run_updatepolicychanger():
    log("Starting UpdatePolicyChanger script execution...")
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(base_path, "components\\update_policy_changer.ps1" if "__compiled__" in globals() else "update_policy_changer.ps1")
        log(f"Loading UpdatePolicyChanger script from: {script_path}")
        
        if not os.path.exists(script_path):
            log("Script not found, please ensure it exists in the current directory.")
            return
        
        log("Preparing PowerShell command execution...")
        powershell_command = f"Set-ExecutionPolicy Bypass -Scope Process -Force; & \"{script_path}\"; exit"
        log(f"PowerShell command prepared: {powershell_command}")
        
        process = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            timeout=300  # Increase timeout if necessary
        )
        
        log(f"PowerShell process completed with return code: {process.returncode}")
        log(f"Process stdout: {process.stdout}")
        log(f"Process stderr: {process.stderr}")
        
        if process.returncode == 0:
            log("UpdatePolicyChanger execution completed successfully")
            apply_registry_changes()
        else:
            log(f"UpdatePolicyChanger execution failed with return code: {process.returncode}")
            apply_registry_changes()
            
    except Exception as e:
        log(f"Critical error in UpdatePolicyChanger: {e}")
        apply_registry_changes()

    except Exception as e:
        log(f"Critical error in UpdatePolicyChanger: {e}")
        log("Proceeding to registry changes due to critical error...")
        apply_registry_changes()

""" Apply modifications done via the Windows registry """
def apply_registry_changes():
    log("Applying registry changes...")
    try:
        registry_modifications = [
            # Visual changes
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarAl", winreg.REG_DWORD, 1), # Align taskbar to the center
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme", winreg.REG_DWORD, 0), # Set Windows apps to dark theme
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "SystemUsesLightTheme", winreg.REG_DWORD, 0), # Set Windows to dark theme
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "AppCaptureEnabled", winreg.REG_DWORD, 0), #Fix the  Get an app for 'ms-gamingoverlay' popup
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\PolicyManager\\default\\ApplicationManagement\\AllowGameDVR", "Value", winreg.REG_DWORD, 0), # Disable Game DVR (Reduces FPS Drops)
            (winreg.HKEY_CURRENT_USER, r"Control Panel\\Desktop", "MenuShowDelay", winreg.REG_SZ, "0"),# Reduce menu delay for snappier UI
            (winreg.HKEY_CURRENT_USER, r"Control Panel\\Desktop\\WindowMetrics", "MinAnimate", winreg.REG_DWORD, 0),# Disable minimize/maximize animations
            (winreg.HKEY_CURRENT_USER, r"Control Panel\\Desktop", "DragFullWindows", winreg.REG_SZ, "1"),  # Show window contents while dragging 
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ExtendedUIHoverTime", winreg.REG_DWORD, 1),# Reduce hover time for tooltips and UI elements
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt", winreg.REG_DWORD, 0),# Show file extensions in Explorer (useful for security and organization)
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\Power", "PowerPlan", winreg.REG_SZ, "8c5e7fda-3b9c-4c3b-8c3b-3b3c3b3c3b3c")  # Set power plan to High Performance
        ]
        for root_key, key_path, value_name, value_type, value in registry_modifications:
            try:
                with winreg.CreateKeyEx(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, value_name, 0, value_type, value)
                    log(f"Applied {value_name} to {key_path}")
            except Exception as e:
                log(f"Failed to modify {value_name} in {key_path}: {e}")
        log("Registry changes applied successfully.")
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["start", "explorer.exe"], shell=True)
        log("Explorer restarted to apply registry changes.")
        finalize_installation()
        log("Wrapping up installation.")
        
    except Exception as e:
        log(f"Error applying registry changes: {e}")

""" Finalize installation by restarting """
def finalize_installation():
    log("Installation complete. Restarting system...")
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
    except subprocess.CalledProcessError as e:
        log(f"Error during restart: {e}")
        try:
            os.system("shutdown /r /t 0")
        except Exception as e:
            log(f"Failed to restart system: {e}")


""" Run the program """
if __name__ == "__main__":
    run_edge_vanisher()
