# Trabalho Prático: Computação Distribuída

## 1. Visão Geral do Projeto

Este repositório contém o desenvolvimento final do trabalho prático da unidade curricular de Computação Distribuída. O projeto consiste num **Sistema Distribuído em 3 Camadas** para a gestão de conteúdos multimédia e monitorização de sensores IoT.

O sistema foi desenhado com foco no isolamento de processos, escalabilidade horizontal e interoperabilidade, aplicando as melhores práticas lecionadas:
* Contentorização do ambiente de execução.
* Separação lógica entre a camada de apresentação (Web) e a persistência de dados.
* Implementação de uma arquitetura *Stateless* através de uma API RESTful.
* Comunicação assíncrona baseada em eventos para o paradigma IoT (MQTT).

---

## 2. Arquitetura e Orquestração (Docker)

A infraestrutura é gerida pelo ficheiro `docker-compose.yml`, garantindo a instanciação simultânea e isolada dos serviços:

1. **`web_app` (Frontend / Gateway):**
   * **Tecnologia:** Python / Flask
   * **Função:** Interface do utilizador, gestão de sessões cliente-servidor, consumo da API REST e subscrição de tópicos MQTT.
   * **Rede:** `rede-publica` (Expõe a porta `5000` para o host).

2. **`api_server` (Web Service REST):**
   * **Tecnologia:** Python / Flask / psycopg2
   * **Função:** Intermediário estrito e *stateless* que processa os pedidos HTTP vindos do Frontend, executando a lógica de negócio e as *queries* parametrizadas contra injeção de SQL.
   * **Redes:** `rede-publica` (para receber os pedidos) e `rede-privada` (para aceder à base de dados).

3. **`base_dados` (Persistência):**
   * **Tecnologia:** PostgreSQL 15 (Alpine)
   * **Função:** Armazenamento relacional de utilizadores e conteúdos (memórias).
   * **Rede:** `rede-privada` (Isolamento total. Nenhuma porta é exposta para o exterior, garantindo acesso exclusivo pela API).

---

## 3. Evolução das Fases do Projeto

### Fase 1: Sockets TCP e Heterogeneidade
* **Implementação inicial:** Comunicação direta entre processos via Sockets (`socket.SOCK_STREAM`) utilizando o protocolo de transporte TCP.
* **Resolução da Heterogeneidade:** Substituição do envio de estruturas binárias nativas por ficheiros de texto estruturados em **JSON**, garantindo interoperabilidade entre diferentes arquiteturas de hardware e ordenação de bytes (*Big-Endian* vs *Little-Endian*).

### Fase 2: Transição para REST e Base de Dados
* **Migração:** O antigo servidor de dados baseado em sockets foi substituído por uma **API REST** padronizada.
* **Comunicação:** O Frontend consome a API através dos métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`).
* **Estado:** A API foi desenhada para ser totalmente **Stateless**, não retendo informação de sessão, o que facilita o balanceamento de carga. A persistência baseada em ficheiros (`.json`) evoluiu para um SGDB relacional (**PostgreSQL**).

### Fase 3: Dashboard IoT (REST vs MQTT)
Implementação de um painel de monitorização consumindo dados dos sensores do laboratório através de dois modelos distintos:
* **Modelo Cliente/Servidor (REST):** Abordagem síncrona, onde a `web_app` utiliza chamadas `GET` aos endpoints de proxy (`/weather/values` e `/socket/values`).
* **Modelo Publish/Subscribe (MQTT):** Abordagem assíncrona e fracamente acoplada, ideal para IoT. A `web_app` atua como cliente *Subscriber* no broker `cjsg.ddns.net:1883`, atualizando o Dashboard de forma eficiente apenas quando ocorrem novos eventos nos tópicos `/weather` e `/power`.

---

## 4. Tecnologias Utilizadas

* **Linguagem Principal:** Python 3.10
* **Framework Web & API:** Flask, Flask-Session
* **Base de Dados:** PostgreSQL
* **Driver DB:** `psycopg2-binary`
* **Comunicações HTTP:** `requests`
* **Protocolo IoT:** MQTT (`paho-mqtt`)
* **Orquestração:** Docker & Docker Compose
* **Frontend:** HTML5, CSS3, Jinja2

---

## 5. Como Executar o Projeto

**Pré-requisitos:** Ter o Docker e o Docker Compose instalados no sistema.

1. Clonar este repositório para a máquina local.
2. Fazer o *build* e iniciar os contentores em modo *detached*:
   ```bash
   docker compose up --build -d
   ```
3. Aceder à aplicação no navegador através do URL: `http://localhost:5000`
4. Para encerrar os serviços e a rede isolada:
   ```bash
   docker compose down
   ```
