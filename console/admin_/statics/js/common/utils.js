/**
 * Created by wuyang on 16/8/4.
 */

define(["dataTableOptions"], function(options) {
    var getCookie = function(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return decodeURIComponent(document.cookie.substring(c_start, c_end));
            }
        }
        return "";
    };

    var dateBetween = function(date1, date2) {
        // Convert both dates to milliseconds
        var date1_ms = date1.getTime();
        var date2_ms = date2.getTime();

        // Calculate the difference in milliseconds
        var difference_ms = date2_ms - date1_ms;
        // take out milliseconds
        difference_ms = difference_ms / 1000;
        var seconds = Math.floor(difference_ms % 60);
        difference_ms = difference_ms / 60;
        var minutes = Math.floor(difference_ms % 60);
        difference_ms = difference_ms / 60;
        var hours = Math.floor(difference_ms % 24);
        var days = Math.floor(difference_ms / 24);

        var ret_data = "";
        if (days)
            ret_data += days + "天";
        if (hours)
            ret_data += hours + "小时";
        if (minutes)
            ret_data += minutes + "分钟";
        if (seconds)
            ret_data += seconds + "秒";

        return ret_data;
    };

    var _ajax = function(obj) {
        /* {
            obj.type
            obj.url
            obj.async:true
            obj.data
            obj.succCB
            obj.errCB
            obj.error
            obj.finalCB
            obj.contentType: 'application/json',

         }*/
        $.ajax({
            type: obj.type || "post",
            async: !obj.async,
            cache: false,
            contentType: obj.contentType || 'application/x-www-form-urlencoded; charset=UTF-8',
            url: obj.url,
            data: obj.data || {},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            },
            success: function(data) {
                if (data.ret_code == 0) {
                    if (obj.succCB)
                        obj.succCB(data);
                } else {
                    if (obj.errCB)
                        obj.errCB(data);
                }
                if (obj.finalCB) {
                    obj.finalCB(data);
                }
            },
            error: function(err) {
                if (obj.error) {
                    obj.error(err);
                }
            }
        });
    };

    var succMsg = function(msg) {
        Messenger().post({
            message: msg,
            type: "success",
            showCloseButton: true
        });
    };

    var errMsg = function(msg) {
        Messenger().post({
            message: msg,
            type: "error",
            showCloseButton: true
        });
    };

    var datatable = function(elem, obj, url, dataTableWillReload) {
        var ajaxOption = {
            type: "post",
            async: true,
            cache: false,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                dataTableWillReload && dataTableWillReload();
            }
        };
        if (typeof url === 'string') {
            ajaxOption.url = url;
        } else {
            ajaxOption = $.extend({}, url, ajaxOption);
        }
        var datatabeleJSON = {
            "language": options.DATATABLE_LANGUAGE_OPTION,
            "scrollY": options.DATATABLE_SCROLLY,
            "processing": true,
            "serverSide": true,
            "paging": true,
            "info": false,
            "dom": '<"top"if>rt<"bottom"lp><"clear">',
            "columns": obj.columns,
            "ajax": ajaxOption
        };
        if (obj.order) {
            datatabeleJSON.order = obj.order;
        }
        if (obj.columnDefs) {
            datatabeleJSON.columnDefs = obj.columnDefs;
        }
        return elem.DataTable(datatabeleJSON);
    };

    var tableClick = function(datatable, obj) {
        datatable.off("click", "tr");
        datatable.on("click", "tr", function() {
            if ($(this).hasClass("selected")) {
                $(this).removeClass("selected");
                obj.offCB && obj.offCB($(this));
            } else {
                datatable.find("tr.selected").removeClass("selected");
                $(this).addClass("selected");
                 obj.onCB && obj.onCB($(this));
            }
            obj.callback && obj.callback($(this));
        });
    };

    var selected_column = function(datatable, column) {
        var col = "td:eq(" + column + ")";
        return datatable.$("tr.selected").children(col);
    };

    var refreshDataTable = function(datatable) {
        $(".refresh").on("click", function() {
            datatable.ajax.reload();
        });
    };

    var trendChart = function(elem, labels, chartLabel, dataSet) {
        var data = {
            labels: chartLabel,
            datasets: [
                {
                    label: labels,
                    fillColor: "rgba(18,164,244,0.2)",
                    strokeColor: "rgba(18,164,244,1)",
                    pointColor: "rgba(18,164,244,1)",
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: dataSet
                }
            ]
        };
        var ctx = elem.get(0).getContext("2d");
        var myNewChart = new Chart(ctx).Line(data, {bezierCurve: false});
        return myNewChart;
    };

    var owner = $("#owner");
    // 获取用户信息
    _ajax({
        url: '/user/info',
        async: true,
        succCB: function(res) {
            owner.val(res.ret_set[0].user.username);
        }
    });
