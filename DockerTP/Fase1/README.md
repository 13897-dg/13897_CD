# Relatório de Desenvolvimento: Aplicação Web com Arquitetura de Microserviços (Docker & Sockets)

Este documento descreve o desenvolvimento, arquitetura e funcionamento de um projeto baseado em contentores Docker. O projeto implementa uma aplicação Web (Frontend/Gateway) e um servidor de dados (Backend/Base de Dados) que comunicam de forma assíncrona através de sockets TCP.

## 1. Visão Geral do Projeto
A aplicação consiste num sistema de gestão de "memórias" (conteúdos multimédia associados a localizações geográficas), construído em Python com a framework **Flask**. Para garantir o isolamento e escalabilidade, o sistema foi dividido em dois contentores distintos orquestrados através de **Docker Compose**:
1. **Servidor Web (`web_app`)**: Gere a interface de utilizador, autenticação, sessões e submissão de ficheiros.
2. **Servidor de Dados (`data_app`)**: Atua como uma base de dados *NoSQL* baseada em ficheiros JSON, recebendo comandos de leitura e escrita através de Sockets.

## 2. Arquitetura e Contentores (Docker & Docker Compose)

A infraestrutura é inteiramente gerida pelo `docker-compose.yml`, que define a relação e as portas expostas entre os contentores. Ambos partilham a mesma imagem baseada num único `Dockerfile` (`python:3.10-slim`), mas executam comandos diferentes no arranque.

### 2.1. Docker Compose
* **`servidor_dados`**: Arranca correndo o script `DataServer.py` e não expõe portas para a máquina *host*, sendo acessível apenas dentro da rede interna do Docker (garantindo segurança).
* **`servidor_web`**: Arranca correndo `Server.py`, expõe a porta `5000` para a máquina *host* e tem uma diretiva `depends_on: - servidor_dados`, indicando que o servidor de dados deve iniciar primeiro.

### 2.2. Gestão de Arranque (Handshake)
Para evitar que o Servidor Web tente aceder ao Servidor de Dados antes de este estar completamente "acordado" e pronto a aceitar ligações, foi implementado um mecanismo de *Handshake* no arranque do `Server.py`:
* O Servidor Web tenta abrir um socket de teste para a porta do Servidor de Dados repetidamente.
* Só avança com o arranque da interface Web (porta 5000) depois de receber resposta bem-sucedida do contentor de dados.

## 3. Comunicação Interna (Sockets TCP)

Uma das características principais deste projeto é o abandono de chamadas HTTP/REST convencionais entre a Web e a Base de Dados em prol de **Sockets TCP Puros**.

### 3.1. Protocolo Customizado
A comunicação é feita através do envio de *strings* formatadas e codificadas em bytes (`utf-8`). Foi criado um protocolo leve com três partes divididas por barras verticais (`|`):
`COMANDO | NOME_DO_FICHEIRO | DADOS_JSON`

* **GET**: O Servidor Web envia `GET|users.json`. O Servidor de Dados lê o ficheiro internamente e devolve a totalidade dos dados em formato JSON nativo.
* **POST**: O Servidor Web transforma os dicionários Python em *strings* JSON e envia, por exemplo, `POST|users.json|[{"email": "...", "password": "..."}]`. O servidor de dados guarda a string num ficheiro físico e responde com `"SUCESSO"`.

### 3.2. Vantagens da Abordagem
* Comunicação super-rápida, direta na camada de transporte (TCP) sem o *overhead* adicional de cabeçalhos HTTP.
* Controlo total sobre o *buffer* de dados e gestão de *timeouts* nas operações vitais da aplicação.

## 4. Funcionalidades da Aplicação Web (Flask)

O contentor do Servidor Web foca-se puramente na lógica de interface e sessão:
* **Autenticação de Utilizadores**: Registo, Login e Logout geridos com segurança através do `flask_session` (sessões baseadas no sistema de ficheiros e não em *cookies* inseguros).
* **Gestão de Conteúdos (CRUD)**: Possibilidade de listar, adicionar, editar e apagar memórias (com título, descrição, tipo de local, coordenadas GPS e upload de ficheiro multimédia associado).
* **Internacionalização (i18n)**: Implementação de um sistema dinâmico de tradução (Português/Inglês) que injeta as variáveis no contexto dos templates Jinja2 e permite a mudança de idioma em tempo real via rotas da sessão.
* **Processamento de *Uploads***: Ficheiros de imagem ou documentos são guardados na pasta estática do contentor Web, gerando UUIDs únicos para evitar colisões de nomes, e mantendo apenas a referência (nome) na base de dados JSON.

## 5. Conclusão
Este projeto evidencia os fundamentos críticos na construção de sistemas distribuídos modernos: contentorização eficaz para padronização de ambientes de execução, independência de microserviços e comunicação baixo-nível síncrona/assíncrona através da implementação customizada de Sockets entre as pontes do ecossistema.
