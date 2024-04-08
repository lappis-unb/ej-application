# Cypress

This directory contains e2e tests implemented with [Cypress](https://www.cypress.io/) tool.

## Instalation

To install Cypress, run the command:
    
    npm install

To open Cypress panel, run the command:

    npx cypress open

Before running tests it's necessary to create a Django superadmin user, with the same
`adminCredentials` keys and values, defined in `e2e/cypress.config.js`.

To run tests on headless mode, run the command:

    npx cypress run

## Tests scenarios

Cypress tests cover the following user journey:

1. login and registration.
2. Conversation creation.
3. Accessing the participation page with a logged user.
4. Accessing the participation page with an anonymous user.
5. Voting on conversation.
6. Adding conversation comments.

In `cypress/support/commands.js` file, we keep custom Cypress functions that can be
reused during tests scenarios. Untill now, we have the following functions:

1. **cy.login()**: Login to the plataform.
2. **cy.logout()**: Logout to the plataform.
3. **cy.removesCypressUser()**: Remove the Cypress user created in Django administration panel.
4. **cy.removesCypressConversation()**: removes Cypress user conversation in Django administration panel.
5. **cy.registerUser()**: Register a new user.
6. cy.createConversation(): Creates a conversation using the EJ form.

These tests are also executed during Gitlab CI pipeline.
