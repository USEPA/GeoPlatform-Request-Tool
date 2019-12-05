// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.


export const environment = {
  production: true,
  oauth_url: 'https://epa.maps.arcgis.com/sharing/rest/oauth2/authorize',
  oauth_client_id: 'corlAY2HXVlIiR4L',
  oauth_response_type: 'token',
  oauth_redirect_uri: 'http://localhost:4200/oauthcallback',
  local_client_id: '9OSDWC6V7jfELi4K04cuKLEFVgwjUMegUf8Jc1XK',
  local_service_endpoint: 'http://127.0.0.1:8000/api',
  recaptcha_siteKey: '6LeXQboUAAAAAANBXP4FTZ3Pp9MOazFhXaF5CzQN'

};

/*
 * For easier debugging in development mode, you can import the following file
 * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
 *
 * This import should be commented out in production mode because it will have a negative impact
 * on performance if an error is thrown.
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.
