describe('Managing a conversaion', () => {
  let conversation_id = "";
  it('creates conversation', () => {
    cy.removesCypressUser()
    cy.registerUser()
    cy.url().then(($url) => {
      if($url == `${Cypress.config('baseUrl')}/profile/tour/`) {
        cy.get('form a[hx-post="/profile/tour/?step=skip"]').click()
      }
    })
    cy.createConversation()
    cy.url().then(($url) => {
      // tokens[1] should be the URL conversation id.
      let tokens = $url.match(/.*conversations\/(\d*)\//);
      if (parseInt(tokens[1])) {
        conversation_id = tokens[1];
      }
    })
  })

  it('access conversation participation page', () => {
    cy.login()
    cy.visit(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/`)
    cy.get('.conversation-header__label').contains('Conversa')
    cy.get('.conversation-header__text').contains('O que você acha do avanço da inteligência artificial na sociedade moderna?')
  })

  it('add comment to conversation', () => {
    cy.login()
    cy.visit(`/cypressmailcom/conversations/${conversation_id}/avancos-da-ia/`)
    cy.get('.voting-card__label.voting-card__add-comment').click({force: true})
    cy.get('#id_content').type("Um comentário do Cypress na conversa de IA")
    cy.get('.modal__buttons button[type=submit]').click()
  })

  it('removes a conversation from django admin painel', () => {
    cy.removesCypressConversation()
  })
})
