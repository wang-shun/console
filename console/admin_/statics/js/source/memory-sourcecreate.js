define(['utils', 'plusMinusInput'], function (utils, PlusMinusInput) {
    var ODD_COUNT = 0;
    var ODD_UNIT = 'G';
    $("#odd_count").html(ODD_COUNT + ODD_UNIT);
    var owner = $("#owner").val();
    var zone = $("#zone").val();
    var box = new PlusMinusInput($("#osd_number"),{
        min: 2,
        max: 2,
        tip: "空闲设备<span style='color:red'>{%max-%value}</span>台",
        waring:"为保证副本备份，设备数量至少2台。",
        hooks : {
            callback: function(status){
                var value = box.getValue();
                $("#count").html((value * ODD_COUNT).toFixed(2) + ODD_UNIT);
            }
        }
    });

    var name = '';
    function setName(){
        name = $("#name").val();
        if(/^[_A-Za-z0-9]+$/.test(name)){
            $("#name_error").html('');
        }else{
            $("#name_error").html('名称只能由字母数组下划线组成');
            return false;
        };
        return name;
    }
    function setMax(){
        utils._ajax({
            url: '/admin/pools/storage_resource/device',
            contentType: 'application/json',
            data: JSON.stringify({
                owner: owner,
                zone: zone,
                kind: $("#type").val().toLocaleLowerCase(),
            }),
            succCB: function (reault) {
                var max = reault.ret_set.num;
                ODD_COUNT = reault.ret_set.unit / (1024 * 1024);
                if(max>=2){
                    $("#create_memory").removeClass('disabled')
                }else{
                    $("#create_memory").addClass('disabled')
                }
                $("#odd_count").html(ODD_COUNT.toFixed(2) + ODD_UNIT);
                $("#count").html((2 * ODD_COUNT).toFixed(2) + ODD_UNIT);
                box.setConfig({
                     max: max
                });
            },
            errCB: function (err) {
                utils.errMsg(err.ret_msg);
                $("#odd_count").html(0 + ODD_UNIT);
                $("#count").html(0 + ODD_UNIT);
                box.setConfig({
                     max: 0
                });
            }
        });
    }
    setMax();
    $("#type").on('change',function(){
        setMax();
    });
    $("#create_memory").click(function(){
        if($(this).hasClass('disabled'))return false;
        name = setName();
        if(name){
            $("#create_memory").addClass("disabled");
            utils._ajax({
                url: '/admin/pools/storage_resource/create',
                contentType: 'application/json',
                data: JSON.stringify({
                    owner: owner,
                    zone: zone,
                    name: name,
                    kind: $("#type").val().toLocaleLowerCase(),
                    size: box.getValue(),
                }),
                succCB: function (reault) {
                    utils.succMsg('存储池创建成功');
                    location.href = '/admin/sourceManage/memorySource';
                },
                errCB: function (err) {
                    utils.errMsg(err.ret_msg);
                },
                error: function () {
                    utils.errMsg('存储池创建失败');
                }
            });
            $('#delete_memory_modal').modal('hide');

        };
    });
});
