
/* 使用案例
 * var $app = $("#app");
 * var box = new PlusMinusInput($app, {
 *    defaultValue: Number, //默认值
      min: Number, //最小值
      max: Number, //最大值
      deep: Number, //每次位移量
      tip: String, // 左边提示，如果不写，那么就不展示，{%d}来表示数字
      waring: String // 下边提示，如果不写，那么就不展示，{%d}来表示数字
      hooks:{   //钩子
        pulsPreCallback:function(){},
        minusPreCallback:function(){},
        pulsCallback:function(){},
        minusListCallback:function(){}
      }
    });
 * box.setConfig({ // 动态设置各种参数
 *   min: Number, //最小值
     max: Number, //最大值
     deep: Number, //每次位移量
 * });
 * console.log(box.getValue()); // 获取当前值
 * console.log(box.getChangeValue()); // 获取变化值
 */

define(function () {
    var PlusMinusInput = function (obj, config) {
        this.obj = obj;
        this.elem = {};
        this.defaultConfig = config;
        this.init(config);
    };
    PlusMinusInput.prototype.init = function(config){
        this.initConfig(config);
        this.initHooks(config);
        this.initHtml();
        this.bandEvent();
    };
    PlusMinusInput.prototype.initConfig = function(config){
        this.min = config.min || 0;
        this.max = config.max || 0;
        this.deep = config.deep || 1;
        this.hooks = config.hooks || {};
        this.value = config.defaultValue || this.min;
        this.defaultValue = this.value;
        this.tip = config.tip || '';
        this.waring = config.waring || '';
    };
    PlusMinusInput.prototype.initHooks = function(config){
        var hooks = {
            plusPreCallback: function(){
                return true;
            },
            minusPreCallback: function(){
                return true;
            },
            plusCallback: function(){

            },
            minusCallback: function(){

            },
            changePreCallback: function(){
                return true;
            },
            changeCallback: function(){

            },
            callback: function(){

            }
        };
        this.hooks = Object.assign(hooks,this.hooks);
    };
    PlusMinusInput.prototype.initHtml = function(){
        var str = `<div class="plusMinusInput-box">
                <div class="plusMinusInput-control">
                    <button class="plusMinusInput-control-minus">-</button>
                    <div class="plusMinusInput-control-input">
                        <input type="number" />
                    </div>
                    <button class="plusMinusInput-control-plus">+</button>
                </div>
                <div class="plusMinusInput-tip"></div>
                <div class="plusMinusInput-waring"></div>
            </div>`;
        this.obj.html(str);
        this.elem = {
            box: this.obj.find('.plusMinusInput-box'),
            minus: this.obj.find('.plusMinusInput-control-minus'),
            plus: this.obj.find('.plusMinusInput-control-plus'),
            input: this.obj.find('.plusMinusInput-control-input input'),
            tip: this.obj.find('.plusMinusInput-tip'),
            waring: this.obj.find('.plusMinusInput-waring'),
        };
        this.elem.input.val(this.value);
        this.renderTip();
        this.renderWaring();

    };
    PlusMinusInput.prototype.bandEvent = function(){
        this.elem.minus.on('click',this.bandEventMinus.bind(this));
        this.elem.plus.on('click',this.bandEventPlus.bind(this));
        this.elem.input.on('change',this.bandEventInput.bind(this));
    };
    PlusMinusInput.prototype.bandEventMinus = function(){
        var status = 'error';
        if(this.hooks.minusPreCallback()){
            this.setValue(this.getValue() - this.deep);
            status = 'success';
        }
        this.hooks.minusCallback(status);
        this.hooks.callback(status);
    };
    PlusMinusInput.prototype.bandEventPlus = function(){
        var status = 'error';
        if(this.hooks.plusPreCallback()){
            this.setValue(this.getValue() + this.deep);
            status = 'success';
        }
        this.hooks.plusCallback(status);
        this.hooks.callback(status);
    };
    PlusMinusInput.prototype.bandEventInput = function(event){
        var old_value = this.value;
        this.value = event.target.value;
        var status = 'error';
        if(this.hooks.changePreCallback()){
            status = 'success';
        }else{
            this.value = old_value;
            status = 'error';
        }
        this.hooks.changeCallback('success');
        this.setValue(this.value);
        this.hooks.callback(status);
    };
    PlusMinusInput.prototype.setValue = function(value){
        if(value > this.max){
            value = this.max;
        }
        if(value < this.min){
            value = this.min;
        }
        var tmpValue = value % this.deep;
        if(tmpValue !== 0){
            value = (parseInt(value /this.deep) * this.deep);
            if(tmpValue > this.deep/2){
              value = value + this.deep;
            }
        }
        this.elem.input.val(value);
        this.value = parseInt(value);
        this.renderTip();
    };
    PlusMinusInput.prototype.setConfig = function(newConfig){
        var config = Object.assign(this.defaultConfig,newConfig);
        this.init(config);
    };
    PlusMinusInput.prototype.getValue = function(){
        return this.value;
    };
    PlusMinusInput.prototype.getChangeValue = function(){
        return this.value - this.defaultValue;
    };
    PlusMinusInput.prototype.renderTip = function(){
        if(this.tip){
            var tip = this.tip;
            var tmp = tip.match(/\{([^}]*?)\}/g);
            for(var i =0 ,l = tmp.length;i<l;i++){
                var str = tmp[i].replace(/%value/g,this.value).replace(/%max/g,this.max).slice(1,-1);
                tip = tip.replace(tmp[i],eval(str));
            }
            this.elem.tip.html(tip);
        }
    };
    PlusMinusInput.prototype.renderWaring = function(){
        if(this.waring){
            this.elem.waring.html(this.waring);
        }
    };
    return PlusMinusInput;
});