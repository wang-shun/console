define(['utils', 'selectBox'], function(utils, SelectBox) {

  var box = new SelectBox({
    container: $("#box-select-box"), // 用于生成插件的父元素
    leftTitle: "所有可用设备",
    rightTitle: "已加入设备",
    isSearchable: true,
    dataList: [[], []]
  });
  utils._ajax({
    url: "/admin/physical_machine/hostname_list/api",
    data: {
      action: 'DescribePhysicalMachineHostnameList',
      owner: $("#owner").val(),
      pool_name: 'default'
    },
    finalCB: function(result) {
      var data = result.ret_set.host_list;
      for (var i = 0, j = data.length; i < j; i++) {
        box.setDataLeft([{'id': data[i], value: data[i]}]);
      }
    }
  });

  $("#create_compute").click(function() {
    var compute_name = $("#create_compute_name").val();
    var hosts = box.getData('right').map(function(item) {
      return item.id;
    });
    if (compute_name.trim() == "") {
      utils.errMsg("名称不能为空");
    } else {
      var params = {
        owner: $("#owner").val(),
        zone: $("#zone").val(),
        name: compute_name,
        hosts: hosts,

      };
      utils._ajax({
        url: "/admin/pools/compute_resource/create",
        data: JSON.stringify(params),
        contentType: 'application/json',
        succCB: function(result) {
          utils.succMsg("创建成功");
          location.href = '/admin/sourceManage/computeSource';
        },
        errCB: function(result) {
          utils.errMsg(result.ret_msg);
        }
      });
    }
  });
});