// 获取url中的参数
    var getUrlParams = function() {
        var str = location.href.split('?');
        var json = {};
        if (str[1]) {
            var arr = str[1].split('&');
            for (var i = 0, j = arr.length; i < j; i++) {
                json[arr[i].split('=')[0]] = arr[i].split('=')[1];
            }
        }
        return json;
    };

// 转化相对时间
    var numToDate = function(difference_ms) {
        if (typeof ~~difference_ms != 'number') {
            return 0;
        }
        difference_ms = ~~difference_ms / 1000;
        var seconds = Math.floor(difference_ms % 60);
        difference_ms = difference_ms / 60;
        var minutes = Math.floor(difference_ms % 60);
        difference_ms = difference_ms / 60;
        var hours = Math.floor(difference_ms % 24);
        var days = Math.floor(difference_ms / 24);

        var ret_data = "";
        if (days)
            ret_data += days + "天";
        if (hours)
            ret_data += hours + "小时";
        if (minutes)
            ret_data += minutes + "分钟";
        if (seconds)
            ret_data += seconds + "秒";

        return ret_data;

    };


    var toMemory = function(num, type, toType, fixed) {
        var type = type || 'byte',
            toType = toType || 'GB',
            num = num || 0,
            mapData = ['byte', 'KB', 'MB', 'GB'],
            fixed = (fixed === undefined || fixed === null) ? 3 : fixed;
        return (Math.pow(1024, (mapData.indexOf(type) - mapData.indexOf(toType))) * num).toFixed(fixed) + toType;
    };

    var toAutoMemory = function(size, type) {
        // 默认byte
        if (!type) {
            var g = Math.floor(size / (1024 * 1024 * 1024));
            var m = Math.floor(size / (1024 * 1024));
            var k = Math.floor(size / 1024);
            if (g > 0) {
                return (size / (1024 * 1024 * 1024)).toFixed(3) + 'G';
            } else if (m > 0) {
                return (size / (1024 * 1024)).toFixed(3) + 'M';
            } else if (k > 0) {
                return (size / (1024)).toFixed(3) + 'K';
            } else {
                return size + 'B';
            }
        }
    };

    // 将时间戳转化为指定格式
    var toDate = function(data, type) {
        // type yyyy MM dd hh mm ss
        var oDate = new Date(data);
        if (oDate instanceof Date) {
            var type = type || 'hh:mm:ss';
            var oDateJson = {
                'yyyy': oDate.getFullYear().toString(),
                'yy': oDate.getFullYear().toString().substring(2),
                'MM': toZero(oDate.getMonth() + 1),
                'dd': toZero(oDate.getDay()),
                'hh': toZero(oDate.getHours()),
                'mm': toZero(oDate.getMinutes()),
                'ss': toZero(oDate.getSeconds())
            };
            var arrtype = type.match(/(\w+|[:\\\/_\s-])/g);
            var newarr = arrtype.map(function(y) {
                return (oDateJson[y] !== undefined) ? oDateJson[y] : y;
            });
            return newarr.join('');
        }

        // 返回补0得函数
        function toZero(str, num) {
            var num = num || 2;
            return (Number(0).toFixed(num).substring(2) + str).slice(-num);
        }
    };

    var arrToString = function(arr, json) {
        return arr.map(function(v) {
            return json[v];
        });
    };


    var usageChart = function(usageChartArr) {
      if (!usageChartArr || !(usageChartArr instanceof Array) || usageChartArr.length === 0) {
        return false;
      }
      var userColor = '#00a2f7';
      var totalColor = '#f5f5f5';

      var $box = $('<div class="usage-box"></div>');

      function init() {
        $box.append(getUsageTitle());
        $box.append(getUsageLine());
        setTimeout(function() {
          $(".usage-line").find('.front').css({"transform": "scale(1,1)"});
        });
        return $box;

      }
      function getUsageTitle() {
        var $boxTitle = $('<div class="usage-title"></div>');
        $boxTitle.html("<ul><li><span style=background:" + userColor + "></span><p>使用量</p></li><li><span style=background:" + totalColor + "></span><p>剩余量</p></li></ul>");
        return $boxTitle;

      }
      function getUsageLine() {
        var $boxLine = $('<ul class="usage-line"></ul>');

        for (var i = 0; i < usageChartArr.length; i++) {
          var usageText = usageChartArr[i].usageText;
          var usageData = usageChartArr[i].usageData;
          var isHighlight = usageChartArr[i].isHighlight;
          var $usageSingleline = $("<li></li>");
          $usageSingleline.append("<label>" + usageText + "</label>");
            if(isHighlight){
                $usageSingleline.append(usageBar(usageData));
            }
          $boxLine.append($usageSingleline);
        }
        function usageBar(usageData) {
            function getScale(scale){
                return scale>100 ? 100 : scale;
            }
          var $usageBar = $("<div><p class='front' style='background:" + userColor + "; width:" + getScale(100 * usageData.used / usageData.total) + "%'>" + usageData.used + "</p><p class='back' style='background:" + totalColor + "'>" + usageData.total + "</p></div>");
          return $usageBar;
        }

        return $boxLine;

      }

      return init();
    };

    var num_to_max = function(num, max) {
        var max = max || 255;
        if (!isNaN(num)) {
            if (num > max) {
                return max;
            } else {
                return num;
            }
        }
        return 0;
    };

    var num_to_min = function(num, min) {
        var min = min || 0;
        if (!isNaN(num)) {
            if (num < min) {
                return min;
            } else {
                return num;
            }
        }
        return 0;
    };
    var generateMD5 = function(string) {
        var hex_chr = "0123456789abcdef";
        function rhex(num) {
            str = "";
            for (j = 0; j <= 3; j++)
                str += hex_chr.charAt((num >> (j * 8 + 4)) & 0x0F) +
                  hex_chr.charAt((num >> (j * 8)) & 0x0F);
            return str;
        }
        function str2blks_MD5(str) {
            nblk = ((str.length + 8) >> 6) + 1;
            blks = new Array(nblk * 16);
            for (i = 0; i < nblk * 16; i++) blks[i] = 0;
            for (i = 0; i < str.length; i++)
                blks[i >> 2] |= str.charCodeAt(i) << ((i % 4) * 8);
            blks[i >> 2] |= 0x80 << ((i % 4) * 8);
            blks[nblk * 16 - 2] = str.length * 8;
            return blks;
        }
        function add(x, y) {
            var lsw = (x & 0xFFFF) + (y & 0xFFFF);
            var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
            return (msw << 16) | (lsw & 0xFFFF);
        }
        function rol(num, cnt) {
            return (num << cnt) | (num >>> (32 - cnt));
        }
        function cmn(q, a, b, x, s, t) {
            return add(rol(add(add(a, q), add(x, t)), s), b);
        }
        function ff(a, b, c, d, x, s, t) {
            return cmn((b & c) | ((~b) & d), a, b, x, s, t);
        }
        function gg(a, b, c, d, x, s, t) {
            return cmn((b & d) | (c & (~d)), a, b, x, s, t);
        }
        function hh(a, b, c, d, x, s, t) {
            return cmn(b ^ c ^ d, a, b, x, s, t);
        }
        function ii(a, b, c, d, x, s, t) {
            return cmn(c ^ (b | (~d)), a, b, x, s, t);
        }
        function MD5(str) {
            x = str2blks_MD5(str);
            var a = 1732584193;
            var b = -271733879;
            var c = -1732584194;
            var d = 271733878;
            for (i = 0; i < x.length; i += 16) {
                var olda = a;
                var oldb = b;
                var oldc = c;
                var oldd = d;
                a = ff(a, b, c, d, x[i + 0], 7, -680876936);
                d = ff(d, a, b, c, x[i + 1], 12, -389564586);
                c = ff(c, d, a, b, x[i + 2], 17, 606105819);
                b = ff(b, c, d, a, x[i + 3], 22, -1044525330);
                a = ff(a, b, c, d, x[i + 4], 7, -176418897);
                d = ff(d, a, b, c, x[i + 5], 12, 1200080426);
                c = ff(c, d, a, b, x[i + 6], 17, -1473231341);
                b = ff(b, c, d, a, x[i + 7], 22, -45705983);
                a = ff(a, b, c, d, x[i + 8], 7, 1770035416);
                d = ff(d, a, b, c, x[i + 9], 12, -1958414417);
                c = ff(c, d, a, b, x[i + 10], 17, -42063);
                b = ff(b, c, d, a, x[i + 11], 22, -1990404162);
                a = ff(a, b, c, d, x[i + 12], 7, 1804603682);
                d = ff(d, a, b, c, x[i + 13], 12, -40341101);
                c = ff(c, d, a, b, x[i + 14], 17, -1502002290);
                b = ff(b, c, d, a, x[i + 15], 22, 1236535329);
                a = gg(a, b, c, d, x[i + 1], 5, -165796510);
                d = gg(d, a, b, c, x[i + 6], 9, -1069501632);
                c = gg(c, d, a, b, x[i + 11], 14, 643717713);
                b = gg(b, c, d, a, x[i + 0], 20, -373897302);
                a = gg(a, b, c, d, x[i + 5], 5, -701558691);
                d = gg(d, a, b, c, x[i + 10], 9, 38016083);
                c = gg(c, d, a, b, x[i + 15], 14, -660478335);
                b = gg(b, c, d, a, x[i + 4], 20, -405537848);
                a = gg(a, b, c, d, x[i + 9], 5, 568446438);
                d = gg(d, a, b, c, x[i + 14], 9, -1019803690);
                c = gg(c, d, a, b, x[i + 3], 14, -187363961);
                b = gg(b, c, d, a, x[i + 8], 20, 1163531501);
                a = gg(a, b, c, d, x[i + 13], 5, -1444681467);
                d = gg(d, a, b, c, x[i + 2], 9, -51403784);
                c = gg(c, d, a, b, x[i + 7], 14, 1735328473);
                b = gg(b, c, d, a, x[i + 12], 20, -1926607734);
                a = hh(a, b, c, d, x[i + 5], 4, -378558);
                d = hh(d, a, b, c, x[i + 8], 11, -2022574463);
                c = hh(c, d, a, b, x[i + 11], 16, 1839030562);
                b = hh(b, c, d, a, x[i + 14], 23, -35309556);
                a = hh(a, b, c, d, x[i + 1], 4, -1530992060);
                d = hh(d, a, b, c, x[i + 4], 11, 1272893353);
                c = hh(c, d, a, b, x[i + 7], 16, -155497632);
                b = hh(b, c, d, a, x[i + 10], 23, -1094730640);
                a = hh(a, b, c, d, x[i + 13], 4, 681279174);
                d = hh(d, a, b, c, x[i + 0], 11, -358537222);
                c = hh(c, d, a, b, x[i + 3], 16, -722521979);
                b = hh(b, c, d, a, x[i + 6], 23, 76029189);
                a = hh(a, b, c, d, x[i + 9], 4, -640364487);
                d = hh(d, a, b, c, x[i + 12], 11, -421815835);
                c = hh(c, d, a, b, x[i + 15], 16, 530742520);
                b = hh(b, c, d, a, x[i + 2], 23, -995338651);
                a = ii(a, b, c, d, x[i + 0], 6, -198630844);
                d = ii(d, a, b, c, x[i + 7], 10, 1126891415);
                c = ii(c, d, a, b, x[i + 14], 15, -1416354905);
                b = ii(b, c, d, a, x[i + 5], 21, -57434055);
                a = ii(a, b, c, d, x[i + 12], 6, 1700485571);
                d = ii(d, a, b, c, x[i + 3], 10, -1894986606);
                c = ii(c, d, a, b, x[i + 10], 15, -1051523);
                b = ii(b, c, d, a, x[i + 1], 21, -2054922799);
                a = ii(a, b, c, d, x[i + 8], 6, 1873313359);
                d = ii(d, a, b, c, x[i + 15], 10, -30611744);
                c = ii(c, d, a, b, x[i + 6], 15, -1560198380);
                b = ii(b, c, d, a, x[i + 13], 21, 1309151649);
                a = ii(a, b, c, d, x[i + 4], 6, -145523070);
                d = ii(d, a, b, c, x[i + 11], 10, -1120210379);
                c = ii(c, d, a, b, x[i + 2], 15, 718787259);
                b = ii(b, c, d, a, x[i + 9], 21, -343485551);
                a = add(a, olda);
                b = add(b, oldb);
                c = add(c, oldc);
                d = add(d, oldd);
            }
            return rhex(a) + rhex(b) + rhex(c) + rhex(d);
        }
        return MD5(string);
    };
    return {
        getCookie: getCookie,
        dateBetween: dateBetween,
        _ajax: _ajax,
        succMsg: succMsg,
        errMsg: errMsg,
        datatable: datatable,
        tableClick: tableClick,
        selected_column: selected_column,
        refreshDataTable: refreshDataTable,
        trendChart: trendChart,
        numToDate: numToDate,
        toMemory: toMemory,
        toDate: toDate,
        arrToString: arrToString,
        usageChart: usageChart,
        getUrlParams: getUrlParams,
        num_to_max: num_to_max,
        num_to_min: num_to_min,
        generateMD5: generateMD5,
        toAutoMemory: toAutoMemory,
    };

});
