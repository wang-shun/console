/**
 * Created by wuyang on 16/8/6.
 */

define(function() {
    var app = function() {
        this.href = location.pathname;
        this._catch = [];
    };

    app.prototype.get = function(url, fun) {
        if (this._catch.length > 0) return false;
        if (!(typeof url === 'string' || url instanceof RegExp)) return false;
        if ((typeof url === 'string' && this.href !== url) || (url instanceof RegExp && !url.test(this.href))) return false;
        if (!(fun instanceof Function)) return false;
        this._catch.push(fun.bind(this));
        this._catch.push(this.end());
        var callback = this._catch.shift();
        callback.call(this);
    };
    app.prototype.next = function() {
        this._catch.shift();
    };
    app.prototype.end = function() {
        return function() {
            return false;
        };
    };
    app.prototype.getUrl = function(){
        if (this.getUrlParam().flag !== undefined && this.getUrlParam().flag == "host") {
            return '/admin/sourceManage/virtualList?host';
        }
        return this.href;
    }
    app.prototype.getUrlParam = function(){
      var str = location.search;
      var json = {};
      if (str!=="") {
        str = str.slice(1);
        var arr = str.split('&');
        for (var i = 0, j = arr.length; i < j; i++) {
          json[arr[i].split('=')[0]] = arr[i].split('=')[1];
        }
      }
      return json;
    }
    return new app();
});


