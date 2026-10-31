"""
Responsável pelo cadastro, padronização e validação das turmas.

Recebe os dados informados pelo usuário na interface, incluindo
identificação, turno e capacidade das turmas.

Retorna as turmas cadastradas, erros encontrados e possíveis
confirmações pendentes para revisão do usuário.

Os dados preparados serão utilizados pelo modelo de otimização.
"""
# Cadastro e validação das turmas
# Padroniza o turno informado
def padronizar_turno(turno):

    if not isinstance(turno, str):
        return None

    turno = turno.strip().upper()

    equivalencias = {
        "MANHA": "MANHÃ",
        "MANHÃ": "MANHÃ",
        "TARDE": "TARDE"
    }

    return equivalencias.get(turno)


# Realiza o cadastro e a validação das turmas
def cadastrar_turmas(
    dados_turmas,
    capacidades_confirmadas=None,
    limite_revisao=40
):

    turmas = []
    erros = []
    confirmacoes_pendentes = []

    # Índices das capacidades altas que o usuário já confirmou
    if capacidades_confirmadas is None:
        capacidades_confirmadas = set()

    # Verifica se foram recebidos dados
    if not isinstance(dados_turmas, list) or not dados_turmas:
        return {
            "sucesso": False,
            "turmas": [],
            "erros": ["Informe pelo menos uma turma."],
            "confirmacoes_pendentes": []
        }

    # Verifica cada turma recebida
    for indice, dados in enumerate(dados_turmas):

        numero_turma = indice + 1

        # Verifica o formato dos dados recebidos
        if not isinstance(dados, dict):
            erros.append(
                f"Turma {numero_turma}: dados em formato inválido."
            )
            continue

        # 1. Valida e padroniza o turno
        turno = padronizar_turno(dados.get("turno"))

        if turno is None:
            erros.append(
                f"Turma {numero_turma}: turno inválido. "
                "Informe MANHÃ ou TARDE."
            )
            continue

        # 2. Valida a identificação da turma
        identificacao = dados.get("identificacao")

        if not isinstance(identificacao, str) or not identificacao.strip():
            erros.append(
                f"Turma {numero_turma}: "
                "a identificação não pode ficar vazia."
            )
            continue

        identificacao = identificacao.strip().upper()

        identificacao_completa = f"{turno} - {identificacao}"

        # 3. Verifica se já existe uma turma com a mesma identificação e turno
        if any(
            turma["identificacao"] == identificacao_completa
            for turma in turmas
        ):
            erros.append(
                f"Turma {numero_turma}: já existe uma turma "
                f"com a identificação {identificacao_completa}."
            )
            continue

        # 4. Valida a capacidade
        capacidade = dados.get("capacidade")

        # Impede valores que não sejam números inteiros
        if isinstance(capacidade, bool):
            erros.append(
                f"Turma {numero_turma}: informe uma capacidade inteira."
            )
            continue

        try:
            capacidade = int(capacidade)

            # Impede valores decimais, como 20.5
            if isinstance(dados.get("capacidade"), float) and not dados.get("capacidade").is_integer():
                raise ValueError

        except (ValueError, TypeError):
            erros.append(
                f"Turma {numero_turma}: capacidade inválida. "
                "Informe um número inteiro."
            )
            continue

        # Impede capacidades iguais a zero ou negativas
        if capacidade <= 0:
            erros.append(
                f"Turma {numero_turma}: "
                "a capacidade deve ser maior que zero."
            )
            continue

        # 5. Solicita confirmação para capacidades muito altas
        if capacidade > limite_revisao and indice not in capacidades_confirmadas:

            confirmacoes_pendentes.append({
                "indice": indice,
                "turma": identificacao_completa,
                "capacidade": capacidade,
                "mensagem": (
                    f"A capacidade de {capacidade} vagas para "
                    f"{identificacao_completa} parece muito alta. "
                    "Deseja confirmar?"
                )
            })

            continue

        # 6. Adiciona a turma à estrutura de dados
        turmas.append({
            "id": numero_turma,
            "identificacao": identificacao_completa,
            "turno": turno,
            "capacidade": capacidade
        })

    # Se houver erros, não libera o cadastro
    if erros:
        return {
            "sucesso": False,
            "turmas": [],
            "erros": erros,
            "confirmacoes_pendentes": confirmacoes_pendentes
        }

    # Se houver capacidades aguardando confirmação
    if confirmacoes_pendentes:
        return {
            "sucesso": False,
            "turmas": [],
            "erros": [],
            "confirmacoes_pendentes": confirmacoes_pendentes
        }

    # Cadastro concluído
    return {
        "sucesso": True,
        "turmas": turmas,
        "erros": [],
        "confirmacoes_pendentes": []
    }
