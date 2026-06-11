import os
import sys
import shutil
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Import logic from cli
from omnidrive.cli import (
    is_mounted, DEFAULT_LINKS, DEFAULT_MOUNT_POINT, DEFAULT_IMAGE_PATH,
    repair_links, run_cmd
)

app = FastAPI(title="OmniDrive Control Panel")

# Set up templates directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Determine if running in Docker
DOCKER_MODE = os.environ.get("DOCKER_MODE", "false").lower() == "true"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "docker_mode": DOCKER_MODE})

@app.get("/api/status")
async def get_status():
    mounted = is_mounted()
    status_data = {
        "mounted": mounted,
        "mount_point": str(DEFAULT_MOUNT_POINT),
        "image_path": str(DEFAULT_IMAGE_PATH),
        "docker_mode": DOCKER_MODE,
        "capacity": {
            "total": "N/A",
            "used": "N/A",
            "free": "N/A",
            "percent": 0
        },
        "symlinks": []
    }
    
    # Gather capacity stats
    if mounted:
        try:
            total, used, free = shutil.disk_usage(DEFAULT_MOUNT_POINT)
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            percent = (used / total) * 100
            status_data["capacity"] = {
                "total": f"{total_gb:.2f} GB",
                "used": f"{used_gb:.2f} GB",
                "free": f"{free_gb:.2f} GB",
                "percent": round(percent, 1)
            }
        except Exception as e:
            status_data["capacity"]["error"] = str(e)

    # Gather symlink status
    for link_name, target in DEFAULT_LINKS.items():
        link_path = DEFAULT_MOUNT_POINT / link_name
        valid = False
        status_str = "missing"
        resolved_str = str(target)
        
        if mounted:
            if link_path.is_symlink():
                resolved = link_path.resolve()
                resolved_str = str(resolved)
                if resolved.exists():
                    valid = True
                    status_str = "valid"
                else:
                    status_str = "broken"
            elif link_path.exists():
                status_str = "invalid_type"
        
        status_data["symlinks"].append({
            "name": link_name,
            "target": str(target),
            "resolved": resolved_str,
            "status": status_str,
            "valid": valid
        })
        
    return JSONResponse(content=status_data)

@app.post("/api/mount")
async def trigger_mount():
    if is_mounted():
        return JSONResponse(content={"success": True, "message": "Already mounted."})
        
    if DOCKER_MODE:
        # Docker container cannot run macOS hdiutil directly. We return instruction or mock.
        return JSONResponse(content={
            "success": False, 
            "message": "⚠️ Running inside Docker. Please run 'omnimount' or mount the sparsebundle on the Host OS first."
        })
        
    if not DEFAULT_IMAGE_PATH.exists():
        return JSONResponse(content={"success": False, "message": f"Image file not found at {DEFAULT_IMAGE_PATH}."})
        
    try:
        run_cmd(f"hdiutil attach {DEFAULT_IMAGE_PATH}")
        if is_mounted():
            # Auto repair links
            repair_links(silent=True)
            return JSONResponse(content={"success": True, "message": "OmniDrive mounted successfully!"})
        else:
            return JSONResponse(content={"success": False, "message": "Mount command completed but volume not visible."})
    except Exception as e:
        return JSONResponse(content={"success": False, "message": f"Failed to mount: {str(e)}"})

@app.post("/api/unmount")
async def trigger_unmount():
    if not is_mounted():
        return JSONResponse(content={"success": True, "message": "Already unmounted."})
        
    if DOCKER_MODE:
        return JSONResponse(content={
            "success": False, 
            "message": "⚠️ Running inside Docker. Please unmount the volume on the Host OS."
        })
        
    try:
        run_cmd(f"hdiutil detach {DEFAULT_MOUNT_POINT}")
        if not is_mounted():
            return JSONResponse(content={"success": True, "message": "OmniDrive detached successfully."})
        else:
            return JSONResponse(content={"success": False, "message": "Unmount command finished but volume is still mounted."})
    except Exception as e:
        return JSONResponse(content={"success": False, "message": f"Failed to unmount: {str(e)}"})

@app.post("/api/link")
async def trigger_link():
    if not is_mounted():
        return JSONResponse(content={"success": False, "message": "OmniDrive must be mounted to create/repair links."})
        
    try:
        # Run repair
        repair_links(silent=True)
        return JSONResponse(content={"success": True, "message": "Symlinks repaired successfully!"})
    except Exception as e:
        return JSONResponse(content={"success": False, "message": f"Failed to repair symlinks: {str(e)}"})

@app.get("/api/files")
async def get_files():
    if not is_mounted():
        return JSONResponse(content={"files": []})
        
    files_list = []
    try:
        for entry in DEFAULT_MOUNT_POINT.iterdir():
            if entry.name.startswith('.'):
                continue
            is_dir = entry.is_dir()
            size = entry.stat().st_size if not is_dir else 0
            files_list.append({
                "name": entry.name,
                "is_dir": is_dir,
                "size": f"{size / 1024:.1f} KB" if not is_dir else "Dir",
                "is_symlink": entry.is_symlink()
            })
    except Exception as e:
        return JSONResponse(content={"error": str(e), "files": []})
        
    return JSONResponse(content={"files": files_list})
