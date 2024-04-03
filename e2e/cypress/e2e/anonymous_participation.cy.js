describe('Voting as anonymous user', () => {
  let conversationUrl = "";

  before(() => {
    cy.registerUser();

    cy.url().then(($url) => {
      if($url == `${Cypress.config('baseUrl')}/profile/tour/`) {
        cy.get('form a[hx-post="/profile/tour/?step=skip"]').click()
      }
    })
    cy.createConversation();
    cy.url().then(($url) => {
      conversationUrl = $url
    })

    cy.logout();

  });

  after(() => {
    cy.removesCypressConversation()
    cy.removesCypressUser();
  });

  it('access conversation as anonymous user', () => {
    cy.visit(conversationUrl)
    cy.get('.conversation-header__label').contains('Conversa')
    cy.get('.conversation-header__text').contains('O que você acha do avanço da inteligência artificial na sociedade moderna?')

  })

  it('vote on conversation as anonymous user', () => {
      const votingUrl = `${conversationUrl}/comment/vote`;
      cy.visit(conversationUrl)
      cy.get('.conversation-header__label').contains('Conversa')
      cy.get('.conversation-header__text').contains('O que você acha do avanço da inteligência artificial na sociedade moderna?')
      cy.intercept(votingUrl).as('vote1')
      cy.get('.voting-card__voting-form__choices--agree').click()
      cy.wait('@vote1').then(() => {
        cy.intercept(votingUrl).as('vote2')
        cy.get('.voting-card__voting-form__choices--disagree').click()
        cy.wait('@vote2').then(() => {
          cy.intercept(votingUrl).as('vote3')
          cy.get('.voting-card__voting-form__choices--disagree').click()
          cy.wait('@vote3').then(() => {
            cy.get('h1').contains('Registre-se para continuar')
          })
        })
      })
  })
})
