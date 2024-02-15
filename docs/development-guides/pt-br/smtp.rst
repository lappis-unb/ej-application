==========
SMTP
==========

A EJ depende de um servidor SMTP para realizar algumas operações como recuperação de senha.
Para isso é preciso indicar qual o servidor será utilizado. Essa configuração é realizada
por meio das seguintes variáveis de ambiente:

- MAILGUN_API_KEY
- MAILGUN_SENDER_DOMAIN

No momento, utilizamos a biblioteca `anymail <https://anymail.dev/en/stable/>`_ para simplificar
a integração com servidores SMTP. Nesse caso, estamos utilizando a API do Mailgun para realizar os disparos.
Acesse a documentação da biblioteca para verificar quais outros serviços são suportados por padrão.
