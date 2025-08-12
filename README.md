O código implementa a lógica de um servidor RMI (Remote Method Invocation) para o jogo de tabuleiro Seega, permitindo que múltiplos clientes (máximo dois jogadores) se conectem e joguem remotamente com atualização em tempo real do estado do jogo e chat integrado.


# RMI
1. Iniciar o Servidor
Abra um terminal e execute:

bash python -m Pyro4.naming
Isso iniciará o serviço de nomes na porta padrão 9090.

2. Iniciar o Servidor do Jogo
Em outro terminal, execute o servidor:

bash python server.py  
Você verá: "Servidor Seega RMI (Pyro4) pronto."

3. Iniciar os Clientes (Dois Jogadores)
Para cada jogador, execute em terminais separados:

bash python client.py  
