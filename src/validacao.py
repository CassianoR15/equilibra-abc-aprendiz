
def validar_dados(alunos, turmas):

    erros = []

    # Validar existência de alunos e turmas
    if not alunos:
        erros.append("Nenhum aluno encontrado.")

    if not turmas:
        erros.append("Nenhuma turma encontrada.")

    # Validar alunos
    ids_alunos = []

    for aluno in alunos:

        if not aluno.get("nome"):
            erros.append("Aluno sem nome.")

        if aluno.get("sexo") not in ["M", "F"]:
            erros.append(
                f"Sexo inválido: {aluno.get('nome')}"
            )

        if not aluno.get("disponibilidade"):
            erros.append(
                f"Disponibilidade ausente: {aluno.get('nome')}"
            )

        ids_alunos.append(aluno.get("id"))

    if len(ids_alunos) != len(set(ids_alunos)):
        erros.append("Existem IDs de alunos duplicados.")

    # Validar turmas
    ids_turmas = []

    for turma in turmas:

        if turma.get("turno") not in ["MANHA", "TARDE"]:
            erros.append("Turno inválido.")

        capacidade = turma.get("capacidade")

        if (
            not isinstance(capacidade, int)
            or isinstance(capacidade, bool)
            or capacidade <= 0
        ):
            erros.append("Capacidade inválida.")

        ids_turmas.append(turma.get("id"))

    if len(ids_turmas) != len(set(ids_turmas)):
        erros.append("Existem IDs de turmas duplicados.")

    # Validar capacidade total
    capacidade_total = sum(
        turma["capacidade"]
        for turma in turmas
    )

    if capacidade_total < len(alunos):
        erros.append(
            "Capacidade total insuficiente para os alunos."
        )

    # Resultado
    if erros:
        return {
            "valido": False,
            "erros": erros
        }

    return {
        "valido": True,
        "erros": [],
        "total_alunos": len(alunos),
        "total_turmas": len(turmas),
        "capacidade_total": capacidade_total
    }
