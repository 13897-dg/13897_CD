# Relatório de Desenvolvimento: Arquitetura Cliente/Servidor com Contentorização e Sockets TCP

## 1. Visão Geral do Projeto
Este documento detalha o desenvolvimento e a arquitetura de um Sistema Distribuído para gestão de conteúdos multimédia e localizações geográficas. O projeto adota um modelo de comunicação **Cliente/Servidor**, separando logicamente a camada de apresentação da camada de persistência de dados. 

Para garantir o isolamento, a interoperabilidade e a consistência do ambiente de execução, o sistema foi integralmente contentorizado utilizando o motor Docker, sendo composto por dois nós independentes:
1. **Servidor Web (`web_app`)**: Atua como o cliente no modelo de distribuição, gerindo a interface, as sessões dos utilizadores e a lógica de apresentação.
2. **Servidor de Dados (`data_app`)**: Atua como o servidor de persistência, processando pedidos de leitura e escrita num sistema de ficheiros estruturado em formato JSON.

## 2. Arquitetura e Orquestração (Docker Compose)
A infraestrutura do sistema é orquestrada através do ficheiro `docker-compose.yml`, que estabelece a topologia da rede e o isolamento dos processos.

* **Isolamento de Rede**: Foi criada uma rede interna do tipo *bridge* (`rede-sockets`). O contentor `data_app` não expõe qualquer porta para a máquina *host*, garantindo que a base de dados em ficheiros está estritamente protegida contra acessos externos. 
* **Acesso Externo**: Apenas o contentor `web_app` expõe a porta `5000` para a máquina hospedeira, centralizando o tráfego HTTP dos utilizadores.
* **Gestão de Dependências de Arranque**: A diretiva `depends_on` garante que o servidor Web apenas inicia o seu processo após o servidor de dados estar instanciado na rede virtual.

## 3. Comunicação Inter-Processos (Sockets TCP e JSON)
Em conformidade com os requisitos iniciais, a comunicação entre o Servidor Web e o Servidor de Dados foi implementada utilizando a interface de **Sockets** ao nível da camada de transporte.

### 3.1. Protocolo de Transporte (TCP)
Foi adotado o protocolo **TCP (Transmission Control Protocol)** (`socket.SOCK_STREAM`) para garantir uma comunicação orientada à conexão, fiável e que preserva a ordem de transmissão dos pacotes de dados. Isto assegura que a transferência de operações de leitura e escrita entre os contentores não sofre perdas.

### 3.2. Resolução da Heterogeneidade (JSON)
Para contornar os problemas clássicos de heterogeneidade de hardware em sistemas distribuídos (como discrepâncias de alinhamento ou ordenação de bytes *Big Endian* vs *Little Endian*), evitou-se a transmissão de estruturas binárias puras. 
A troca de mensagens foi implementada através do envio de *strings* serializadas em formato **JSON** e codificadas em UTF-8. O protocolo aplicacional customizado define uma estrutura chave-valor para cada pedido, por exemplo:
`{"acao": "VERIFY_USER", "dados": {"email": "...", "password": "..."}}`

O Servidor de Dados descodifica o fluxo de bytes, interpreta a ação solicitada, interage com os ficheiros locais correspondentes (`users.json` ou `conteudos.json`) e devolve uma resposta estruturada de volta pelo socket.

## 4. Camada de Apresentação e Funcionalidades (Flask)
O contentor Web aloja a aplicação desenvolvida em Python (Flask) e foca-se exclusivamente na interação com o utilizador final, delegando a persistência para o `data_app`.

* **Autenticação e Sessões**: Gestão de acessos (Login/Logout) suportada pelo `flask_session`, com armazenamento de sessões seguro (Server-side) em detrimento de cookies vulneráveis no cliente.
* **Operações CRUD**: Lógica de negócio para listagem, inserção, pesquisa e eliminação de conteúdos. A aplicação Web processa os pedidos HTTP recebidos e traduz os mesmos para chamadas RPC (*Remote Procedure Call*) simuladas através dos Sockets TCP.
* **Internacionalização (i18n)**: Sistema dinâmico de tradução através da injeção de dicionários no contexto dos *templates* Jinja2, permitindo a alternância de idiomas.
* **Gestão de *Uploads***: Os ficheiros físicos (imagens/vídeos) são armazenados num volume local no contentor Web. Para evitar colisões, o sistema gera UUIDs (Identificadores Únicos Universais) para os nomes dos ficheiros, transmitindo apenas este identificador para o Servidor de Dados.

## 5. Conclusão
O desenvolvimento desta solução reflete a aplicação prática dos conceitos centrais de Computação Distribuída. A separação estrita entre a camada de apresentação e os dados mitiga pontos únicos de falha e facilita a escalabilidade independente de cada módulo. Adicionalmente, o uso de contentores resolve os problemas de inconsistência ambiental, enquanto a comunicação via TCP com *payloads* em JSON garante interoperabilidade, eficiência e fiabilidade na troca de informações entre os processos distribuídos.
