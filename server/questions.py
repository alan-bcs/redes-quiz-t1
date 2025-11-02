questionsC1 = [
    {
        "question": "Qual é a principal diferença entre a comutação de pacotes (packet switching) e a comutação de circuitos (circuit switching)?",
        "options": {
            "A": "A comutação de pacotes pode levar a atrasos e perdas por enfileiramento, enquanto a comutação de circuitos oferece desempenho garantido.",
            "B": "A comutação de pacotes reserva recursos de ponta a ponta para uma conexão, enquanto a comutação de circuitos compartilha recursos sob demanda.",
            "C": "A comutação de circuitos é mais adequada para dados em rajadas ('bursty data').",
            "D": "A comutação de pacotes não requer configuração de chamada ('call setup'), mas a comutação de circuitos sim."
        },
        "answer": "A"
    },
    {
        "question": "Quais são as quatro principais fontes de atraso (delay) de um pacote em uma rede?",
        "options": {
            "A": "Atraso do servidor, atraso do cliente, atraso da aplicação e atraso físico.",
            "B": "Atraso de processamento, atraso de enfileiramento, atraso de transmissão e atraso de propagação.",
            "C": "Atraso de TCP, atraso de IP, atraso de HTTP e atraso de Ethernet.",
            "D": "Atraso de congestionamento, atraso de roteamento, atraso de comutação e atraso de link."
        },
        "answer": "C"
    },
    {
        "question": "No modelo de camadas da Internet, qual camada é responsável pelo roteamento de datagramas da origem ao destino através de múltiplos roteadores?",
        "options": {
            "A": "Camada de Aplicação",
            "B": "Camada de Transporte",
            "C": "Camada de Enlace (Link)",
            "D": "Camada de Rede"
        },
        "answer": "D"
    },
    {
        "question": "O que é encapsulamento no contexto de protocolos de rede?",
        "options": {
            "A": "É o processo de criptografar uma mensagem para segurança.",
            "B": "É o processo de dividir uma mensagem grande em pacotes menores.",
            "C": "É quando uma camada adiciona seu próprio cabeçalho (header) aos dados recebidos da camada superior.",
            "D": "É a conversão de bits em sinais elétricos ou ópticos para transmissão."
        },
        "answer": "C"
    },
    {
        "question": "Qual das seguintes opções é um exemplo de meio físico de rede guiado?",
        "options": {
            "A": "Rede celular 5G",
            "B": "Cabo de fibra óptica",
            "C": "WiFi",
            "D": "Comunicação via satélite"
        },
        "answer": "B"
    },
    {
        "question": "Um ataque de Negação de Serviço (Denial of Service - DoS) tem como principal objetivo:",
        "options": {
            "A": "Roubar senhas e informações confidenciais interceptando pacotes.",
            "B": "Fingir ser outro computador na rede usando um endereço de origem falso.",
            "C": "Tornar um serviço ou recurso indisponível para usuários legítimos sobrecarregando-o com tráfego.",
            "D": "Instalar software malicioso em um computador para controlá-lo remotamente."
        },
        "answer": "C"
    },
    {
        "question": "O que constitui a 'borda da rede' (network edge)?",
        "options": {
            "A": "Os hosts, como clientes e servidores, onde as aplicações de rede são executadas.",
            "B": "As redes de acesso, como DSL, cabo e redes sem fio.",
            "C": "Roteadores e a malha de links que interconectam as redes.",
            "D": "Os Provedores de Serviço de Internet (ISPs) e os pontos de troca de tráfego (IXPs)."
        },
        "answer": "C"
    },
    {
        "question": "Em uma rota de comunicação, o que é o 'link gargalo' (bottleneck link)?",
        "options": {
            "A": "O link com a maior taxa de transmissão.",
            "B": "O primeiro link pelo qual o pacote passa a partir da origem.",
            "C": "O link no caminho que restringe a vazão (throughput) de ponta a ponta.",
            "D": "O link com o maior atraso de propagação."
        },
        "answer": "C"
    },
    {
        "question": "Qual organização é primariamente responsável por desenvolver e promover os padrões da Internet, como os RFCs (Request for Comments)?",
        "options": {
            "A": "IEEE (Institute of Electrical and Electronics Engineers)",
            "B": "ISO (International Organization for Standardization)",
            "C": "ARPAnet (Advanced Research Projects Agency Network)",
            "D": "IETF (Internet Engineering Task Force)"
        },
        "answer": "D"
    },
    {
        "question": "Qual das seguintes tecnologias de acesso à rede é caracterizada por compartilhar a capacidade de transmissão entre várias residências em uma vizinhança?",
        "options": {
            "A": "DSL (Digital Subscriber Line)",
            "B": "Rede de Acesso por Cabo (Cable-based access)",
            "C": "Fibra Óptica Ponto a Ponto",
            "D": "Conexão Discada (Dial-up)"
        },
        "answer": "B"
    }
]

