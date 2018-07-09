define(['utils'], function (utils) {
    var owner = $('#owner').val();
    var zone = $('#zone').val();
    var param = utils.getUrlParams();
    var status = {
        'Normal' : '正常',
        'Modifying' : '修改中',
        'Recovering': '恢复中',
        'Creating' : '创建中',
        'Abnormal' : '异常',
    };
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
            $("#name").html(data.name);
            $("#status").html(status[data.status] || '异常');
            $("#type").html(data.type);
            $("#dev_num").html(data.dev_num);
            $("#total").html(utils.toMemory(data.size,'KB','GB'));
            $("#used").html(utils.toMemory(data.used,'KB','GB'));
        },
        error: function () {
            utils.errMsg('存储池获取失败');
        }
    });
    $("#memory").on("click",function(){
        location.href = '/admin/sourceManage/memorySource';
    })
});