# RMI
1. Iniciar o Servidor
Abra um terminal e execute:

bash python -m Pyro4.naming
Isso iniciará o serviço de nomes na porta padrão 9090.

2. Iniciar o Servidor do Jogo
Em outro terminal, execute o servidor:

bash python seega_server.py  
Você verá: "Servidor Seega RMI (Pyro4) pronto."

3. Iniciar os Clientes (Dois Jogadores)
Para cada jogador, execute em terminais separados:

bash python seega_client.py  
