from app import create_app
from pathlib import Path
import sys
import subprocess
import os


def ensure_venv_and_reexec():
    root = Path(__file__).parent
    venv_dir = root / 'venv'
    if os.name == 'nt':
        venv_python = venv_dir / 'Scripts' / 'python.exe'
    else:
        venv_python = venv_dir / 'bin' / 'python'

    try:
        if Path(sys.executable).resolve() == venv_python.resolve():
            return
    except Exception:
        pass

    if not venv_dir.exists():
        print('Creating virtual environment...')
        subprocess.check_call([sys.executable, '-m', 'venv', str(venv_dir)])

    req = root / 'requirements.txt'
    req_for_install = str(req)
    if req.exists():
        raw = req.read_bytes()
        if b'\x00' in raw:
            try:
                text = raw.decode('utf-16')
            except Exception:
                text = raw.decode('utf-8', errors='ignore')
            alt = root / 'requirements-utf8.txt'
            alt.write_text(text, encoding='utf-8')
            req_for_install = str(alt)

    print('Installing dependencies into virtualenv (this may take a while)...')
    subprocess.check_call([str(venv_python), '-m', 'pip',
                          'install', '--upgrade', 'pip'])
    if req.exists():
        subprocess.check_call(
            [str(venv_python), '-m', 'pip', 'install', '-r', req_for_install])
    else:
        print('No requirements.txt found; skipping pip install')

    print('Re-launching using virtualenv Python:', str(venv_python))
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)


ensure_venv_and_reexec()


app = create_app()

if __name__ == '__main__':
    print("Starting HireNest Application Server...")
    app.run(host='127.0.0.1', port=5000, debug=True)
