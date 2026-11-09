# Sistema de Gestão Hospitalar

Sistema em Python, com menu de terminal, que organiza especialidades, médicos, pacientes e consultas usando estruturas de dados clássicas. Os dados são salvos em arquivo JSON. Projeto acadêmico.

## Estruturas de dados

| Estrutura | Onde é usada | Complexidade |
|---|---|---|
| Árvore | Especialidades e sub-especialidades, com médicos em cada nó | Busca em profundidade: O(n) |
| Grafo (lista de adjacência) | Relação paciente e médico, criada a cada consulta | Consulta de vizinhos: O(grau) |
| Tabela hash (dict) | Prontuários indexados pelo CPF | Acesso médio: O(1) |
| Busca linear | Busca parcial de pacientes por nome | O(n) |
| Bubble Sort | Ordenação de pacientes por nome, com parada antecipada | O(n²) |
| Recursão | Listagem de médicos na árvore, contagem de consultas e relatório por ano e mês | - |

## Decisões de projeto
- A lógica fica na classe `SistemaHospitalar`, sem `print` nem `input`: ela retorna dados ou levanta `ValueError`, e os menus cuidam da tela.
- Cada consulta é registrada em um único lugar, atualizando prontuário e grafo juntos.
- O grafo usa CPF e CRM como identificadores, evitando conflito entre pessoas com o mesmo nome.
- Busca e ordenação ignoram acentos e diferença entre maiúsculas e minúsculas.
- Ao salvar, o grafo não vai para o arquivo: ele é reconstruído a partir das consultas, evitando dados duplicados.

## Estrutura do projeto

```
src/hospital.py       lógica do sistema e menus
src/persistencia.py   salvar e carregar dados em JSON
src/main.py           ponto de entrada
test/                 testes automáticos
```

## Como rodar
Requer Python 3.9 ou superior, sem bibliotecas externas.

```powershell
python src/main.py
```

Os dados são salvos em `dados/hospital.json` ao sair e carregados na próxima execução. Sem esse arquivo, o sistema inicia com dados fictícios de exemplo. Para ver o relatório, escolha a opção 5 e use o CPF `222.222.222-22`.

## Exemplo de saída

```
▶ ANO: 2024
  ↳ MÊS: 05 - Maio
    • 2024-05-10 | Dr. Carlos | Gripe forte
▶ ANO: 2023
  ↳ MÊS: 11 - Novembro
    • 2023-11-20 | Dr. Marcelo | Fratura no braço
```

## Testes
Os 18 testes automáticos cobrem formatação de CPF e data, busca sem acentos, Bubble Sort, regras da árvore (raiz única e CRM único), consultas no prontuário e no grafo, contagem recursiva, relatório por ano e o salvamento e carregamento dos dados em JSON.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install pytest
python -m pytest
```

## Limitações
- Os dados ficam em um arquivo JSON local, sem criptografia nem controle de acesso.
- O CPF é validado apenas pelo formato (11 dígitos), sem os dígitos verificadores.
- A contagem recursiva de consultas é didática: acima de cerca de mil consultas por paciente, bateria no limite de recursão do Python.
- Todos os dados são fictícios.

## Próximos passos
- Validar os dígitos verificadores do CPF.
- Criar uma interface web ou uma API.