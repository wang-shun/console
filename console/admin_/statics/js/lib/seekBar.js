define(function () {
    // 拖动条控件
    function SeekBar(obj, config) {
        this.obj = obj;
        this.init(config);
    }

    SeekBar.prototype.init = function (config) {
        this.initConfig(config);
        this.initHTML();
        this.initElement();
        this.drage();
        this.bindEvent();

        this.setInputValue(this.minValue);
        this.oTip.find('span').html(this.tip);
        this.oUnit.html(this.unit);
    };
    SeekBar.prototype.initConfig = function (config) {
        this.maxValue = config.maxValue;
        this.minValue = config.minValue;
        this.step = config.step;
        this.unit = config.unit;
        this.tip = config.tip || this.minValue + this.unit + "-" + this.maxValue + this.unit + ",步长为" + this.step + this.unit;
    };
    SeekBar.prototype.initHTML = function () {
        var str = '\
            <div class="seekBar-box-bar">\
                <div class="seekBar-box-bg"></div>\
                <div class="seekBar-box-block"></div>\
            </div>\
            <div class="seekBar-box-text">\
                <input type="text" class="seekBar-box-input">\
                <label class="seekBar-box-unit"></label>\
                <div class="seekBar-box-btns">\
                    <a href="javascript:;" class="seekBar-box-up"></a>\
                    <a href="javascript:;" class="seekBar-box-down"></a>\
                </div>\
            </div>\
            <div class="seekBar-box-tip">\
                <span></span>\
            </div>\
       ';
        this.obj.html(str);
    };
    SeekBar.prototype.initElement = function () {
        this.oBar = this.obj.find(".seekBar-box-bar");
        this.oBlock = this.obj.find(".seekBar-box-block");
        this.oBg = this.obj.find(".seekBar-box-bg");
        this.oInput = this.obj.find(".seekBar-box-input");
        this.oUp = this.obj.find(".seekBar-box-up");
        this.oDown = this.obj.find(".seekBar-box-down");
        this.oTip = this.obj.find(".seekBar-box-tip");
        this.oUnit = this.obj.find(".seekBar-box-unit");

        this.oBarWidth = this.oBar.width();
        this.oBlockWidth = this.oBlock.width();
    };
    SeekBar.prototype.setBarValue = function (val) {
        var w = (this.oBarWidth - this.oBlockWidth) * (val - this.minValue) / (this.maxValue - this.minValue);
        this.oBlock.css('left', w + 'px');
        this.oBg.css('width', this.oBlockWidth / 2 + w);
    };
    SeekBar.prototype.setInputValue = function (val) {
        var v = 0, sv = this.minValue;
        var val = parseFloat(val);
        if (!isNaN(val)) {
            v = Math.round(val / this.step * this.step);
            sv = val < this.minValue ? this.minValue : (val > this.maxValue ? this.maxValue : ((val - v) < (this.step / 2) ? v : (v + this.step)));
        }
        this.oInput.val(sv);
        this.setBarValue(sv);
    };
    SeekBar.prototype.drage = function () {
        this.oBlock.on('mousedown', function (event) {
            var oleft = event.pageX;
            var l = this.oBlock.position().left;
            $(document).on('mousemove', function (event) {
                var sleft = event.pageX;
                this.setInputValue((sleft - oleft + l) * (this.maxValue - this.minValue) / (this.oBarWidth - this.oBlockWidth) + this.minValue);
            }.bind(this));
            $(document).on('mouseup', function () {
                $(document).off('mousemove');
                $(document).off('mouseup');
            }.bind(this));
        }.bind(this));
    };
    SeekBar.prototype.bindEvent = function () {
        this.oInput.on('blur', function () {
            this.setInputValue(this.oInput.val());
        }.bind(this));
        this.oBar.on('click', function (event) {
            if (!$(event.target).hasClass('seekBar-box-block')) {
                var num = (event.pageX - this.oBar.offset().left) * (this.maxValue - this.minValue) / (this.oBarWidth - this.oBlockWidth) + this.minValue;
                this.setInputValue(num);
            }
        }.bind(this));
        this.oUp.on('click', function () {
            this.setInputValue(parseFloat(this.oInput.val()) + this.step);
        }.bind(this));
        this.oDown.on('click', function () {
            this.setInputValue(parseFloat(this.oInput.val()) - this.step);
        }.bind(this));
    };
    SeekBar.prototype.getValue = function () {
        return this.oInput.val();
    };
    return SeekBar;
});