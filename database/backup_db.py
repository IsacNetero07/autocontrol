import shutil
from datetime import datetime
from pathlib import Path
from database.database import DB_PATH


def fazer_backup():
    pasta_backups = DB_PATH.parent / "backups"
    pasta_backups.mkdir(exist_ok=True)

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = pasta_backups / f"oficina_backup_{agora}.db"

    shutil.copy2(DB_PATH, destino)

    return destino


def restaurar_backup(caminho_backup):
    caminho_backup = Path(caminho_backup)

    if not caminho_backup.exists():
        raise FileNotFoundError("Arquivo de backup não encontrado.")

    pasta_backups = DB_PATH.parent / "backups"
    pasta_backups.mkdir(exist_ok=True)
    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    seguranca = pasta_backups / f"oficina_pre_restauro_{agora}.db"
    shutil.copy2(DB_PATH, seguranca)

    shutil.copy2(caminho_backup, DB_PATH)


def listar_backups():
    pasta_backups = DB_PATH.parent / "backups"
    if not pasta_backups.exists():
        return []

    arquivos = sorted(pasta_backups.glob("oficina_backup_*.db"), reverse=True)
    return arquivos