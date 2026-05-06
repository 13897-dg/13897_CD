# Relatório de Desenvolvimento: Calculadora Complexa (Sockets)

Este documento descreve o processo de desenvolvimento, a arquitetura e as escolhas tecnológicas aplicadas na implementação do sistema distribuído **Calculadora Complexa** com base em Sockets TCP, desenvolvido e testado em ambientes **Java** e **Python**.

## 1. Visão Geral do Projeto
A **Calculadora Complexa** é um sistema cliente-servidor concebido para efetuar operações aritméticas simples (adição, subtração e multiplicação) sobre números complexos. O sistema foi desenvolvido com o foco no uso de Sockets de rede e na comunicação fiável orientada à ligação (TCP). O principal objetivo é demonstrar a troca estruturada de dados através da rede e comprovar a interoperabilidade completa entre aplicações desenvolvidas em linguagens distintas.

## 2. Implementação Técnica

Para garantir que tanto o cliente como o servidor comunicam com clareza, a partilha de informação é feita através de cadeias de caracteres formatadas em **JSON**.

### 2.1. Estrutura de Dados (JSON)
A comunicação assenta num formato comum para assegurar a compatibilidade universal:
* **Pedidos (Request):** O cliente envia um objeto com um *array* `operations`. Cada operação contém uma parte real e uma imaginária para os dois números (`r1`, `i1`, `r2`, `i2`) e um operador em forma de string (`oper` podendo ser `+`, `-`, `*`).
* **Respostas (Response):** O servidor processa todas as operações e devolve um objeto com um *array* `results`. Cada elemento deste *array* contém os resultados (`rRes`, `iRes`) das operações pela ordem correspondente.

### 2.2. Servidor e Cliente em Python
Na variante de **Python**, o servidor e o cliente tiram partido da biblioteca padrão para a manipulação de sockets e conversão de dados:
* **Módulos Nativos:** Utilização do módulo `socket` nativo para a gestão das ligações e `json` nativo (`json.dumps` e `json.loads`) para a serialização.
* **Concorrência (Threads):** O Servidor (`ServidorCalc.py`) encontra-se preparado para suportar múltiplos clientes em simultâneo através do uso do módulo `threading`. Quando um cliente se liga, uma nova Thread `ServidorDedicado` é instanciada para processar os pedidos de forma independente.
* **Cliente:** O script `ClienteCalc.py` conecta-se através de um *socket* TCP (`socket.SOCK_STREAM`), gera a lista de pedidos, codifica-a em JSON de formato *utf-8*, aguarda o pacote de retorno e imprime os cálculos.

### 2.3. Servidor e Cliente em Java
A variante **Java** mantém a mesma lógica processual, utilizando os paradigmas do ecossistema Java:
* **Sockets de Rede:** Utilização das classes `java.net.Socket` (Cliente) e `java.net.ServerSocket` (Servidor). O servidor (`CalculatorServidor`) implementa uma abstração multithreading nativa da interface `Runnable` (no `CalculatorServidorDedicado`), lançando uma Thread independente por cada Socket estabelecido com o cliente.
* **Conversão JSON:** Diferente do Python, que suporta dicionários nativos facilmente traduzíveis para JSON, a implementação Java foca-se na abstração OO. Utiliza a dependência avançada externa **Jackson** (`ObjectMapper` e `ObjectWriter`) para serializar as instâncias das classes (`ComplexRequestList`, `ComplexOperation`, `ComplexResult`) numa *string* transacionável na rede.

## 3. Interoperabilidade Plena (4 Tipos de Comunicação)

Uma das maiores vitórias arquitetónicas deste modelo é o desacoplamento integral entre a interface e o processamento através do protocolo JSON e das normas de rede unificadas (TCP sobre IP). 

Isto resulta na possibilidade prática de realizar **4 tipos de comunicação totalmente interoperáveis**:
1. **Servidor Python ⇔ Cliente Python:** O cenário mais homogéneo, que utiliza as rotinas nativas de codificação Python.
2. **Servidor Java ⇔ Cliente Java:** Uma comunicação estritamente orientada a objetos com a biblioteca Jackson a efetuar a conversão automática nas extremidades.
3. **Servidor Java ⇔ Cliente Python:** Um Cliente Python, que empacota o pedido utilizando os dicionários nativos de Python, envia com sucesso para o Servidor Java. O Java Server interpreta os *bytes*, desserializa a representação genérica numa instância `ComplexRequestList`, faz os cálculos em memória, e o Jackson volta a compor a *string* de resposta, que o Python compreende e desencripta perfeitamente.
4. **Servidor Python ⇔ Cliente Java:** Um Cliente Java fortemente tipado produz e converte os objetos da API Jackson para JSON que são de seguida interpretados dinamicamente no Python usando as funções de parse baseadas em dicionários flexíveis. A resposta volta a ser convertida sem erros em propriedades de uma classe Java.

A arquitetura baseada numa camada de formato de dados neutra (JSON) provou ser completamente invisível à linguagem de implementação de qualquer um dos lados da abstração da comunicação.

## 4. Conclusão
O projeto "Calculadora Complexa" atinge de forma exímia o objetivo pedagógico de testar os fundamentos da comunicação Cliente/Servidor assíncrona baseada em Sockets TCP. Destacam-se o design escalável multithreading de ambos os servidores, a separação de lógica via parse JSON (Jackson e native dicts) e, especialmente, a poderosa flexibilidade do protocolo desenhado, suportando comunicação em malha completa e interoperável entre a máquina virtual da linguagem Java e o interpretador de Python.