questionsC2 = [
    {
        "question": "Qual é a principal função do protocolo DNS (Domain Name System)?",
        "options": {
            "A": "Transferir arquivos entre um cliente e um servidor.",
            "B": "Traduzir nomes de domínio legíveis por humanos em endereços IP.",
            "C": "Criptografar a comunicação entre o navegador e o servidor web.",
            "D": "Gerenciar o envio e recebimento de e-mails."
        },
        "answer": "B"
    },
    {
        "question": "O protocolo HTTP é considerado 'stateless' (sem estado). O que isso significa?",
        "options": {
            "A": "O servidor armazena informações detalhadas sobre cada cliente que se conecta.",
            "B": "Cada requisição HTTP é tratada de forma independente, sem que o servidor guarde informações de requisições anteriores.",
            "C": "A conexão TCP é mantida aberta indefinidamente.",
            "D": "O protocolo não precisa de uma camada de transporte confiável."
        },
        "answer": "B"
    },
    {
        "question": "Qual tecnologia é usada por websites para manter o estado entre transações, como em carrinhos de compra?",
        "options": {
            "A": "DNS",
            "B": "UDP",
            "C": "Sockets",
            "D": "Cookies"
        },
        "answer": "D"
    },
    {
        "question": "No contexto de e-mail, qual protocolo é usado para transferir mensagens entre servidores de e-mail?",
        "options": {
            "A": "HTTP (Hypertext Transfer Protocol)",
            "B": "IMAP (Internet Message Access Protocol)",
            "C": "SMTP (Simple Mail Transfer Protocol)",
            "D": "DNS (Domain Name System)"
        },
        "answer": "C"
    },
    {
        "question": "Qual dos seguintes serviços de transporte da Internet oferece entrega confiável de dados e controle de fluxo?",
        "options": {
            "A": "UDP (User Datagram Protocol)",
            "B": "TCP (Transmission Control Protocol)",
            "C": "IP (Internet Protocol)",
            "D": "HTTP (Hypertext Transfer Protocol)"
        },
        "answer": "B"
    },
    {
        "question": "Um código de status HTTP '404 Not Found' significa que:",
        "options": {
            "A": "A requisição foi bem-sucedida e o objeto está sendo enviado.",
            "B": "O objeto solicitado foi movido permanentemente para um novo local.",
            "C": "O servidor não conseguiu encontrar o documento ou recurso solicitado.",
            "D": "A requisição enviada pelo cliente não foi entendida pelo servidor."
        },
        "answer": "C"
    },
    {
        "question": "No paradigma cliente-servidor, qual é a característica de um servidor?",
        "options": {
            "A": "Possui um endereço IP dinâmico e está conectado de forma intermitente.",
            "B": "É um host que está sempre ativo ('always-on') e possui um endereço IP permanente.",
            "C": "Inicia a comunicação com o cliente.",
            "D": "Não se comunica diretamente com outros servidores."
        },
        "answer": "B"
    },
    {
        "question": "O que é um socket no contexto de programação de redes?",
        "options": {
            "A": "Um endereço IP e um número de porta.",
            "B": "Uma interface de software que serve como uma 'porta' entre o processo da aplicação e o protocolo de transporte.",
            "C": "Um protocolo de camada de aplicação para troca de mensagens.",
            "D": "Um dispositivo físico de rede para conectar múltiplos computadores."
        },
        "answer": "B"
    },
    {
        "question": "Qual é a principal vantagem de se usar Web Caching (ou Proxy Servers)?",
        "options": {
            "A": "Aumentar a segurança da conexão, criptografando todos os dados.",
            "B": "Reduzir o tempo de resposta para o cliente e o tráfego na rede, armazenando cópias de objetos localmente.",
            "C": "Garantir que os usuários sempre recebam a versão mais recente de uma página web, sem exceções.",
            "D": "Permitir que múltiplos usuários editem a mesma página web simultaneamente."
        },
        "answer": "B"
    },
    {
        "question": "A tecnologia DASH (Dynamic, Adaptive Streaming over HTTP) é usada em streaming de vídeo para:",
        "options": {
            "A": "Fornecer uma taxa de bits constante (CBR) para garantir a qualidade máxima do vídeo.",
            "B": "Permitir que o cliente escolha a qualidade do vídeo dinamicamente com base na largura de banda disponível.",
            "C": "Transmitir o vídeo inteiro de uma só vez para evitar buffering.",
            "D": "Criptografar o conteúdo de vídeo para evitar pirataria."
        },
        "answer": "B"
    }
]