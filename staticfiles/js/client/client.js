var hund = angular.module('hund', []);

hund.config(function($interpolateProvider, $httpProvider) {
    $httpProvider.defaults.headers.common['X-CSRFToken'] = csrf_token;

    //// Change default template tags
    $interpolateProvider.startSymbol('((');
    $interpolateProvider.endSymbol('))');
});