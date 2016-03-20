var translit = function(str, typ) {
    var func = function(typ) {
        var abs = Math.abs(typ);
        if (typ === abs) {
            str = str.replace(/(\u0456(?=.[^\u0430\u0435\u0438\u043E\u0443\u044A\s]+))/ig, "1`");
            return [
                function(col, row) {
                    var chr;
                    if (chr = col[0] || col[abs]) {
                        trantab[row] = chr;
                        regarr.push(row);
                    }
                },
                function(str) {
                    return str.replace(/i``/ig, "i`").
                        replace(/((c)z)(?=[ieyj])/ig, "2");// "cz" в символ "c"
                }];
        } else {
            str = str.replace(/(c)(?=[ieyj])/ig, "1z");
            return [
                function(col, row) {
                    var chr;
                    if (chr = col[0] || col[abs]) {
                        trantab[chr] = row;
                        regarr.push(chr);
                    }
                },

                function(str) {
                    return str;
                }];
        }
    }(typ);
    var iso9 = {
        "\u0449": ["", "\u015D", "", "sth", "", "shh", "shh"],
        "\u044F": ["", "\u00E2", "ya", "ya", "", "ya", "ya"],
        "\u0454": ["", "\u00EA", "", "", "", "", "ye"],
        "\u0463": ["", "\u011B", "", "ye", "", "ye", ""],
        "\u0456": ["", "\u00EC", "i", "i`", "", "i`", "i"],
        "\u0457": ["", "\u00EF", "", "", "", "", "yi"],
        "\u0451": ["", "\u00EB", "yo", "", "", "yo", ""],
        "\u044E": ["", "\u00FB", "yu", "yu", "", "yu", "yu"],
        "\u0436": ["zh", "\u017E"],
        "\u0447": ["ch", "\u010D"],
        "\u0448": ["sh", "\u0161"],
        "\u0473": ["", "f\u0300", "", "fh", "", "fh", ""],
        "\u045F": ["", "d\u0302", "", "", "dh", "", ""],
        "\u0491": ["", "g\u0300", "", "", "", "", "g`"],
        "\u0453": ["", "\u01F5", "", "", "g`", "", ""],
        "\u0455": ["", "\u1E91", "", "", "z`", "", ""],
        "\u045C": ["", "\u1E31", "", "", "k`", "", ""],
        "\u0459": ["", "l\u0302", "", "", "l`", "", ""],
        "\u045A": ["", "n\u0302", "", "", "n`", "", ""],
        "\u044D": ["", "\u00E8", "e`", "", "", "e`", ""],
        "\u044A": ["", "\u02BA", "", "a`", "", "``", ""],
        "\u044B": ["", "y", "y`", "", "", "y`", ""],
        "\u045E": ["", "\u01D4", "u`", "", "", "", ""],
        "\u046B": ["", "\u01CE", "", "o`", "", "", ""],
        "\u0475": ["", "\u1EF3", "", "yh", "", "yh", ""],
        "\u0446": ["cz", "c"],
        "\u0430": ["a"],
        "\u0431": ["b"],
        "\u0432": ["v"],
        "\u0433": ["g"],
        "\u0434": ["d"],
        "\u0435": ["e"],
        "\u0437": ["z"],
        "\u0438": ["", "i", "", "i", "i", "i", "y`"],
        "\u0439": ["", "j", "j", "j", "", "j", "j"],
        "\u043A": ["k"],
        "\u043B": ["l"],
        "\u043C": ["m"],
        "\u043D": ["n"],
        "\u043E": ["o"],
        "\u043F": ["p"],
        "\u0440": ["r"],
        "\u0441": ["s"],
        "\u0442": ["t"],
        "\u0443": ["u"],
        "\u0444": ["f"],
        "\u0445": ["x", "h"],
        "\u044C": ["", "\u02B9", "`", "`", "", "`", "`"],
        "\u0458": ["", "j\u030C", "", "", "j", "", ""],
        "\u2019": ["'", "\u02BC"],
        "\u2116": ["#"]
    }, regarr = [], trantab = {};
    for (var row in iso9) {
        func[0](iso9[row], row);
    }
    return func[1](
        str.replace(
            new RegExp(regarr.join("|"), "gi"),
            function(R) {
                if (
                    R.toLowerCase() === R) {
                    return trantab[R];
                } else {
                    return trantab[R.toLowerCase()].toUpperCase();
                }
            }));
};

var ancestors_levels_keys = [
    'm',
    'f',
    'mm',
    'mf',
    'fm',
    'ff',
    'mmm',
    'mmf',
    'mfm',
    'mff',
    'fmm',
    'fmf',
    'ffm',
    'fff',
    'mmmm',
    'mmmf',
    'mmfm',
    'mmff',
    'mfmm',
    'mfmf',
    'mffm',
    'mfff',
    'fmmm',
    'fmmf',
    'fmfm',
    'fmff',
    'ffmm',
    'ffmf',
    'fffm',
    'ffff'
];


var role_to_name = function(role) {
    var value = '';
    if (role) {
        var gender = role[role.length - 1];
        var level = role.length;
        if (gender === 'm') {
            value = {1: 'Отец', 2: 'Дед', 3: 'Прадед', 4: 'Прапрадед'}[level];
        }
        if (gender === 'f') {
            value = {1: 'Мать', 2: 'Бабка', 3: 'Прабабка', 4: 'Прапрабабка'}[level];
        }
    }
    return value;
};