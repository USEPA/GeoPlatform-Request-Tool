describe('Anonymous submission', () => {
  it('anyone can submit account request', () => {
    cy.visit('/')
    cy.get('input[formcontrolname="first_name"]').type('Test')
    cy.get('input[formcontrolname="last_name"]').type('User')
    cy.get('input[formcontrolname="email"]').type('notanemail')

    cy.get('mat-error').first().should('contain', 'Not a valid email')

  })

  it('shows invalid email error', () => {

  })
})
