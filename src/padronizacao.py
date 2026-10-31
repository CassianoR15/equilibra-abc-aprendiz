
import unicodedata


def normalizar_texto(valor):

    if valor is None:
        return ""

    texto = str(valor).strip().upper()

    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )


def padronizar_nome(valor):

    if valor is None:
        return ""

    return " ".join(
        str(valor).strip().split()
    )


def padronizar_sexo(valor):

    texto = normalizar_texto(valor)

    if texto in ["M", "MASCULINO"]:
        return "M"

    if texto in ["F", "FEMININO"]:
        return "F"

    return None


def padronizar_disponibilidade(valor):

    texto = normalizar_texto(valor)

    if texto in ["MANHA", "MATUTINO"]:
        return "MANHA"

    if texto in ["TARDE", "VESPERTINO"]:
        return "TARDE"

    return None
