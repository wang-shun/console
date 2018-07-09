define(['utils'], function(utils) {
  var param = utils.getUrlParams();
  var change_tenant_list = [];
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
    succCB: function(result) {
      $("#edit_flavor_name").html(result.ret_set.name);
      $("#edit_vcpus").html(result.ret_set.vcpus + '(核)');
      $("#edit_ram").html(result.ret_set.ram + '(G)');
      $("#edit_disk").html(result.ret_set.disk + '(G)');
      $("#edit_public").html(result.ret_set.public ? '公开' : '不公开');
      if (!result.ret_set.public) {
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
          succCB: function(result) {
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
          }
        });
      }
    },
    errCB: function(result) {
      utils.errMsg(result.ret_msg);
    }
  });
});
