import random
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Gerador de Fichas de Trabalho", page_icon="📝")

# ---------------------------------------------------------------- DADOS
VERBOS = [
    ("play", "plays", "football every day"),
    ("eat", "eats", "breakfast at seven o'clock"),
    ("watch", "watches", "TV in the evening"),
    ("study", "studies", "English on Mondays"),
    ("go", "goes", "to school by bus"),
    ("drink", "drinks", "water every morning"),
    ("read", "reads", "a book before bed"),
    ("live", "lives", "in Luanda"),
    ("work", "works", "in a shop"),
    ("have", "has", "a big family"),
    ("wash", "washes", "the car on Sunday"),
    ("cook", "cooks", "dinner at home"),
]
SUJEITOS = [
    ("I", False), ("You", False), ("We", False), ("They", False),
    ("My friends", False), ("The children", False),
    ("He", True), ("She", True), ("My mother", True),
    ("The teacher", True), ("Pedro", True), ("The dog", True),
]
SUJEITOS_BE = [
    ("I", "am"), ("You", "are"), ("He", "is"), ("She", "is"), ("It", "is"),
    ("We", "are"), ("They", "are"), ("Maria", "is"), ("The boys", "are"),
    ("My father", "is"), ("The cat", "is"), ("You and I", "are"),
]
COMPL_BE = [
    "happy", "tired", "at home", "in the classroom",
    "from Angola", "ready", "hungry", "late",
]
PLURAIS = [
    ("book", "books"), ("box", "boxes"), ("child", "children"), ("man", "men"),
    ("woman", "women"), ("city", "cities"), ("foot", "feet"), ("tooth", "teeth"),
    ("bus", "buses"), ("knife", "knives"), ("mouse", "mice"), ("baby", "babies"),
    ("dog", "dogs"), ("watch", "watches"), ("day", "days"), ("leaf", "leaves"),
    ("person", "people"), ("class", "classes"), ("toy", "toys"), ("fish", "fish"),
]
VOCABULARIO = [
    ("casa", "house"), ("escola", "school"), ("livro", "book"), ("mesa", "table"),
    ("cadeira", "chair"), ("janela", "window"), ("porta", "door"), ("gato", "cat"),
    ("cão", "dog"), ("água", "water"), ("pão", "bread"), ("leite", "milk"),
    ("maçã", "apple"), ("amigo", "friend"), ("família", "family"), ("mãe", "mother"),
    ("pai", "father"), ("irmão", "brother"), ("irmã", "sister"), ("professor", "teacher"),
    ("aluno", "student"), ("carro", "car"), ("sol", "sun"), ("lua", "moon"),
    ("rua", "street"), ("cidade", "city"), ("praia", "beach"), ("cor", "colour"),
]

NIVEIS = {1: "Fácil", 2: "Médio", 3: "Difícil"}
MAXV = {1: 20, 2: 100, 3: 1000}