*(Nota: O armazenamento local das imagens de upload fica guardado na pasta `/static/uploads`, e a base de dados persiste através do volume gerido pelo Docker).*

---

## 6. Manual de Utilização

Após a execução do ambiente via Docker, a interação com o sistema é feita inteiramente através do *Frontend* Web, que atua como *Gateway* para os restantes microserviços.

**Passo 1: Acesso e Autenticação**
1. Na página inicial, criar uma nova conta no separador de "Registo". A aplicação Web fará um pedido à API REST (`api_server`), que validará os dados e os inserirá de forma segura na base de dados isolada.
2. Efetuar o *Login* para iniciar a sessão (gerida *server-side*).

**Passo 2: Gestão de Memórias (CRUD)**
1. No painel principal, o utilizador visualiza a listagem de memórias registadas.
2. Para adicionar um novo registo, deve preencher os metadados (título, descrição, tipo de local), as coordenadas geográficas e anexar um ficheiro multimédia.
3. O identificador do ficheiro e os metadados são enviados para persistência via API, enquanto o ficheiro físico é armazenado no volume do contentor Web.

**Passo 3: Monitorização IoT (Dashboard)**
1. Navegar para a secção "Dashboard IoT".
2. O ecrã apresentará os dados meteorológicos e de energia do laboratório.
3. O painel atualizar-se-á automaticamente sem necessidade de recarregar a página globalmente, refletindo o comportamento assíncrono mediado pela subscrição do Broker MQTT.

---

## 7. Resultados e Discussão

A implementação do sistema cumpriu todos os requisitos propostos, demonstrando a viabilidade de uma arquitetura modular e distribuída:

* **Isolamento e Segurança:** A orquestração com Docker Compose provou ser eficaz. O acesso direto à base de dados PostgreSQL a partir do exterior foi totalmente bloqueado, forçando todo o tráfego a passar pela API REST, que atua como barreira de segurança (validando *queries* contra *SQL Injection*).
* **Interoperabilidade Alcançada:** Na fase inicial baseada em Sockets TCP, a decisão de serializar os *payloads* em formato JSON garantiu que a comunicação fluísse sem corrupção de dados, mitigando na íntegra os desafios de heterogeneidade de *hardware* (*Endianness*).
* **Eficiência na IoT:** O painel de monitorização permitiu um confronto direto entre os paradigmas REST e MQTT. Observou-se que a via REST exigia processos de *polling* síncronos e contínuos, consumindo recursos no *backend* e gerando tráfego redundante. Em contrapartida, a integração do MQTT provou ser substancialmente mais leve e eficiente, reagindo em tempo real e de forma assíncrona apenas quando novos eventos eram publicados pelos sensores no *Broker*.
* **Documentação e Contratos de API:** A documentação da API REST foi integrada diretamente no código-fonte. O contrato formal da API (as definições de rotas, métodos e esquemas baseados na especificação OpenAPI) foi redigido utilizando a sintaxe YAML e encontra-se documentado em formato de comentários no ficheiro `ApiServer.py`. Nesta fase da implementação, optou-se por esta representação descritiva interna em detrimento da extração para um ficheiro `.yaml` independente ou da ativação da interface gráfica interativa do Swagger.

---

## 8. Declaração de Uso de Inteligência Artificial

No âmbito do desenvolvimento e documentação deste projeto, foram utilizadas ferramentas de Inteligência Artificial Generativa como assistentes de engenharia de software e estruturação documental. O seu uso cingiu-se a:

* **Esclarecimento Arquitetural:** Auxílio na compreensão teórica e comparação entre modelos de comunicação (e.g., Sockets TCP vs. RESTful APIs; *Polling* síncrono vs. *Publish/Subscribe* assíncrono).
* **Revisão e Otimização de Código:** Identificação de boas práticas para a parametrização de *queries* SQL (mitigação de injeções via `psycopg2`) e estruturação do protocolo customizado JSON sobre TCP.
* **Apoio na Redação Técnica:** Melhoria da coesão, clareza e adequação do vocabulário técnico utilizado na redação final deste relatório Markdown.

**Exemplos de tópicos abordados nas validações:**
> Resolução de problemas de heterogeneidade na transmissão de dados via sockets TCP; Impacto no consumo de rede entre chamadas REST e subscrições MQTT; Estruturação de redes *bridge* em Docker Compose para isolamento de bases de dados relacionais.
