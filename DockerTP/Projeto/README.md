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

1. **`web_app` (Frontend / Gateway):** * **Tecnologia:** Python / Flask
   * **Função:** Interface do utilizador, gestão de sessões cliente-servidor, consumo da API REST e subscrição de tópicos MQTT.
   * **Rede:** `rede-publica` (Expõe a porta `5000` para o host).

2. **`api_server` (Web Service REST):** * **Tecnologia:** Python / Flask / psycopg2
   * **Função:** Intermediário estrito e *stateless* que processa os pedidos HTTP vindos do Frontend, executando a lógica de negócio e as *queries* parametrizadas contra injeção de SQL.
   * **Redes:** `rede-publica` (para receber os pedidos) e `rede-privada` (para aceder à base de dados).

3. **`base_dados` (Persistência):** * **Tecnologia:** PostgreSQL 15 (Alpine)
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

