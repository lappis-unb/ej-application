# Cypress

Essa pasta contem testes de aceitação implementados com a ferramenta [Cypress](https://www.cypress.io/).
O objetivo é garantir que a jornada do usuário não quebre e, caso quebre, o
time de desenvolvimento consiga identificar problemas que seriam complexos de
capturar com o pytest. A principio, cobriremos apenas alguns cenários
da aplicação com Cypress. Para mudanças de backend, continuaremos utilizando
o pytest.

## Instalação

Para instalar o Cypress, execute o comando (dentro da pasta `e2e`):
    
    npm install

Para abrir o painel de testes, execute o comando:

    npx cypress open


Antes de rodar os testes, é necessário criar um usuário superadmin no Django, com as mesmas 
credenciais do dicionário `adminCredentials`, definido no arquivo `e2e/cypress.config.js`.

Para rodar os testes em modo *headless* (sem abrir a tela do navegador), execute o comando:

    npx cypress run

## Cenários de teste

Cobriremos os seguintes cenários com os testes do Cypress:

1. login e registro.
2. Criação de uma conversa.
3. Acesso à pagina de participação no modo logado.
4. Acesso à página de participação no modo anônimo.
5. Votação em uma conversa.
6. Adição de comentários em uma conversa.

No arquivo `cypress/support/commands.js` manteremos funções customizadas
que serão reutilizadas nos seguintes cenários de teste. Até o momento, temos
as seguintes funções:

1. **cy.login()**: realiza login na plataforma.
2. **cy.logout()**: realiza logout na plataforma.
3. **cy.removesCypressUser()**: remove o usuário criado pelo Cypress via painel administrativo.
4. **cy.removesCypressConversation()**: remove a conversa criada pelo Cypress via painel administrativo.
5. **cy.registerUser()**: registra um novo usuário
6. cy.createConversation(): cria uma conversa utilizando o formulário da área logada.

Todas as issues que impactarem diretamente a jornada de participação, deverão ter um teste com Cypress
para validar que novas versões da plataforma não quebrem para o usuário.
