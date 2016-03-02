hund.filter('role_to_name', function() {
    return function(role) {
        return role_to_name(role);
    };
});