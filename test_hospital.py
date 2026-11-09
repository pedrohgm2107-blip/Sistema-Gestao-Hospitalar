import pytest

from hospital import SistemaHospitalar, formatar_cpf, normalizar, validar_data


@pytest.fixture
def sistema():
    """Sistema novo, com os dados de exemplo, para cada teste."""
    return SistemaHospitalar()


# ---- utilitários
def test_formatar_cpf_aceita_digitos_e_pontuacao():
    assert formatar_cpf("11111111111") == "111.111.111-11"
    assert formatar_cpf("111.111.111-11") == "111.111.111-11"


def test_formatar_cpf_invalido():
    with pytest.raises(ValueError):
        formatar_cpf("123")


def test_validar_data_padroniza_zeros():
    assert validar_data("2024-5-10") == "2024-05-10"


def test_validar_data_invalida():
    with pytest.raises(ValueError):
        validar_data("10/05/2024")


def test_normalizar_ignora_acentos_e_maiusculas():
    assert normalizar("  JOÃO ") == "joao"


# ---- pacientes
def test_paciente_duplicado_nao_e_aceito(sistema):
    with pytest.raises(ValueError):
        sistema.adicionar_paciente("Outro Nome", "111.111.111-11", 40)


def test_idade_invalida(sistema):
    with pytest.raises(ValueError):
        sistema.adicionar_paciente("Fulano", "444.444.444-44", 200)


def test_busca_ignora_acentos(sistema):
    achados = sistema.buscar_paciente_por_nome("joao")
    assert [p.nome for p in achados] == ["João Santos"]


def test_bubble_sort_ordena_por_nome(sistema):
    sistema.ordenar_pacientes_por_nome()
    assert [p.nome for p in sistema.pacientes] == ["Ana Lima", "João Santos", "Maria Silva"]


# ---- árvore
def test_arvore_aceita_apenas_uma_raiz(sistema):
    with pytest.raises(ValueError):
        sistema.adicionar_especialidade("Nova Raiz")


def test_crm_e_unico_na_arvore(sistema):
    with pytest.raises(ValueError):
        sistema.adicionar_medico("Pediatria", "Outro Medico", "crm1001")


# ---- consultas, hash e grafo
def test_registrar_consulta_atualiza_prontuario_e_grafo(sistema):
    cpf = "333.333.333-33"
    assert sistema.contar_consultas(cpf) == 0
    sistema.registrar_consulta(cpf, "2024-06-01", "Dr. Carlos", "Check-up")
    assert sistema.contar_consultas(cpf) == 1
    assert [m.crm for m in sistema.medicos_que_atenderam(cpf)] == ["CRM1001"]


def test_consulta_de_paciente_inexistente(sistema):
    with pytest.raises(ValueError):
        sistema.registrar_consulta("999.999.999-99", "2024-06-01", "Dr. Carlos", "x")


def test_contagem_recursiva_de_consultas(sistema):
    assert sistema.contar_consultas("222.222.222-22") == 2


def test_relatorio_mostra_ano_mais_recente_primeiro(sistema):
    linhas = sistema.relatorio_historico("222.222.222-22")
    assert linhas[0] == "▶ ANO: 2024"
    assert any("2023-11-20" in linha for linha in linhas)