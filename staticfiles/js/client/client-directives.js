hund.directive('ngWidgetFullAnimalForm', function() {
    return {
        scope: {
            'data': '=ngBindData'
        },
        templateUrl: 'tpl_ngwidgetfullanimalform',
        controller: 'AnimalFormCtrl',
        link: function($scope, $element, attrs) {
            $scope.form_mode = 'full';
        }
    }
});

hund.directive('ngWidgetShortAnimalForm', function() {
    return {
        scope: {
            'data': '=ngBindData',
            'target_data': '=ngBindTargetData',
            'role': '=ngBindRole'
        },
        templateUrl: 'tpl_ngwidgetshortanimalform',
        controller: 'AnimalFormCtrl',
        link: function($scope, $element, attrs) {
            $scope.form_mode = 'short';
        }
    }
});

hund.directive('ngWidgetShortAnimal', function() {
    return {
        templateUrl: 'tpl_ngwidgetshortanimal',
        scope: {
            'target_data': '=ngBindTargetData',
            'role': '=ngBindRole'
        },
        controller: function($scope, $timeout) {
            $scope.widget_state = 'open';
            $scope.popup_open = false;
            $scope.data = null;

            $scope.setData = function(data) {
                $scope.data = data;

                if (data && data.ancestors) {
                    var _keys = _.keys(data.ancestors);

                    var _parent_keys = _.filter(_.map(_keys, function(_key) {
                        return $scope.role + _key;
                    }), function(item) {
                        return item.length <= 4;
                    });

                    (function() {
                        for (var i = 0; i < _parent_keys.length; i++) {
                            $scope.$emit('widgetshortanimal_set_sibling_ancestors', _parent_keys[i], null);
                        }
                    })();

                    var _valid_parents = _.filter(_.map(_parent_keys, function(_key) {
                        var _real_key = _key.slice($scope.role.length);
                        var _data = data.ancestors[_real_key];
                        return [_key, _data];
                    }), function(item) {
                        return !!item[1];
                    });

                    (function() {
                        for (var i = 0; i < _valid_parents.length; i++) {
                            $scope.$emit('widgetshortanimal_set_sibling_ancestors', _valid_parents[i][0], _valid_parents[i][1]);
                        }
                    })();
                }
            };

            $scope.$watch('data', function(data) {
                if (data !== null) {
                    $scope.widget_state = 'close';
                } else {
                    $scope.widget_state = 'open';
                }
            });

            $scope.showPopup = function() {
                $scope.popup_open = true;
            };

            $scope.editItem = function() {
                $scope.$broadcast('animalformctrl_setobject', $scope.data);
                $scope.showPopup();
            };

            $scope.removeItem = function() {
                if (confirm('Вы уверены?')) {
                    $scope.setData(null);
                }
            };

            if ($scope.target_data.ancestors) {
                $scope.setData($scope.target_data.ancestors[$scope.role]);
            }

            $scope.$on('widgetshortanimal_get_ancestor', function(e, role, callback) {
                if ($scope.role === role) {
                    callback($scope.data);
                }
            });

            $scope.$on('widgetshortanimal_set_ancestor', function(e, role, data) {
                if ($scope.role === role) {
                    $scope.setData(data);
                }
            })
        },
        link: function($scope, $element, attrs) {

        }
    }
});


hund.directive('ngDatepicker', function() {
    return {
        link: function($scope, $element, attrs) {
            $element.datepicker(datepicker_settings);
        }
    }
});


hund.directive('ngBreedAutocomplete', function() {
    return {
        scope: {
            data: '=ngBindData'
        },
        link: function($scope, $element, attrs) {
            var selct2_config = {
                ajax: {
                    url: ROUTER.core_ajax_breed_search,
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        return {
                            q: params.term
                        };
                    },
                    processResults: function(data) {
                        return {
                            results: data
                        };
                    }
                }
            };
            setTimeout(function() {
                $element.select2(selct2_config);
                $element.on("select2:select", function(e) {
                    $scope.data = e.params.data;
                    $scope.$apply();
                    setTimeout(function() {
                        $element.select2(selct2_config);
                    }, 100);
                });
            }, 100);
        }
    }
});

