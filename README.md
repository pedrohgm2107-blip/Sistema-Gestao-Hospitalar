# Sistema de Gestão Hospitalar

Sistema em Python, com menu de terminal, que organiza especialidades, médicos, pacientes e consultas usando estruturas de dados clássicas. Projeto acadêmico.

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

## Como rodar
Requer Python 3.9 ou superior, sem bibliotecas externas.

```powershell
python src/hospital.py
```

O sistema já inicia com dados fictícios de exemplo. Para ver o relatório, escolha a opção 5 e use o CPF `222.222.222-22`.

## Exemplo de saída

```
▶ ANO: 2024
  ↳ MÊS: 05 - Maio
    • 2024-05-10 | Dr. Carlos | Gripe forte
▶ ANO: 2023
  ↳ MÊS: 11 - Novembro
    • 2023-11-20 | Dr. Marcelo | Fratura no braço
```

## Limitações
- Os dados ficam só em memória e se perdem ao fechar o programa.
- O CPF é validado apenas pelo formato (11 dígitos), sem os dígitos verificadores.
- A contagem recursiva de consultas é didática: acima de cerca de mil consultas por paciente, bateria no limite de recursão do Python.
- Todos os dados são fictícios.

## Próximos passos
- Testes automatizados com pytest.
- Salvar e carregar os dados em arquivo JSON.