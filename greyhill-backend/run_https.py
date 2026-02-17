
"""
Run FastAPI server with HTTPS using cert.pfx
"""
import uvicorn
import os

# vytvor certifikáty ak neexistujú
if not os.path.exists('cert.pfx'):
    print("Certificate not found. Generating...")
    os.system('python generate_cert.py')

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        ssl_certfile="cert.pfx",
        reload=True
    )
