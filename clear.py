from pathlib import Path


def clearLog():
    root = Path('.')
    log_path = root.rglob('*.log')
    for log in log_path:
        log.unlink()


if __name__ == '__main__':
    clearLog()
