from hospital import SistemaHospitalar
from persistencia import carregar_sistema, salvar_sistema


def test_salvar_e_carregar_preserva_os_dados(tmp_path):
    original = SistemaHospitalar()
    arquivo = tmp_path / "hospital.json"

    salvar_sistema(original, arquivo)
    carregado = carregar_sistema(arquivo)

    cpf = "222.222.222-22"
    assert [p.nome for p in carregado.pacientes] == [p.nome for p in original.pacientes]
    assert carregado.contar_consultas(cpf) == original.contar_consultas(cpf)
    assert carregado.linhas_medicos("Clínica Geral") == original.linhas_medicos("Clínica Geral")
    assert [m.crm for m in carregado.medicos_que_atenderam(cpf)] == [
        m.crm for m in original.medicos_que_atenderam(cpf)
    ]


def test_grafo_e_reconstruido_ao_carregar(tmp_path):
    original = SistemaHospitalar()
    arquivo = tmp_path / "hospital.json"

    salvar_sistema(original, arquivo)
    carregado = carregar_sistema(arquivo)

    assert carregado.grafo == original.grafo


def test_sistema_vazio_pode_ser_salvo_e_carregado(tmp_path):
    arquivo = tmp_path / "vazio.json"

    salvar_sistema(SistemaHospitalar(com_dados_exemplo=False), arquivo)
    carregado = carregar_sistema(arquivo)

    assert carregado.raiz is None
    assert carregado.pacientes == []