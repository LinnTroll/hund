hund.controller('AnimalFormCtrl', function($scope, $rootScope, $http, uwn) {
    $scope.uw_number = uwn.registerWidget($scope);

    $scope.errors = null;

    $scope.empty_pedigree_number = {
        id: null,
        number: ''
    };

    $scope.empty_owner = {
        id: null,
        force_open: false,
        data: {
            id: null,
            name: '',
            address: '',
            phone: '',
            email: '',
            work: ''
        }
    };

    $scope.empty_kennel = {
        id: null,
        force_open: false,
        data: {
            id: null,
            name: '',
            address: '',
            breeder: ''
        }
    };

    $scope.empty_title = {
        id: null,
        title: '',
        info: ''
    };

    var _prepare_data = function(data) {
        var _initial_gender = null;
        var _initial_breed = null;
        var _initial_breed_data = null;

        if ($scope.target_data && $scope.target_data.breed) {
            _initial_breed = $scope.target_data.breed;
        }

        if ($scope.target_data && $scope.target_data.breed_data) {
            _initial_breed_data = $scope.target_data.breed_data;
        }

        if ($scope.role) {
            _initial_gender = $scope.role[$scope.role.length - 1];
        }

        if (data === null || data === undefined) {
            data = {
                pk: null,
                name_ru: '',
                name_en: '',
                gender: _initial_gender,
                color_ru: '',
                color_en: '',
                birthdate: '',
                breed_data: _initial_breed_data,
                breed: _initial_breed,
                mark: '',
                chip: '',
                pedigree_numbers: [_.clone($scope.empty_pedigree_number)],
                owners: [_.clone($scope.empty_owner)],
                kennels: [_.clone($scope.empty_kennel)],
                titles: [_.clone($scope.empty_title)],
                is_our: false,
                reg_number: null,
                reg_date: ''
            };
        }

        return data;
    };

    $scope.data = _prepare_data($scope.data);

    $scope.$watch('data.name_ru', function(name_ru, old_name_ru) {
        if ($scope.data.name_en === translit(old_name_ru, 5)) {
            $scope.data.name_en = translit(name_ru, 5);
        }
    });

    $scope.$watch('data.color_ru', function(color_ru, old_color_ru) {
        if ($scope.data.color_en === translit(old_color_ru || '', 5)) {
            $scope.data.color_en = translit(color_ru || '', 5);
        }
    });

    $scope.$watch('data.breed_data', function(breed_data) {
        if (breed_data && breed_data.id !== undefined) {
            $scope.data.breed = breed_data.id;
        } else {
            $scope.data.breed = null;
        }
    });

    $scope.addPedigreeNumberField = function() {
        $scope.data.pedigree_numbers.push(_.clone($scope.empty_pedigree_number));
    };

    $scope.removePedigreeNumberField = function(index) {
        $scope.data.pedigree_numbers = _.filter($scope.data.pedigree_numbers, function(e, i) {
            return i !== index;
        });
    };

    $scope.addOwnerBlock = function() {
        $scope.data.owners.push(_.clone($scope.empty_owner));
    };

    $scope.editOwnerBlock = function(index) {
        $scope.data.owners[index].force_open = true;
        //$scope.data.owners.push(_.clone($scope.empty_owner));
    };

    $scope.removeOwnerBlock = function(index) {
        $scope.data.owners = _.filter($scope.data.owners, function(e, i) {
            return i !== index;
        });
    };

    $scope.openOwnerAddPopup = function(index) {
        $rootScope.$broadcast('show_owner_add_popup', function(new_owner) {
            var owner = $scope.data.owners[index];
            owner.data = new_owner;
            owner.force_open = false;
        });
    };

    $scope.addKennelBlock = function() {
        $scope.data.kennels.push(_.clone($scope.empty_kennel));
    };

    $scope.editKennelBlock = function(index) {
        $scope.data.kennels[index].force_open = true;
    };

    $scope.removeKennelBlock = function(index) {
        $scope.data.kennels = _.filter($scope.data.kennels, function(e, i) {
            return i !== index;
        });
    };

    $scope.addTitleRow = function() {
        $scope.data.titles.push(_.clone($scope.empty_title));
    };

    $scope.removeTitleRow = function(index) {
        $scope.data.titles = _.filter($scope.data.titles, function(e, i) {
            return i !== index;
        });
    };

    $scope.openKennelAddPopup = function(index) {
        $rootScope.$broadcast('show_kennel_add_popup', function(new_kennel) {
            var kennel = $scope.data.kennels[index];
            kennel.data = new_kennel;
            kennel.force_open = false;
        });
    };

    //

    $scope.buildAncestor = function() {
        var ancestors_dict = {};
        (function() {
            for (var i = 0; i < ancestors_levels_keys.length; i++) {
                var _key = ancestors_levels_keys[i];
                $scope.$broadcast('widgetshortanimal_get_ancestor', _key, function(data) {
                    ancestors_dict[_key] = data;
                });
            }
        })();
        return ancestors_dict;
    };

    //

    $scope.saveObject = function(success_callback) {
        $scope.data['ancestors'] = $scope.buildAncestor();
        var json_data = angular.toJson($scope.data);

        $scope.loading = true;
        $scope.errors = null;
        $http({
            method: 'POST',
            url: ROUTER.core_ajax_animal_create,
            data: json_data
        })
            .success(function(data) {
                if (data.status === 'success') {
                    if (success_callback !== undefined) {
                        success_callback(data.data);
                    }
                    if ($scope.form_mode === 'full') {
                        location.href = data.urls.core_animals_list;
                    }
                } else {
                    if (data.warnings !== undefined) {
                        if (data.warnings.length > 0) {
                            var _pedigree_numbers_warnings = _.filter(data.warnings, function(item) {
                                return (item.field === 'pedigree_numbers');
                            });
                            if (_pedigree_numbers_warnings.length) {
                                var _html = '' +
                                    '<div>' +
                                    '    <div>Введеные номера родословных похожа на уже существующие! Проверте совпадения:</div>' +
                                    '</div>' +
                                    '<h3></h3>';
                                _.each(_pedigree_numbers_warnings, function(item, n) {
                                    _html += '<div class="row">';
                                    _html += '    <div class="col-sm-4">';
                                    _html += '        <b>' + item.number + '</b>';
                                    _html += '    </div>';
                                    _html += '    <div class="col-sm-8">';

                                    _.each(item.animals, function(item_animal) {
                                        _html += '    <div>';
                                        _html += '        <div><b>' + _.map(item_animal.pedigree_numbers, function(_it) {return _it.number;}).join(', ') + '</b></div>';
                                        _html += '        <div><a href="' + item_animal.absolute_url + '" target="_blank">' + item_animal.text + '</a> (' + item_animal.breed_data.text + ')</div>';
                                        _html += '    </div>';
                                    });

                                    _html += '    </div>';
                                    _html += '</div>';

                                    if (n !== _pedigree_numbers_warnings.length - 1) {
                                        _html += '<hr>';
                                    }
                                });
                                $rootScope.$broadcast('show_popup_animalcreateform_warnings', _html);
                            }
                        }
                    }
                    if (data.errors !== undefined) {
                        $scope.errors = data.errors;
                    }
                }
            });
    };

    $scope.$on('animalformctrl_saveobject', function(e, success_callback) {
        $scope.saveObject(success_callback);
    });

    $scope.$on('animalformctrl_setobject', function(e, data) {
        $scope.data = _prepare_data(data);
    });

    $scope.$on('widgetshortanimal_set_sibling_ancestors', function(e, role, data) {
        $scope.$broadcast('widgetshortanimal_set_ancestor', role, data);
    });
});