# ---------------------------------------------------------------- GERADORES
def g_adicao(n):
    a, b = random.randint(1, MAXV[n] // 2), random.randint(1, MAXV[n] // 2)
    return f"{a} + {b} = __", str(a + b)


def g_subtracao(n):
    a = random.randint(2, MAXV[n])
    b = random.randint(1, a)
    return f"{a} - {b} = __", str(a - b)


def g_multiplicacao(n):
    if n == 3:
        a, b = random.randint(11, 99), random.randint(2, 9)
    else:
        m = 5 if n == 1 else 10
        a, b = random.randint(2, m), random.randint(2, m)
    return f"{a} x {b} = __", str(a * b)


def g_divisao(n):
    d = random.randint(2, {1: 5, 2: 9, 3: 12}[n])
    q = random.randint(2, {1: 9, 2: 12, 3: 50}[n])
    r = random.randint(0, d - 1)
    return f"{d * q + r} : {d} = __ resto __", f"{q} resto {r}"


def g_mista(n):
    return random.choice([g_adicao, g_subtracao, g_multiplicacao, g_divisao])(n)


def g_present_simple(_):
    base, terceira, comp = random.choice(VERBOS)
    suj, tp = random.choice(SUJEITOS)
    return f"{suj} ____ ({base}) {comp}.", terceira if tp else base


def g_to_be(_):
    suj, forma = random.choice(SUJEITOS_BE)
    return f"{suj} ____ {random.choice(COMPL_BE)}.", forma


def g_plurais(_):
    s, p = random.choice(PLURAIS)
    return f"{s} -> ____", p


def g_vocabulario(_):
    pt, en = random.choice(VOCABULARIO)
    return f"{pt} = ____", en


# nome -> (gerador, instrução, colunas, altura da linha, usa dificuldade)
TIPOS = {
    "Matemática": {
        "Adição": (g_adicao, "Resolve as adições.", 2, 13, True),
        "Subtração": (g_subtracao, "Resolve as subtrações.", 2, 13, True),
        "Multiplicação": (g_multiplicacao, "Resolve as multiplicações.", 2, 13, True),
        "Divisão com resto": (g_divisao, "Resolve as divisões. Escreve o quociente e o resto.", 1, 13, True),
        "Mista": (g_mista, "Resolve as operações.", 2, 13, True),
    },
    "Inglês": {
        "Present Simple": (g_present_simple, "Completa as frases com a forma correta do verbo (Present Simple).", 1, 14, False),
        "Verb to be": (g_to_be, "Completa as frases com am, is ou are.", 1, 14, False),
        "Plurais": (g_plurais, "Escreve o plural das palavras.", 2, 13, False),
        "Vocabulário PT -> EN": (g_vocabulario, "Traduz as palavras para inglês.", 2, 13, False),
    },
}


def gerar_exercicios(gerador, nivel, n):
    """Gera n exercícios, evitando repetições sempre que possível."""
    vistos, lista, tentativas = set(), [], 0
    while len(lista) < n and tentativas < n * 30:
        tentativas += 1
        q, a = gerador(nivel)
        if q not in vistos:
            vistos.add(q)
            lista.append((q, a))
    while len(lista) < n:  # se faltarem combinações, permite repetir
        lista.append(gerador(nivel))
    return lista


# ---------------------------------------------------------------- PDF
def limpar(texto):
    """As fontes base do PDF só aceitam latin-1 (inclui acentos portugueses)."""
    trocas = {"→": "->", "–": "-", "—": "-", "“": '"', "”": '"',
              "‘": "'", "’": "'", "…": "...", "•": "-"}
    for a, b in trocas.items():
        texto = texto.replace(a, b)
    return texto.encode("latin-1", "replace").decode("latin-1")


def desenhar_lista(pdf, itens, colunas, altura, y_inicial, tamanho):
    largura = 190 / colunas
    pdf.set_font("Helvetica", "", tamanho)
    y = y_inicial
    for i, texto in enumerate(itens):
        col = i % colunas
        if col == 0:
            if i > 0:
                y += altura
            if y + altura > 280:
                pdf.add_page()
                y = 20
        pdf.set_xy(10 + col * largura, y)
        pdf.cell(largura, altura, limpar(texto))


def criar_pdf(titulo, instrucao, exercicios, colunas, altura, escola, professor, com_solucoes):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    if escola:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, limpar(escola), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, limpar(titulo), align="C", new_x="LMARGIN", new_y="NEXT")
    if professor:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, limpar(f"Professor(a): {professor}"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(110, 8, "Nome: __________")
    pdf.cell(0, 8, "Data: __ / __ / ____", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(110, 8, "Turma: ____")
    pdf.cell(0, 8, "Nota: ____", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 7, limpar(instrucao), new_x="LMARGIN", new_y="NEXT")

    y0 = pdf.get_y() + 4
    desenhar_lista(pdf, [f"{i + 1}) {q}" for i, (q, _) in enumerate(exercicios)],
                   colunas, altura, y0, 13)

    if com_solucoes:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Soluções (professor)", align="C", new_x="LMARGIN", new_y="NEXT")
        desenhar_lista(pdf, [f"{i + 1}) {a}" for i, (_, a) in enumerate(exercicios)],
                       3, 9, 30, 12)

    return bytes(pdf.output())


# ---------------------------------------------------------------- INTERFACE
st.title("📝 Gerador de Fichas de Trabalho")
st.caption("Cria fichas em PDF com exercícios novos de cada vez.")

disciplina = st.selectbox("Disciplina", list(TIPOS.keys()))
tipo = st.selectbox("Tipo de exercício", list(TIPOS[disciplina].keys()))
gerador, instrucao, colunas, altura, usa_nivel = TIPOS[disciplina][tipo]

if usa_nivel:
    nivel = st.select_slider("Dificuldade", options=[1, 2, 3], value=2,
                             format_func=lambda x: NIVEIS[x])
else:
    nivel = 1

n = st.slider("Número de exercícios", 4, 40, 20)
titulo = st.text_input("Título da ficha", value=f"Ficha de {disciplina} - {tipo}")
escola = st.text_input("Escola ou nome do curso (opcional)")
professor = st.text_input("Professor(a) (opcional)")

if st.button("Gerar ficha", type="primary", use_container_width=True):
    exercicios = gerar_exercicios(gerador, nivel, n)
    st.session_state["ficha"] = {
        "exercicios": exercicios,
        "aluno": criar_pdf(titulo, instrucao, exercicios, colunas, altura, escola, professor, False),
        "professor": criar_pdf(titulo, instrucao, exercicios, colunas, altura, escola, professor, True),
    }

ficha = st.session_state.get("ficha")
if ficha:
    st.success("Ficha pronta.")
    st.download_button("⬇️ PDF para o aluno", ficha["aluno"],
                       file_name="ficha_aluno.pdf", mime="application/pdf",
                       use_container_width=True)
    st.download_button("⬇️ PDF com soluções (professor)", ficha["professor"],
                       file_name="ficha_professor.pdf", mime="application/pdf",
                       use_container_width=True)
    with st.expander("Pré-visualizar exercícios"):
        for i, (q, a) in enumerate(ficha["exercicios"], 1):
            st.write(f"{i}) {q}   *→ {a}*")