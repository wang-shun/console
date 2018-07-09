define(['utils', 'seekBar', 'selectBox'], function (utils, SeekBar, SelectBox) {
    var is_public = true;

    var VCPUS = new SeekBar($("#create_flavor_VCPUS"), {
        maxValue: 99,
        minValue: 1,
        step: 1,
        unit: "核"
    });

    var memory = new SeekBar($("#create_flavor_memory"), {
        maxValue: 99,
        minValue: 1,
        step: 1,
        unit: "GB"
    });

    var ghost = new SeekBar($("#create_flavor_ghost"), {
        maxValue: 100,
        minValue: 20,
        step: 1,
        unit: "GB"
    });

    var box = new SelectBox({
        container: $("#box-select-box"), // 用于生成插件的父元素
        leftTitle: "人员名单",
        rightTitle: "可见人员名单",
        isSearchable: true,
        dataList: [
            [], // 左侧列表
            []  // 右侧列表
        ]
    });

    utils._ajax({
        url: "/finance/api/",
        data: {
            action: 'DescribeDepartmentMember',
            data: {
                department_id: "dep-00000001"
            },
            owner: $("#owner").val(),
            zone: $("#zone").val(),
            timestamp: new Date().getTime(),
        },
        succCB: function (result) {
            var data = result.ret_set.member_list;
            for (var i = 0, j = data.length; i < j; i++) {
                box.setDataLeft([{'id': data[i]['id'], value: data[i]['name']}]);
            }
        }
    });

    $("#open_gateway").click(function () {
        $("#box-select-content").hide();
        $("#open_gateway").addClass("active");
        $("#close_gateway").removeClass("active");
        is_public = true;
    });

    $("#close_gateway").click(function () {
        $("#box-select-content").show();
        $("#open_gateway").removeClass("active");
        $("#close_gateway").addClass("active");
        is_public = false;
    });

    $("#create_flavor").click(function () {
        var flavor_name = $("#create_flavor_name").val();
        var ram = memory.getValue();
        var vcpus = VCPUS.getValue();
        var disk = ghost.getValue();

        var tenant_list = box.getData('right').map(function (item) {
            return item.id;
        });
        if (flavor_name.trim() == "") {
            utils.errMsg("名称不能为空");
        } else {
            var params = {
                action: "AddInstanceTypes",
                owner: $("#owner").val(),
                zone: $("#zone").val(),
                flavor_name: flavor_name,
                ram: ram,
                vcpus: vcpus,
                disk: disk,
                is_public: is_public
            };
            if (!is_public) {
                params.tenant_list = tenant_list.toString();
            }
            console.log(params);
            utils._ajax({
                url: "/admin/api/",
                data: params,
                succCB: function (result) {
                    utils.succMsg("创建成功");
                    location.href = '/admin/customize/flavor';
                },
                errCB: function (result) {
                    utils.errMsg(result.ret_msg);
                }
            });
        }
    });
});