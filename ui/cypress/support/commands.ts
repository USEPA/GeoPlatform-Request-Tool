// ***********************************************
// This example namespace declaration will help
// with Intellisense and code completion in your
// IDE or Text Editor.
// ***********************************************
declare namespace Cypress {
  interface Chainable<Subject = any> {
    solveGoogleReCAPTCHA(): typeof this.solveGoogleReCAPTCHA;
    loginWithCredentials(u: string, p: string): typeof this.loginWithCredentials;
  }
}
//
// function customCommand(param: any): void {
//   console.warn(param);
// }
//
// NOTE: You can use it like so:
// Cypress.Commands.add('customCommand', customCommand);
//
// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add('solveGoogleReCAPTCHA', () => {
  // Wait until the iframe (Google reCAPTCHA) is totally loaded
  cy.wait(500);
  cy.get('iframe[title="reCAPTCHA"]')
    .then($iframe => {
      const $body = $iframe.contents().find('body');
      cy.wrap($body)
        .find('.recaptcha-checkbox-border')
        .should('be.visible')
        .click();
      cy.wait(500)
    });

});

function loginCreds(username, password) {
  cy.visit('/api/auth/login/');
  cy.get('input[name="username"]').type(username, {
    log: false,
  });
  cy.get('input[name="password"]').type(password, {
    log: false,
  });
  cy.get('input[type="submit"]').click();
    // }
  // );
  // cy.visit('/');
}

Cypress.Commands.add('loginWithCredentials' as any, (username: string, password: string) => {
  cy.session(`credentials-${username}`, () => {
    const log = Cypress.log({
      displayName: 'Django credentials login',
      message: [`🔐 Authenticating | ${username}`],
      autoEnd: false,
    });
    log.snapshot('before');

    loginCreds(username, password);

    log.snapshot('after');
    log.end();
  }, {
    validate: () => {
      cy.visit('/');
      cy.get('button#userName', {timeout: 30000}).should('not.contain', 'Login');
    }
  });

});
