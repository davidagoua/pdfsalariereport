
import uvicorn
import os
import sys

# Add the current directory to sys.path to ensure modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Freeze support is needed for multiprocessing on Windows (though uvicorn logic differs slightly, good practice)
    # However, Uvicorn's reload option doesn't work well in frozen apps, so we disable it.
    
    # We use a hardcoded port or one passed via environment/args.
    # For a desktop app, finding a free port dynamically is better, but let's stick to 8000 for now or allow override.
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False, workers=1)
