define(['utils', 'selectBox'], function(utils, SelectBox) {
  var param = utils.getUrlParams();
  $("#edit_compute_name").val(decodeURIComponent(param.name));
  var box = new SelectBox({
    container: $("#box-select-box"), // 用于生成插件的父元素
    leftTitle: "所有可用设备",
    rightTitle: "已加入设备",
    isSearchable: true,
    event: {
      removeListPreCallback: function(id) {
        var vm_amount = getPhysicalNumber(id);
        var host = box.getData('right');
        if (vm_amount > 0 && host.length > 1) {
          $("#warning_remove_host_modal").modal();
          return false;
        } else if (vm_amount > 0 && host.length === 1) {
          $("#remove_host_modal").modal();
          return false;
        } else {
          return true;
        }
      }
    },
    dataList: [[], []]
  });
  $("#remove_host_btn").click(function() {
    $('#box-select-box').find('.multi-select-box-content-right').find('li button').click();
  });
  utils._ajax({
    url: "/admin/physical_machine/hostname_list/api",
    data: {
      action: 'DescribePhysicalMachineHostnameList',
      owner: $("#owner").val(),
      pool_name: decodeURIComponent(param.name)
    },
    finalCB: function(result) {
      var data = result.ret_set.host_list;
      for (var i = 0, j = data.length; i < j; i++) {
        box.setDataRight([{'id': data[i], value: data[i]}]);
      }
    }
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
  function getPhysicalNumber(id) {
    var num = null;
    utils._ajax({
      url: "/admin/physical_machine/vm_amount/api",
      async: true,
      data: {
        action: 'DescribePhysicalMachineVmamount',
        owner: $("#owner").val(),
        physical_machine_hostname: id
      },
      succCB: function(result) {
        num = result.ret_set.vm_amount;
      }
    });
    return num;
  }
  $("#edit_compute").click(function() {
    var newname = $("#edit_compute_name").val();
    var name = decodeURIComponent(param.name);
    var change_compute_list = box.getChangedData('right');
    var add_compute_list = [];
    var del_compute_list = [];
    for (var i = 0, j = change_compute_list.length; i < j; i++) {
      if (change_compute_list[i].type == 'add') {
        add_compute_list.push(change_compute_list[i].data.id);
      }
      if (change_compute_list[i].type == 'remove') {
        del_compute_list.push(change_compute_list[i].data.id);
      }
    }
    var COUNT = 0;
    if (newname !== name) {
      utils._ajax({
        url: "/admin/pools/compute_resource/rename",
        async: true,
        data: {
          owner: $("#owner").val(),
          zone: $("#zone").val(),
          newname: newname,
          name: name,
        },
        succCB: function() {
          utils.succMsg('资源池名称修改成功');
        },
        errCB: function(err) {
          utils.errMsg(err.ret_msg);
        },
        error: function() {
          utils.errMsg('资源池名称修改失败');
        }
      });
    }
    href_list();
    if (add_compute_list.length > 0) {
      utils._ajax({
        url: "/admin/pools/compute_resource/addhosts",
        contentType: 'application/json',
        data: JSON.stringify({
          owner: $("#owner").val(),
          zone: $("#zone").val(),
          name: newname,
          hosts: add_compute_list
        }),
        succCB: function() {
          utils.succMsg('资源池添加物理机成功');
          href_list();
        },
        errCB: function(err) {
          utils.errMsg(err.ret_msg);
        },
        error: function() {
          utils.errMsg('资源池添加物理机失败');
        }
      });
    } else {
      href_list();
    }
    if (del_compute_list.length > 0) {
      utils._ajax({
        url: "/admin/pools/compute_resource/delhosts",
        contentType: 'application/json',
        data: JSON.stringify({
          owner: $("#owner").val(),
          zone: $("#zone").val(),
          name: newname,
          hosts: del_compute_list
        }),
        succCB: function() {
          utils.succMsg('资源池删除物理机成功');
          href_list();
        },
        errCB: function(err) {
          utils.errMsg(err.ret_msg);
        },
        error: function() {
          utils.errMsg('资源池删除物理机失败');
        }
      });
    } else {
      href_list();
    }
    function href_list() {
      COUNT++;
      if (COUNT >= 3) {
        location.href = '/admin/sourceManage/computeSource';
      }
    }
  });
});
