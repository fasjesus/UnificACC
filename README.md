# 🚀 Gerador de Barema de Atividades Complementares

Esta é uma aplicação web desenvolvida em Python (com o framework Flask) para automatizar o processo de preenchimento e unificação do barema de Atividades Complementares (AACC) do curso de Ciência da Computação.

A ferramenta carrega o barema correto (para ingressantes até 2022.2 ou a partir de 2023.1) com base no número de matrícula do aluno, permite o preenchimento online dos dados e das horas, e possibilita o anexo de múltiplos certificados por atividade. Ao final, ela gera um único documento PDF, com o barema preenchido e todos os certificados anexados em ordem.

## ✨ Funcionalidades Principais

  * **Validação de Matrícula:** Verifica se a matrícula tem 9 dígitos e se o 5º dígito é '1' ou '2'.
  * **Carregamento Dinâmico de Barema:** Carrega automaticamente a tabela de atividades correta (antiga ou nova) após a validação da matrícula.
  * **Formulário Web Completo:** Inclui campos para dados do discente (Nome, Matrícula, Email), data de verificação automática e logos da universidade.
  * **Validação de Horas:** Impede que o utilizador insira um valor de "C.H. Cumprida" superior ao máximo permitido pela atividade.
  * **Geração de PDF (ReportLab):** Cria um PDF do barema em formato A4 Paisagem, preenchido com todos os dados do formulário e com o layout dos logos.
  * **Contagem de Páginas e Unificação (PyPDF):** Conta corretamente o número de páginas de cada certificado (mesmo que um ficheiro tenha várias páginas) e preenche o barema com os intervalos corretos (ex: "2-3, 5, 6-7").
  * **Interface Intuitiva:** Sistema de upload de ficheiros personalizado que permite anexar múltiplos comprovativos por atividade, com opções de "Alterar Arquivo" e "Remover" (✖).

-----

## 🔧 Pré-requisitos

Antes de começar, certifique-se de que tem o seguinte software instalado:

  * **Python 3.10** (ou superior)
  * **pip** (o gestor de pacotes do Python)

-----

## ⚙️ Instalação e Configuração

Siga estes passos para configurar o ambiente e preparar a aplicação:

**1. Descarregue ou Clone o Projeto:**
Descarregue os ficheiros do projeto (ou clone o repositório) para uma pasta no seu computador.

**2. Navegue para a Pasta do Projeto:**
Abra o seu terminal (CMD, PowerShell, Bash, etc.) e aceda à pasta do projeto:

```bash
cd caminho/para/a/pasta/verificadorHoras
```

**3. Crie um Ambiente Virtual (Altamente Recomendado):**
Isto isola as dependências do projeto do resto do seu sistema.

```bash
# Criar o ambiente
python -m venv venv

# Ativar o ambiente
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

**4. Instale as Dependências:**
Instale as bibliotecas Python necessárias que estão listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

**5. Configure os Ficheiros CSV:**
Certifique-se de que os ficheiros de barema estão na pasta raiz do projeto com os nomes corretos:

  * `barema_antigo.csv`
  * `barema_novo.csv`

**6. Configure as Imagens (Logos):**
Certifique-se de que os seus logos estão na seguinte estrutura de pastas:

```
verificadorHoras/
|-- static/
|   |-- images/
|       |-- logo_uesc.png
|       |-- logo_computacao.png
|-- app.py
|-- ... (outros ficheiros)
```

*(O código `app.py` espera encontrar os logos exatamente nestes caminhos).*

-----

## ▶️ Como Rodar a Aplicação

1.  Certifique-se de que o seu ambiente virtual (venv) está ativado (se o criou).
2.  No terminal, execute o servidor Flask:
    ```bash
    python app.py
    ```
3.  O terminal deverá mostrar que o servidor está a rodar, algo como:
    ```
     * Running on http://127.0.0.1:5000
    ```
4.  Abra o seu navegador de internet (Chrome, Firefox, etc.) e aceda ao endereço:
    **[http://127.0.0.1:5000](https://www.google.com/url?sa=E&source=gmail&q=http://127.0.0.1:5000)**

-----

## 📋 Como Usar a Ferramenta

1.  Aceda à página no seu navegador.
2.  Preencha os campos de **Nome do Discente**, **Email** e **Matrícula**.
3.  O campo de Matrícula deve ter 9 dígitos (ex: `202210123` para o barema antigo ou `202310123` para o novo).
4.  Clique fora do campo de Matrícula. A tabela de atividades correspondente ao seu ano de ingresso será carregada automaticamente.
5.  Preencha os campos **"C.H. Cumprida"** para as atividades que realizou. O formulário não permitirá inserir um valor acima do máximo permitido.
6.  Anexe um ou mais certificados PDF para cada atividade usando os botões **"Escolher Arquivo"**.
      * Pode adicionar mais ficheiros à mesma atividade clicando em **"+ Adicionar outro"**.
      * Pode remover um ficheiro clicando no **"✖"** vermelho.
7.  Quando terminar de preencher, clique no botão **"Gerar PDF Unificado"**.
8.  O download do documento final (barema preenchido em A4 paisagem + todos os certificados anexados) será iniciado automaticamente.