hund.directive('ngAnimalAutocomplete', function() {
    return {
        scope: {
            'setData': '=ngBindSetData',
            'target_data': '=ngBindTargetData',
            'role': '=ngBindRole'
        },
        link: function($scope, $element, attrs) {
            $scope.gender = '';

            if ($scope.role) {
                $scope.gender = $scope.role[$scope.role.length - 1];
            }

            var selct2_config = {
                placeholder: role_to_name($scope.role),
                ajax: {
                    url: ROUTER.core_ajax_animal_search,
                    dataType: 'json',
                    delay: 250,
                    data: function(params) {
                        //var _breed = '';
                        //if ($scope.target_data && $scope.target_data.breed) {
                        //    _breed = $scope.target_data.breed;
                        //}
                        return {
                            q: params.term,
                            gender: $scope.gender
                            //breed: _breed
                        };
                    },
                    processResults: function(data) {
                        return {
                            results: data
                        };
                    }
                },
                templateResult: function(item) {
                    if (item.pk === undefined) {
                        return item.text;
                    } else {
                        var pedigree_numbers = _.map(item.pedigree_numbers, function(it) {
                            return it.number;
                        }).join(', ');
                        return $('' +
                        '<div class="shortanimal__autocompliterow">' +
                        '    <div class="shortanimal__autocompliterow__name">' + (item.name_ru || item.name_en) + '</div>' +
                        '    <div class="shortanimal__autocompliterow__number">' + pedigree_numbers + '</div>' +
                        '</div>');
                    }
                }
            };
            setTimeout(function() {
                $element.select2(selct2_config);
                $element.on('select2:select', function(e) {
                    if ($scope.setData) {
                        $scope.setData(e.params.data);
                        $scope.$apply();
                    }
                });
            }, 100);
        }
    };
});

hund.directive('ngAnimalPopup', function() {
    return {
        templateUrl: 'tpl_nganimalpopup',
        scope: {
            'setData': '=ngBindSetData',
            'target_data': '=ngBindTargetData',
            'popup_open': '=ngBindPopupOpen',
            'role': '=ngBindRole'
        },
        controller: function($scope) {
            $scope.closePopup = function() {
                $scope.popup_open = false;
            };

            $scope.popupSave = function() {
                $scope.$broadcast('animalformctrl_saveobject', function(data) {
                    $scope.setData(data);
                    $scope.closePopup();
                });
            };
        },
        link: function($scope, $element, attrs) {
            var $animalpopup = $element.find('.animalpopup');
            $animalpopup.appendTo($('body'));
        }
    };
});


hund.directive('ngDocpreviewControls', function() {
    return {
        templateUrl: 'tpl_ngdocpreviewcontrols',
        scope: {
            'models_data': '=ngBindModelsData'
        },
        controller: function($scope, $rootScope) {
            $scope.show_page = 'models';
            $scope.model = null;

            $scope.selectModel = function(model, options) {
                if (options === undefined) {
                    options = {};
                }

                $scope.show_page = 'fields';
                $scope.model = model;

                if (options.nobroadcast !== true) {
                    $rootScope.$broadcast('ngdocpreviewcontrols_change_model', $scope.model);
                }
            };

            $scope.backToStart = function() {
                if (confirm('Вы действительно хотите вернутся к выбору моделей? Все расставленные поля будут удалены!')) {
                    $scope.show_page = 'models';
                    $scope.model = null;
                    $rootScope.$broadcast('ngdocpreviewcontrols_change_model', $scope.model);
                    $rootScope.$broadcast('ngdocpreviewcontrols_clear_items');
                }
            };
        },
        link: function($scope, $element, attrs) {
            $scope.$settings = $('[name=settings]');

            var _settings = $scope.$settings.val();

            if (_settings) {
                $scope.settings = JSON.parse(_settings);
                if ($scope.settings && $scope.settings.model) {

                    var _model = null;

                    if ($scope.models_data) {
                        (function() {
                            var _model_data = null;
                            for (var i = 0; i < $scope.models_data.length; i++) {
                                _model_data = $scope.models_data[i];
                                if (_model_data.app_label === $scope.settings.model.app_label) {
                                    if (_model_data.model_name === $scope.settings.model.model_name) {
                                        _model = _model_data;
                                        break;
                                    }
                                }
                            }
                        })();
                    }

                    if (_model) {
                        $scope.selectModel(_model, {nobroadcast: true});
                    }
                }
            }
        }
    };
});


hund.directive('ngDocpreviewControlsPanel', function() {
    return {
        link: function($scope, $element, attrs) {
            $element.draggable({
                handle: '.docpreview__controls__panel__header'
            })
        }
    }
});


