describe('Voting as anonymous user', () => {
  let conversation_id = "";

  it('creates conversation', () => {
    cy.removesCypressUser()
    cy.registerUser()
    cy.url().then(($url) => {
      if($url == `${Cypress.config('baseUrl')}/profile/tour/`) {
        cy.get('form a[hx-post="/profile/tour/?step=skip"]').click()
        cy.createConversation()
        cy.url().then(($url) => {
          // tokens[1] should be the URL conversation id.
          let tokens = $url.match(/.*conversations\/(\d*)\//);
          if (parseInt(tokens[1])) {
            conversation_id = tokens[1];
          }
        })
      }
    })
  })

  it('access conversation as anonymous user', () => {
    cy.visit(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/`)
    cy.get('.conversation-header__label').contains('Conversa')
    cy.get('.conversation-header__text').contains('O que você acha do avanço da inteligência artificial na sociedade moderna?')

  })

  it('vote on conversation as anonymous user', () => {
    cy.visit(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/`)
    cy.get('.conversation-header__label').contains('Conversa')
    cy.get('.conversation-header__text').contains('O que você acha do avanço da inteligência artificial na sociedade moderna?')
    cy.intercept(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/comment/vote`).as('vote1')
    cy.get('.voting-card__voting-form__choices--agree').click()
    cy.wait('@vote1').then(() => {
      cy.intercept(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/comment/vote`).as('vote2')
      cy.get('.voting-card__voting-form__choices--disagree').click()
      cy.wait('@vote2').then(() => {
        cy.intercept(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/comment/vote`).as('vote3')
        cy.get('.voting-card__voting-form__choices--disagree').click()
        cy.wait('@vote3').then(() => {
          cy.get('h1').contains('Registre novo usuário')
        })
      })
    })
  })

  it('removes a conversation from django admin painel', () => {
    cy.removesCypressConversation()
  })
})
