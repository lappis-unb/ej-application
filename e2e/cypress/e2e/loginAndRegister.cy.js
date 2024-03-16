describe('The login page', () => {
  it('trigger error for unexistent user', () => {
    cy.removesCypressUser()
    cy.login()
    cy.get(".errorlist li").should('contain', 'E-mail ou senha inválida')
  })

  it('Check our welcome for new user', () => {
    cy.registerUser()
    cy.get('.welcome h1').should('contain', 'Bem vindo à EJ')
    cy.removesCypressUser()
  })
})
