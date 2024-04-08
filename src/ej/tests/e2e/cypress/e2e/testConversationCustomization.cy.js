describe('Managing custom conversation', () => {
    beforeEach(() => {
      cy.registerUser();

      cy.url().then(($url) => {
        if($url == `${Cypress.config('baseUrl')}/profile/tour/`) {
          cy.get('form a[hx-post="/profile/tour/?step=skip"]').click()
        }
      })
    });

    it('test check custom final voting message', () => {
      cy.createCustomConversation();
      cy.get('.voting-card__message').contains("Muito obrigada pela participação, ela é muito importante.");
      cy.removesCypressConversation("praças públicas");
    })

    it('test check default final voting message', () => {
      cy.createConversation();
      cy.url().then(($url) => {
        const votingUrl = `${$url}/comment/vote`;
        cy.intercept(votingUrl).as('vote1');
        cy.get('.voting-card__voting-form__choices--agree').click();
        cy.wait('@vote1').then(() => {
          cy.intercept(votingUrl).as('vote2');
          cy.get('.voting-card__voting-form__choices--disagree').click();
          cy.wait('@vote2').then(() => {
            cy.intercept(votingUrl).as('vote3');
            cy.get('.voting-card__voting-form__choices--disagree').click();
            cy.wait('@vote3').then(() => {
              cy.get('.voting-card__message').contains("Você já votou em todos os comentários.");
            })
          })
        })
      })
      cy.removesCypressConversation();
    })

    afterEach(() => {
        cy.removesCypressUser();
    });
})
