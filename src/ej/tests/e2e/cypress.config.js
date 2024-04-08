const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    env: {
      adminCredentials: {
        'email': 'contato@pencillabs.com.br',
        'password': 'pencil5678'
      },
      userCredentiails: {
        'name': 'Cypress',
        'email': 'cypress@mail.com',
        'password': 'cypress1234'
      }
    },
    baseUrl: 'http://localhost:8000',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
