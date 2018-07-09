define(['utils', 'seekBar', 'selectBox'], function (utils, SeekBar, SelectBox) {
    var param = utils.getUrlParams();
    var change_tenant_list = [];
    var box = null;
    var add_tenant_list = [];
    var del_tenant_list = [];
    utils._ajax({
        url: '/admin/api/',
        data: {
            action: 'ShowoneInstanceType',
            owner: $('#owner').val(),
            zone: $('#zone').val(),
            flavor_id: param.flavor_id
        },
        succCB: function (result) {
            $("#edit_name").html(result.ret_set.name);
            $("#edit_vcpus").html(result.ret_set.vcpus + '(核)');
            $("#edit_ram").html(result.ret_set.ram + '(G)');
            $("#edit_disk").html(result.ret_set.disk + '(G)');
            $("#edit_public").html(result.ret_set.public ? '公开' : '不公开');
            param.is_public = result.ret_set.public;
            param.name = result.ret_set.name;
            if (!result.ret_set.public) {
                box = new SelectBox({
                    container: $("#box-select-box"), // 用于生成插件的父元素
                    leftTitle: "人员名单",
                    rightTitle: "可见人员名单",
                    isSearchable: true,
                    dataList: [[], []]
                });
                var tenant_list = result.ret_set.tenant_list;
                utils._ajax({
                    url: '/finance/api/',
                    data: {
                        action: "DescribeDepartmentMember",
                        data: {
                            department_id: "dep-00000001"
                        },
                        owner: $("#owner").val(),
                        zone: $("#zone").val(),
                        timestamp: new Date().getTime(),
                    },

                    succCB: function (result) {
                        var data = result.ret_set.member_list;
                        var leftData = [];
                        var rightData = [];
                        for (var i = 0, j = data.length; i < j; i++) {
                            leftData.push({id: data[i]['id'], value: data[i]['name']});
                            for (var m = 0, n = tenant_list.length; m < n; m++) {
                                if (data[i]['id'] == tenant_list[m]) {
                                    rightData.push({id: data[i]['id'], value: data[i]['name']});
                                    leftData.pop();
                                }
                            }
                        }
                        box.setDataLeft(leftData);
                        box.setDataRight(rightData);
                    }
                });

            }
        },
        errCB: function (result) {
            utils.errMsg(result.ret_msg);
        }
    });
    $("#save_flavor").click(function () {
        change_tenant_list = box.getChangedData('right');
        add_tenant_list = [];
        del_tenant_list = [];
        for (var i = 0, j = change_tenant_list.length; i < j; i++) {
            if (change_tenant_list[i].type == 'add') {
                add_tenant_list.push(change_tenant_list[i].data.id);
            }
            if (change_tenant_list[i].type == 'remove') {
                del_tenant_list.push(change_tenant_list[i].data.id);
            }
        }
        var params = {
            action: "ChangeInstanceType",
            owner: $("#owner").val(),
            zone: $("#zone").val(),
            name: param.name,
            flavor_id: param.flavor_id,
            is_public: param.is_public
        };
        if (!param.is_public) {
            params.add_tenant_list = add_tenant_list.toString();
            params.del_tenant_list = del_tenant_list.toString();
        }
        utils._ajax({
            url: "/admin/api/",
            data: params,
            succCB: function (result) {
                utils.succMsg("修改成功");
                location.href = '/admin/customize/flavor';
            },
            errCB: function (result) {
                utils.errMsg(result.ret_msg);
            }
        });
    });
});
