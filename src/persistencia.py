"""Salvar e carregar o SistemaHospitalar em arquivo JSON."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from hospital import Consulta, Medico, NodeEspecialidade, SistemaHospitalar


def _no_para_dict(no: NodeEspecialidade) -> dict:
    return {
        "nome": no.nome,
        "medicos": [asdict(m) for m in no.medicos],
        "filhos": [_no_para_dict(f) for f in no.filhos],
    }


def _dict_para_no(d: dict) -> NodeEspecialidade:
    return NodeEspecialidade(
        d["nome"],
        [Medico(m["nome"], m["crm"]) for m in d["medicos"]],
        [_dict_para_no(f) for f in d["filhos"]],
    )


def salvar_sistema(sistema: SistemaHospitalar, caminho) -> None:
    """Grava árvore, pacientes e consultas. O grafo é reconstruído ao carregar."""
    dados = {
        "arvore": _no_para_dict(sistema.raiz) if sistema.raiz else None,
        "pacientes": [asdict(p) for p in sistema.pacientes],
        "consultas": {
            cpf: [
                {"data": c.data, "crm": c.medico.crm, "diagnostico": c.diagnostico}
                for c in consultas
            ]
            for cpf, consultas in sistema.prontuarios.items()
        },
    }
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_sistema(caminho) -> SistemaHospitalar:
    """Lê o arquivo JSON e reconstrói o sistema, inclusive o grafo."""
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    sistema = SistemaHospitalar(com_dados_exemplo=False)

    if dados["arvore"]:
        sistema.raiz = _dict_para_no(dados["arvore"])

    for p in dados["pacientes"]:
        sistema.adicionar_paciente(p["nome"], p["cpf"], p["idade"])

    for cpf, consultas in dados["consultas"].items():
        for c in consultas:
            medico = sistema.buscar_medico_por_crm(c["crm"])
            if medico is None:
                raise ValueError(f"Médico com CRM {c['crm']} não encontrado no arquivo.")
            sistema.prontuarios.setdefault(cpf, []).append(
                Consulta(c["data"], medico, c["diagnostico"])
            )
            sistema.grafo.setdefault(("P", cpf), set()).add(("M", medico.crm))
            sistema.grafo.setdefault(("M", medico.crm), set()).add(("P", cpf))
    return sistema