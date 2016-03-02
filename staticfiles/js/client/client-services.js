hund.factory('uwn', function() {
    var registred_widgets = [];
    var registerWidget = function(widget) {
        registred_widgets.push(widget);
        return registred_widgets.length;
    };
    return {
        registerWidget: registerWidget
    };
});