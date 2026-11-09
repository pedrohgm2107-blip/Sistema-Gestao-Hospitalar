import json
from pathlib import Path

from hospital import SistemaHospitalar, menu_principal
from persistencia import carregar_sistema, salvar_sistema

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "hospital.json"


def iniciar() -> SistemaHospitalar:
    if ARQUIVO.exists():
        try:
            sistema = carregar_sistema(ARQUIVO)
            print(f"Dados carregados de {ARQUIVO.name}.")
            return sistema
        except (json.JSONDecodeError, KeyError, ValueError):
            print("Arquivo de dados inválido. Iniciando com os dados de exemplo "
                  "(o arquivo será substituído ao sair).")
    return SistemaHospitalar()


if __name__ == "__main__":
    sistema = iniciar()
    try:
        menu_principal(sistema)
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")
    finally:
        salvar_sistema(sistema, ARQUIVO)
        print(f"Dados salvos em {ARQUIVO.name}.")
        print("Os dados são salvos em dados/hospital.json ao sair e carregados na próxima execução.")
        