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

  it('try to comment on conversation as anonymous user', () => {
    cy.visit(conversationUrl)
    cy.get('.voting-card__add-comment').click()
    cy.get('textarea').type('adding this comment.')
    cy.intercept(`${conversationUrl}/comment`).as('comment')
    cy.get('button[type="submit"]').click({force: true})
    cy.wait('@comment').then((event) => {
      expect(event.response.statusCode).to.be.equal(200)
    })
  })

  it('access conversation statistics as anonymous user', () => {
    cy.visit(conversationUrl)
    cy.get('.conversation-header__n_participants span').contains("1")
    cy.get('.conversation-header__n_votes span').contains("2")
  })

  it('participation screen should contain author name', () => {
    cy.visit(conversationUrl)
    cy.get("#author-name").contains("Comentário adicionado por Cypress")
  })

  it('anonymous user should not vote on hiden conversation', () => {
      cy.login()
      //edit start and end date of conversation
      cy.visit(`${conversationUrl}edit`)
      cy.get("#start_date").type("2024-03-19")
      cy.get('#end_date').type("2024-03-27")
      cy.get('input[type="submit"]').click({force: true})
      cy.visit('/profile/home')

      //author verify if conversation is hidden
      cy.get(`#public-current-cards a[href="${conversationUrl}"]`).should('not.exist')
      cy.logout()
      
      //annymous user verify if conversation is hidden
      cy.visit(conversationUrl)
      cy.get('p').contains('Esta conversa está oculta.')
  })

})
