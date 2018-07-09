define(['utils', 'plusMinusInput'], function (utils, PlusMinusInput) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var ODD_COUNT = 0;
    var ODD_UNIT = 'G';
    var status = {
        'Normal' : '正常',
        'Modifying' : '修改中',
        'Recovering': '恢复中',
        'Creating' : '创建中',
        'Abnormal' : '异常',
    };
    var name = decodeURIComponent(param.name);
    var new_name=name;
    var box = new PlusMinusInput($("#osd_number"),{
        min: 2,
        max: 0,
        hooks:{
            minusPreCallback: function(){
                var getChangeValue = box.getChangeValue();
                return (getChangeValue > -1);
            },
            changePreCallback: function(){
                var getChangeValue = box.getChangeValue();
                return (getChangeValue > -1);
            },
            callback: function(status){
                if(status == 'success'){
                    setCountNum();
                };
            }
        },
        tip: "空闲设备<span style='color:red'>{%max - %value}</span>台",
        waring:"为保证副本备份，设备数量至少2台。<br/><br/> 为了保证数据安全，每次操作只能减少一台设备。"
    });
    utils._ajax({
        url: '/admin/pools/storage_resource/info',
        contentType: 'application/json',
        data: JSON.stringify({
            owner: owner,
            zone: zone,
            pool_name: decodeURIComponent(param.name)
        }),
        finalCB: function (result) {
            var data = result.data[0];
            $("#name").val(data.name);
            $("#type").html(data.type);
            $("#total").html(utils.toMemory(data.size,'KB','GB'));
            $("#used").html(utils.toMemory(data.used,'KB','GB'));
            utils._ajax({
                url: '/admin/pools/storage_resource/device',
                contentType: 'application/json',
                data: JSON.stringify({
                    owner: owner,
                    zone: zone,
                    kind: data.type,
                }),
                succCB: function (reault) {
                    var max = reault.ret_set.num;
                    ODD_COUNT = reault.ret_set.unit / (1024 * 1024);
                    $("#odd_count").html(ODD_COUNT.toFixed(2) + ODD_UNIT);
                    $("#count").html((2 * ODD_COUNT).toFixed(2) + ODD_UNIT);
                    box.setConfig({
                        defaultValue: data.dev_num,
                        max: (max+data.dev_num)
                    });
                }
            });
        },
        error: function () {
            utils.errMsg('存储池获取失败');
            $("#odd_count").html(0 + ODD_UNIT);
            $("#count").html(0 + ODD_UNIT);
            box.setConfig({
                 max: 0
            });
        }
    });
    function setCountNum(){
        var getValue = box.getValue();
        $("#count_num").html(ODD_COUNT * getValue);
    }

    function setName(){
        new_name = $("#name").val();
        if(/^[_A-Za-z0-9]+$/.test(new_name)){
            $("#name_error").html('');
        }else{
            $("#name_error").html('名称只能由字母数组下划线组成');
            return false;
        };
        return new_name;
    }
    $("#edit_memory").click(function(){
        new_name = setName();
        if(name){
            if(name != new_name && !box.getChangeValue()){
                editAdjust('name', new_name);
            }else if(box.getChangeValue() && name == new_name){
                editAdjust('size', box.getChangeValue());
            }else if(name != new_name && box.getChangeValue()){
                editAdjust('size', box.getChangeValue(),function(){
                    editAdjust('name', new_name)
                })
            }
        };

        function editAdjust(type,value, callback){
            var params = {
                owner: owner,
                zone: zone,
                name: name,
                new_name:value,
                adjust_size: value,
            };
            if(type == 'name'){
                delete params.adjust_size;
            }
            if(type == 'size'){
                delete params.new_name;
            }
            utils._ajax({
                url: '/admin/pools/storage_resource/adjust',
                contentType: 'application/json',
                data: JSON.stringify(params),
                succCB: function (reault) {
                    if(callback){
                        callback();
                    }else{
                        utils.errMsg('存储池修改成功');
                        location.href = '/admin/sourceManage/memorySource';
                    }
                },
                errCB: function (err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function () {
                    utils.errMsg('存储池修改失败');
                }
            });
        }
    });
});