hund.directive('ngDocpreviewControlsPanelDragField', function() {
    return {
        scope: {
            field: '=ngBindField',
            model: '=ngBindModel'
        },
        link: function($scope, $element, attrs) {
            $element.draggable({
                cursor: "move",
                helper: function(event) {
                    var $helper = $('<div class="docpreview__controls__panel__draghelper">' + $scope.field[1] + '</div>');
                    return $helper;
                }
            })
        }
    }
});


hund.directive('ngDocpreviewDestLayer', function() {
    return {
        templateUrl: 'tpl_ngdocpreviewdestlayer',
        scope: {
            bind_mode: '=ngBindMode'
        },
        controller: function($scope) {
            $scope.items = [];
            $scope.model = null;

            $scope.settings = {
                model: null,
                layer: null,
                items: []
            }
        },
        link: function($scope, $element, attrs) {
            $scope.$settings = $('[name=settings]');

            var _settings = $scope.$settings.val();

            if (_settings) {
                $scope.settings = JSON.parse(_settings);
                $scope.items = $scope.settings.items;
                $scope.model = $scope.settings.model;
            }

            $scope.$on('ngdocpreviewcontrols_change_model', function(e, model) {
                $scope.model = model;
            });

            $scope.$on('ngdocpreviewlayeritem_remove_item', function(e, item) {
                $scope.items = _.filter($scope.items, function(it) {
                    return it.index !== item.index;
                });
            });

            $scope.$on('ngdocpreviewcontrols_clear_items', function(e) {
                $scope.items = [];
            });

            $scope.$watch('items', function(items) {
                $scope.settings.items = items;
                $scope.settings.model = $scope.model;
            }, true);

            $scope.$watch('model', function(model) {
                $scope.settings.items = $scope.items;
                $scope.settings.model = model;
            });

            $scope.$watch('settings', function(settings) {
                $scope.$settings.val(JSON.stringify(settings));
            }, true);

            $scope.settings.layer = {
                width: $element.width(),
                height: $element.height()
            };

            $element.droppable({
                accept: '.docpreview__controls__panel .docpreview__controls__panel__body__row_field',
                drop: function(event, ui) {
                    var model_app_label = ui.draggable.data('modelAppLabel');
                    var model_name = ui.draggable.data('modelName');
                    var field_name = ui.draggable.data('fieldName');
                    var field_label = ui.draggable.data('fieldLabel');

                    var _position = $element.offset();

                    var _pos_x = (event.pageX - event.offsetX) - _position.left;
                    var _pos_y = (event.pageY - event.offsetY) - _position.top;

                    var _max_index = 0;

                    if ($scope.items.length > 0) {
                        _max_index = Math.max.apply(undefined, _.map($scope.items, function(item) {
                            return item.index;
                        }));
                    }

                    $scope.items.push({
                        model: {
                            app_label: model_app_label,
                            name: model_name
                        },
                        field: {
                            name: field_name,
                            label: field_label
                        },
                        left: _pos_x,
                        top: _pos_y,
                        width: ui.helper.width(),
                        height: ui.helper.outerHeight(),
                        index: _max_index + 1
                    });

                    $scope.$apply();
                }
            });
        }
    }
});

hund.directive('ngDocpreviewLayerItem', function() {
    return {
        templateUrl: 'tpl_ngdocpreviewlayeritem',
        scope: {
            bind_item: '=ngBindItem',
            bind_mode: '=ngBindMode'
        },
        controller: function($scope) {
            $scope.panel_show = false;

            $scope.showPanel = function() {
                $scope.panel_show = true;
            };

            $scope.hidePanel = function() {
                $scope.panel_show = false;
            };

            $scope.removeItem = function() {
                if (confirm('Вы действительно хотите удалит поле "' + $scope.bind_item.field.label + '"')) {
                    $scope.$emit('ngdocpreviewlayeritem_remove_item', $scope.bind_item);
                }
            };
        },
        link: function($scope, $element, attrs) {
            $scope.$element = $element;
            $scope.$layer = $element.parents('.docpreview__layer');

            if ($scope.bind_mode === 'default') {
                $scope.$element.draggable({
                    cursor: 'move',
                    stop: function(event, ui) {
                        var _element_position = $scope.$element.offset();
                        var _layer_position = $scope.$layer.offset();

                        var _pos_x = _element_position.left - _layer_position.left;
                        var _pos_y = _element_position.top - _layer_position.top;

                        $scope.bind_item.left = _pos_x;
                        $scope.bind_item.top = _pos_y;
                        $scope.$apply();
                    }
                });

                $scope.$element.resizable({
                    handles: 'n, e, s, w',
                    stop: function(event, ui) {
                        $scope.bind_item.width = $scope.$element.outerWidth();
                        $scope.bind_item.height = $scope.$element.outerHeight();
                        $scope.$apply();
                    }
                });

                $scope.$element.on('dblclick', function() {
                    if ($scope.panel_show) {
                        $scope.hidePanel();
                    } else {
                        $scope.showPanel();
                    }
                    $scope.$apply();
                });
            }

            $scope.$watch('bind_item', function(bind_item) {
                $scope.$element.css({
                    top: bind_item.top,
                    left: bind_item.left,
                    width: bind_item.width,
                    lineHeight: bind_item.height + 'px',
                    height: bind_item.height
                })
            });
        }
    }
});


