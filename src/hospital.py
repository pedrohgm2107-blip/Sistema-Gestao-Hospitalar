"""Sistema de Gestão Hospitalar (Estruturas de Dados).

Estruturas usadas:
  1. Árvore de Especialidades  -> NodeEspecialidade (DFS recursiva)
  2. Grafo de Relacionamento   -> dicionário de adjacência (paciente <-> médico)
  3. Tabela Hash               -> dict de prontuários (chave: CPF)
  4. Busca Linear e Bubble Sort de pacientes
  5. Relatório histórico recursivo (ano -> mês -> consultas)

Melhorias principais:
  - Lógica separada da interface: a classe do sistema não usa print/input,
    apenas retorna dados ou levanta ValueError; os menus cuidam da saída.
  - Dataclasses e type hints.
  - Validação de CPF, data, idade e CRM (único em toda a árvore).
  - Consulta registrada em UM só lugar: atualiza prontuário e grafo juntos.
  - Grafo usa identificadores únicos (CPF / CRM) em vez de nomes, evitando
    colisão entre pessoas com o mesmo nome.
  - Busca e ordenação ignoram acentos e maiúsculas/minúsculas.
  - Bubble Sort com parada antecipada; contagem recursiva sem fatiar listas.
  - Meses em português independentes do idioma do sistema operacional.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Optional

MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


# ---------------------------------------------------------------- utilitários
def normalizar(texto: str) -> str:
    """Remove acentos, espaços nas pontas e diferença de maiúsculas."""
    decomposto = unicodedata.normalize("NFD", texto.strip())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn").casefold()


def formatar_cpf(cpf: str) -> str:
    """Aceita '11111111111' ou '111.111.111-11' e devolve o formato padrão."""
    digitos = re.sub(r"\D", "", cpf)
    if len(digitos) != 11:
        raise ValueError("CPF deve ter 11 dígitos.")
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def validar_data(data: str) -> str:
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Data inválida. Use o formato AAAA-MM-DD.") from None
    return data


# ------------------------------------------------------------------- modelos
@dataclass
class Medico:
    nome: str
    crm: str


@dataclass
class Paciente:
    nome: str
    cpf: str
    idade: int


@dataclass
class Consulta:
    data: str
    medico: Medico
    diagnostico: str


@dataclass
class NodeEspecialidade:
    """Nó da Árvore de Especialidades (nome, médicos, sub-especialidades)."""
    nome: str
    medicos: list[Medico] = field(default_factory=list)
    filhos: list["NodeEspecialidade"] = field(default_factory=list)


# ------------------------------------------------------------------- sistema
class SistemaHospitalar:
    def __init__(self, com_dados_exemplo: bool = True) -> None:
        self.raiz: Optional[NodeEspecialidade] = None            # Árvore
        self.grafo: dict[tuple[str, str], set[tuple[str, str]]] = {}  # Grafo
        self.prontuarios: dict[str, list[Consulta]] = {}         # Tabela Hash
        self.pacientes: list[Paciente] = []                      # Lista
        self._pacientes_por_cpf: dict[str, Paciente] = {}        # índice O(1)
        if com_dados_exemplo:
            self._carregar_exemplo()

    # ---------------------------------------------------- 1. Árvore
    def _percorrer(self, no: Optional[NodeEspecialidade] = None) -> Iterator[NodeEspecialidade]:
        """Percorre a árvore em profundidade (pré-ordem), recursivamente."""
        if no is None:
            no = self.raiz
        if no is None:
            return
        yield no
        for filho in no.filhos:
            yield from self._percorrer(filho)

    def buscar_especialidade(self, nome: str) -> Optional[NodeEspecialidade]:
        alvo = normalizar(nome)
        return next((n for n in self._percorrer() if normalizar(n.nome) == alvo), None)

    def adicionar_especialidade(self, nome: str, nome_pai: Optional[str] = None) -> None:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome da especialidade não pode ser vazio.")
        if self.buscar_especialidade(nome):
            raise ValueError(f"A especialidade '{nome}' já existe.")

        novo = NodeEspecialidade(nome)
        if nome_pai is None:
            if self.raiz is not None:
                raise ValueError(
                    f"Já existe uma raiz ('{self.raiz.nome}'). Informe uma especialidade pai."
                )
            self.raiz = novo
            return

        pai = self.buscar_especialidade(nome_pai)
        if pai is None:
            raise ValueError(f"Especialidade pai '{nome_pai}' não encontrada.")
        pai.filhos.append(novo)

    def adicionar_medico(self, especialidade: str, nome: str, crm: str) -> Medico:
        no = self.buscar_especialidade(especialidade)
        if no is None:
            raise ValueError(f"Especialidade '{especialidade}' não encontrada.")
        nome, crm = nome.strip(), crm.strip().upper()
        if not nome or not crm:
            raise ValueError("Nome e CRM são obrigatórios.")
        if self.buscar_medico_por_crm(crm):
            raise ValueError(f"Já existe um médico com CRM {crm}.")
        medico = Medico(nome, crm)
        no.medicos.append(medico)
        return medico

    def _todos_medicos(self) -> Iterator[Medico]:
        for no in self._percorrer():
            yield from no.medicos

    def buscar_medico_por_crm(self, crm: str) -> Optional[Medico]:
        crm = crm.strip().upper()
        return next((m for m in self._todos_medicos() if m.crm == crm), None)

    def buscar_medico_por_nome(self, nome: str) -> Optional[Medico]:
        alvo = normalizar(nome)
        return next((m for m in self._todos_medicos() if normalizar(m.nome) == alvo), None)

    def linhas_medicos(self, especialidade: str) -> list[str]:
        """Médicos de uma especialidade e de suas sub-especialidades (recursivo)."""
        no = self.buscar_especialidade(especialidade)
        if no is None:
            raise ValueError(f"Especialidade '{especialidade}' não encontrada.")

        def montar(atual: NodeEspecialidade, nivel: int) -> list[str]:
            recuo = "  " * nivel
            linhas = [f"{recuo}* {atual.nome}:"]
            if atual.medicos:
                linhas += [f"{recuo}  - {m.nome} (CRM: {m.crm})" for m in atual.medicos]
            else:
                linhas.append(f"{recuo}  - Ninguém registrado.")
            for filho in atual.filhos:
                linhas += montar(filho, nivel + 1)
            return linhas

        return montar(no, 0)

    # ---------------------------------------------------- 4. Pacientes
    def adicionar_paciente(self, nome: str, cpf: str, idade: int) -> Paciente:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome do paciente não pode ser vazio.")
        cpf = formatar_cpf(cpf)
        if not 0 <= idade <= 130:
            raise ValueError("Idade deve estar entre 0 e 130.")
        if cpf in self._pacientes_por_cpf:
            raise ValueError(f"Paciente com CPF {cpf} já cadastrado.")
        paciente = Paciente(nome, cpf, idade)
        self.pacientes.append(paciente)
        self._pacientes_por_cpf[cpf] = paciente
        return paciente

    def buscar_paciente_por_nome(self, trecho: str) -> list[Paciente]:
        """Busca linear, parcial, sem diferenciar acentos/maiúsculas."""
        alvo = normalizar(trecho)
        return [p for p in self.pacientes if alvo in normalizar(p.nome)]

    def ordenar_pacientes_por_nome(self) -> None:
        """Bubble Sort (O(n²)) com parada antecipada se já estiver ordenado."""
        lista, n = self.pacientes, len(self.pacientes)
        for i in range(n - 1):
            trocou = False
            for j in range(n - 1 - i):
                if normalizar(lista[j].nome) > normalizar(lista[j + 1].nome):
                    lista[j], lista[j + 1] = lista[j + 1], lista[j]
                    trocou = True
            if not trocou:
                break

    # ---------------------------------------------------- 2 e 3. Consultas
    def registrar_consulta(self, cpf: str, data: str, nome_medico: str, diagnostico: str) -> None:
        """Registra a consulta no prontuário (hash) e no grafo, de uma só vez."""
        cpf = formatar_cpf(cpf)
        data = validar_data(data)
        paciente = self._pacientes_por_cpf.get(cpf)
        if paciente is None:
            raise ValueError(f"Paciente com CPF {cpf} não cadastrado.")
        medico = self.buscar_medico_por_nome(nome_medico)
        if medico is None:
            raise ValueError(f"Médico '{nome_medico}' não encontrado na árvore de especialidades.")

        # Tabela Hash
        self.prontuarios.setdefault(cpf, []).append(
            Consulta(data, medico, diagnostico.strip() or "Não informado")
        )
        # Grafo não direcionado: vértices identificados por (tipo, id)
        v_pac, v_med = ("P", cpf), ("M", medico.crm)
        self.grafo.setdefault(v_pac, set()).add(v_med)
        self.grafo.setdefault(v_med, set()).add(v_pac)

    def buscar_prontuario(self, cpf: str) -> list[Consulta]:
        cpf = formatar_cpf(cpf)
        if cpf not in self.prontuarios:
            raise ValueError(f"Prontuário do CPF {cpf} não encontrado.")
        return self.prontuarios[cpf]

    def contar_consultas(self, cpf: str) -> int:
        consultas = self.prontuarios.get(formatar_cpf(cpf), [])

        def contar(indice: int) -> int:  # recursão por índice (sem copiar a lista)
            if indice >= len(consultas):
                return 0
            return 1 + contar(indice + 1)

        return contar(0)

    def medicos_que_atenderam(self, cpf: str) -> list[Medico]:
        cpf = formatar_cpf(cpf)
        if ("P", cpf) not in self.grafo:
            raise ValueError("Paciente sem consultas registradas.")
        medicos = [self.buscar_medico_por_crm(v[1]) for v in self.grafo[("P", cpf)]]
        return sorted(medicos, key=lambda m: normalizar(m.nome))

    def pacientes_do_medico(self, nome_medico: str) -> list[Paciente]:
        medico = self.buscar_medico_por_nome(nome_medico)
        if medico is None or ("M", medico.crm) not in self.grafo:
            raise ValueError("Médico não encontrado ou sem consultas registradas.")
        pacientes = [self._pacientes_por_cpf[v[1]] for v in self.grafo[("M", medico.crm)]]
        return sorted(pacientes, key=lambda p: normalizar(p.nome))

    # ---------------------------------------------------- 5. Relatório
    def relatorio_historico(self, cpf: str) -> list[str]:
        """Consultas agrupadas por ano e mês, exibidas recursivamente."""
        consultas = self.buscar_prontuario(cpf)

        agrupado: dict[int, dict[int, list[Consulta]]] = {}
        for c in consultas:
            d = datetime.strptime(c.data, "%Y-%m-%d")
            agrupado.setdefault(d.year, {}).setdefault(d.month, []).append(c)

        def montar(estrutura, nivel: int = 0) -> list[str]:
            recuo = "  " * nivel
            linhas: list[str] = []
            if isinstance(estrutura, dict):
                for chave in sorted(estrutura, reverse=True):  # mais recente primeiro
                    rotulo = f"ANO: {chave}" if nivel == 0 else f"MÊS: {chave:02d} - {MESES[chave]}"
                    linhas.append(f"{recuo}{'▶' if nivel == 0 else '↳'} {rotulo}")
                    linhas += montar(estrutura[chave], nivel + 1)
            else:  # lista de consultas
                for c in sorted(estrutura, key=lambda x: x.data, reverse=True):
                    linhas.append(
                        f"{recuo}• {c.data} | {c.medico.nome} | {c.diagnostico}"
                    )
            return linhas

        return montar(agrupado)

    # ---------------------------------------------------- dados de exemplo
    def _carregar_exemplo(self) -> None:
        self.adicionar_paciente("Maria Silva", "111.111.111-11", 35)
        self.adicionar_paciente("João Santos", "222.222.222-22", 50)
        self.adicionar_paciente("Ana Lima", "333.333.333-33", 28)

        self.adicionar_especialidade("Clínica Geral")
        self.adicionar_especialidade("Pediatria", "Clínica Geral")
        self.adicionar_especialidade("Cirurgia Geral", "Clínica Geral")
        self.adicionar_especialidade("Ortopedia", "Cirurgia Geral")

        self.adicionar_medico("Clínica Geral", "Dr. Carlos", "CRM1001")
        self.adicionar_medico("Pediatria", "Dra. Fernanda", "CRM2002")
        self.adicionar_medico("Ortopedia", "Dr. Marcelo", "CRM3003")

        self.registrar_consulta("222.222.222-22", "2024-05-10", "Dr. Carlos", "Gripe forte")
        self.registrar_consulta("111.111.111-11", "2024-03-05", "Dra. Fernanda", "Check-up")
        self.registrar_consulta("222.222.222-22", "2023-11-20", "Dr. Marcelo", "Fratura no braço")


# ----------------------------------------------------------------- interface
def ok(msg: str) -> None:
    print(f"\n✅ {msg}")


def erro(msg: str) -> None:
    print(f"\n❌ ERRO: {msg}")


def tratar(func, *args) -> None:
    """Executa uma ação do sistema e mostra erros de validação de forma amigável."""
    try:
        func(*args)
    except ValueError as e:
        erro(str(e))


def menu_especialidades(s: SistemaHospitalar) -> None:
    while True:
        print("\n--- 1. ÁRVORE DE ESPECIALIDADES ---")
        print("a. Adicionar Especialidade\nb. Adicionar Médico")
        print("c. Buscar Especialidade\nd. Listar Médicos (Recursivo)\nv. Voltar")
        op = input("Opção: ").strip().lower()

        if op == "a":
            nome = input("Nome da nova Especialidade: ")
            pai = input("Especialidade Pai (vazio para Raiz): ").strip()

            def acao():
                s.adicionar_especialidade(nome, pai or None)
                ok(f"Especialidade '{nome.strip()}' adicionada.")
            tratar(acao)
        elif op == "b":
            esp = input("Especialidade do médico: ")
            nome = input("Nome do Médico: ")
            crm = input("CRM do Médico: ")

            def acao():
                m = s.adicionar_medico(esp, nome, crm)
                ok(f"{m.nome} (CRM: {m.crm}) adicionado(a).")
            tratar(acao)
        elif op == "c":
            no = s.buscar_especialidade(input("Nome da Especialidade: "))
            if no:
                ok(f"'{no.nome}' encontrada! {len(no.medicos)} médico(s), "
                   f"{len(no.filhos)} sub-especialidade(s).")
            else:
                erro("Especialidade não encontrada.")
        elif op == "d":
            nome = input("Especialidade: ")

            def acao():
                print(f"\n--- Médicos em '{nome}' e sub-especialidades ---")
                print("\n".join(s.linhas_medicos(nome)))
            tratar(acao)
        elif op == "v":
            return
        else:
            print("Opção inválida.")


def menu_grafo(s: SistemaHospitalar) -> None:
    while True:
        print("\n--- 2. GRAFO DE RELACIONAMENTO ---")
        print("a. Adicionar Consulta (cria aresta)")
        print("b. Médicos que atenderam um Paciente (por CPF)")
        print("c. Pacientes atendidos por um Médico (por nome)\nv. Voltar")
        op = input("Opção: ").strip().lower()

        if op == "a":
            cpf = input("CPF do Paciente: ")
            medico = input("Nome do Médico: ")
            data = input("Data (AAAA-MM-DD): ")
            tratar(lambda: (s.registrar_consulta(cpf, data, medico, ""),
                            ok("Consulta registrada (prontuário e grafo).")))
        elif op == "b":
            cpf = input("CPF do Paciente: ")

            def acao():
                meds = s.medicos_que_atenderam(cpf)
                print(f"\n--- Médicos que atenderam o CPF {formatar_cpf(cpf)} ---")
                for m in meds:
                    print(f"- {m.nome} (CRM: {m.crm})")
            tratar(acao)
        elif op == "c":
            nome = input("Nome do Médico: ")

            def acao():
                pacs = s.pacientes_do_medico(nome)
                print(f"\n--- Pacientes atendidos por {nome} ---")
                for p in pacs:
                    print(f"- {p.nome} (CPF: {p.cpf})")
            tratar(acao)
        elif op == "v":
            return
        else:
            print("Opção inválida.")


def menu_hash(s: SistemaHospitalar) -> None:
    while True:
        print("\n--- 3. TABELA HASH (PRONTUÁRIOS) ---")
        print("a. Adicionar Consulta ao Prontuário\nb. Buscar Prontuário Completo")
        print("c. Contar Consultas (Recursivo)\nv. Voltar")
        op = input("Opção: ").strip().lower()

        if op == "a":
            cpf = input("CPF do Paciente: ")
            data = input("Data (AAAA-MM-DD): ")
            medico = input("Nome do Médico: ")
            diag = input("Diagnóstico: ")
            tratar(lambda: (s.registrar_consulta(cpf, data, medico, diag),
                            ok("Consulta registrada.")))
        elif op == "b":
            cpf = input("CPF do Paciente: ")

            def acao():
                consultas = s.buscar_prontuario(cpf)
                print(f"\n--- Prontuário (CPF: {formatar_cpf(cpf)}) ---")
                for i, c in enumerate(consultas, 1):
                    print(f"[{i}] {c.data} | {c.medico.nome} | {c.diagnostico}")
            tratar(acao)
        elif op == "c":
            cpf = input("CPF do Paciente: ")
            tratar(lambda: print(f"\nTotal de consultas: {s.contar_consultas(cpf)}"))
        elif op == "v":
            return
        else:
            print("Opção inválida.")


def menu_pacientes(s: SistemaHospitalar) -> None:
    while True:
        print("\n--- 4. BUSCA E ORDENAÇÃO DE PACIENTES ---")
        print("a. Adicionar Paciente\nb. Buscar por Nome (Busca Linear)")
        print("c. Ordenar por Nome (Bubble Sort)\nv. Voltar")
        op = input("Opção: ").strip().lower()

        if op == "a":
            nome = input("Nome: ")
            cpf = input("CPF: ")
            idade_txt = input("Idade: ")

            def acao():
                if not idade_txt.strip().isdigit():
                    raise ValueError("Idade deve ser um número inteiro.")
                p = s.adicionar_paciente(nome, cpf, int(idade_txt))
                ok(f"Paciente '{p.nome}' (CPF: {p.cpf}) adicionado(a).")
            tratar(acao)
        elif op == "b":
            achados = s.buscar_paciente_por_nome(input("Nome ou parte do nome: "))
            print("\n--- Resultado da busca ---")
            for p in achados:
                print(f"- {p.nome} | CPF: {p.cpf} | Idade: {p.idade}")
            if not achados:
                print("- Nenhum paciente encontrado.")
        elif op == "c":
            s.ordenar_pacientes_por_nome()
            ok("Pacientes ordenados por nome (Bubble Sort).")
            for p in s.pacientes:
                print(f"- {p.nome} (CPF: {p.cpf})")
        elif op == "v":
            return
        else:
            print("Opção inválida.")


def menu_principal(s: SistemaHospitalar) -> None:
    while True:
        print("\n" + "=" * 50)
        print("SISTEMA DE GESTÃO HOSPITALAR (ESTRUTURA DE DADOS)")
        print("=" * 50)
        print("1. Árvore de Especialidades")
        print("2. Grafo de Relacionamento (Consultas)")
        print("3. Tabela Hash (Prontuários)")
        print("4. Busca/Ordenação de Pacientes")
        print("5. Relatório Histórico Recursivo")
        print("0. Sair")
        print("-" * 50)
        op = input("Escolha uma opção: ").strip()

        if op == "1":
            menu_especialidades(s)
        elif op == "2":
            menu_grafo(s)
        elif op == "3":
            menu_hash(s)
        elif op == "4":
            menu_pacientes(s)
        elif op == "5":
            cpf = input("CPF do paciente (ex: 222.222.222-22): ")

            def acao():
                linhas = s.relatorio_historico(cpf)
                print(f"\n--- Histórico por ano/mês (CPF: {formatar_cpf(cpf)}) ---\n")
                print("\n".join(linhas))
            tratar(acao)
        elif op == "0":
            print("Encerrando o Sistema de Gestão Hospitalar. Até logo!")
            return
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        menu_principal(SistemaHospitalar())
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")


