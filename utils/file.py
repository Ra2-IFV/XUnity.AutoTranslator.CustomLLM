from pathlib import Path

def read_file_to_str(path: str) -> str:
    try:
        with open(Path().cwd() / path, 'rb') as f:
            return f.read().decode(encoding='utf-8')
    except FileNotFoundError:
        raise
    