hund.directive('ngCertificateDiapason', function() {
    return {
        controller: function($scope) {
            $scope.diapasonCheck = function(start, end) {
                if (Number.isInteger(start) && Number.isInteger(end)) {
                    if (start < 1) {
                        alert('Неверные значения интервала');
                    } else {
                        if (start > end) {
                            alert('Начало интервала должно быть меньше его конца');
                        } else {
                            return true;
                        }
                    }
                } else {
                    alert('Неверные значения интервала');
                }
                return false;
            };

            $scope.diapasonEnumerate = function(start, end) {
                start = parseInt(start, 10);
                end = parseInt(end, 10);

                var _do_enumerate = function() {
                    var _exist_cnt = (end - start) + 1;
                    var _nead_cnt = $scope.$cert_inputs.length;

                    $scope.$cert_inputs.val('');
                    _.each($scope.$cert_inputs, function(ci) {
                        $(ci).parents('tr').removeClass('danger');
                    });

                    (function() {
                        for (var i = 0; i < _exist_cnt; i++) {
                            (function() {
                                if (i < _nead_cnt) {
                                    var $ci = $scope.$cert_inputs.eq(i);
                                    $ci.val(start + i);
                                }
                            })();
                        }
                    })();

                    if (_nead_cnt > _exist_cnt) {
                        (function() {
                            for (var i = 0; i < (_nead_cnt - _exist_cnt); i++) {
                                (function() {
                                    var $ci = $scope.$cert_inputs.eq(_exist_cnt + i);
                                    var $tr = $ci.parents('tr');
                                    $tr.addClass('danger');
                                })();
                            }
                        })();
                    }

                };

                var _check_step_1 = function() {
                    var _exist_cnt = (end - start) + 1;
                    var _nead_cnt = $scope.$cert_inputs.length;

                    if (_nead_cnt > _exist_cnt) {
                        if (confirm('Недостаточно номеров диапазона. Нехватает ' + (_nead_cnt - _exist_cnt))) {
                            _do_enumerate();
                        }
                    } else {
                        _do_enumerate();
                    }
                };

                var _valid = $scope.diapasonCheck(start, end);

                if (_valid) {
                    var _cert_vals = _.map($scope.$cert_inputs, function(ci) {
                        return $.trim($(ci).val());
                    });

                    var _certs_empty = _.filter(_cert_vals, function(val) {
                        return val !== '';
                    }).length === 0;

                    if (_certs_empty) {
                        _check_step_1();
                    } else {
                        if (confirm('Номера сертификатов уже указаны. Заменить их новыми?')) {
                            _check_step_1();
                        }
                    }
                }
            };
        },
        link: function($scope, $element, attrs) {
            $scope.$diapason_start = $element.find('input[name=diapason_start]');
            $scope.$diapason_end = $element.find('input[name=diapason_end]');
            $scope.$diapason_run = $element.find('.diapason-run');
            $scope.$cert_inputs = $element.find('.member-cert');

            $scope.$diapason_run.on('click', function() {
                var _start = $scope.$diapason_start.val();
                var _end = $scope.$diapason_end.val();

                $scope.diapasonEnumerate(_start, _end);
            });
        }
    };
});


hund.directive('ngPopupAnimalCreateFormWarnings', function() {
    return {
        templateUrl: 'popup_animalcreateform_warnings',
        controller: function($scope) {
            $scope.$on('show_popup_animalcreateform_warnings', function(e, html) {
                $scope.$modal.find('.modal-body').html(html);
                $scope.$modal.modal();
            });
        },
        link: function($scope, $element, attrs) {
            $scope.$modal = $element.find('.modal');
        }
    }
});