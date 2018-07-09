define(['utils'], function(utils) {
  var owner = $('#owner').val();
  var zone = $('#zone').val();
  var selected_source = {};
  var columns = [{
    "data": "name",
    "name": "name"
  }, {
    "data": "host_count",
    "name": "host_count"
  }, {
    "data": "cpu",
    "name": "cpu"
  }, {
    "data": "memory",
    "name": "memory"
  }];
  var columnDefs = [{
    targets: 0,
    render: function(data, type, item) {
    if(item.type === 'KVM'){
      return '<a href="/admin/sourceManage/computeSourceDetails?name=' + item.name + '">' + data + '</a>';
    }else{
      return '<span href="/admin/sourceManage/computeSourceDetails?name=' + item.name + '">' + data + '</span>';
    }
    }
  }, {
    targets: 1,
    render: function(data, type, item) {
      return '<a href="/admin/sourceManage/physicsSource?name=' + item.name + '">' + data + '</a>';
    }
  }, {
    targets: 2,
    render: function(data, type, item) {
      var num = data * 100;
      if (item.memory.total_mem === 0) {
        return '-';
      }
      return num.toFixed(2) + '%';
    }
  }, {
    targets: 3,
    render: function(data, type, item) {
      var num = data.use_mem / data.total_mem * 100;
      if (isNaN(num)) {
        return '-';
      }
      return num.toFixed(2) + '%';
    }
  }];
  var _datatable = utils.datatable($("#pools_compute_list"), {
    columns: columns,
    columnDefs: columnDefs
  }, {url: '/admin/pools/compute_resource/list', data: {owner: owner, zone: zone, flag: 1}});

  $("#delete_compute").click(function() {
    if (selected_source.host_count) {
      $('#delete_compute_modal').find('.modal-body .text-center').html('该集群存在宿主机无法直接删除，请先进行该集群进行修改，移除所有的物理机再进行删除池操作。');
      $('#delete_compute_btn').hide();
    } else {
      $('#delete_compute_modal').find('.modal-body .text-center').html('确认删除该集群。');
      $('#delete_compute_btn').show();
    }
    $('#delete_compute_modal').modal();
  });

  utils.tableClick($("#pools_compute_list"), {
    onCB: function(obj) {
      $("#edit_compute").removeAttr('disabled');
      $("#delete_compute").removeAttr('disabled');
      selected_source = {
        name: $(obj[0].children[0]).text(),
        host_count: parseInt($(obj[0].children[1]).find('a').html()),
        instances_count: parseInt($(obj[0].children[4]).find('a').html())
      };
    },
    offCB: function() {
      $("#edit_compute").attr('disabled', 'disabled');
      $("#delete_compute").attr('disabled', 'disabled');
      selected_source = {};
    }
  });
  $("#edit_compute").click(function() {
    if (selected_source.name) {
      location.href = $(this).data('href') + '?name=' + selected_source.name;
    }
  });

  $('#delete_compute_btn').on('click', function() {
    utils._ajax({
      url: '/admin/pools/compute_resource/delete',
      contentType: 'application/json',
      data: JSON.stringify({
        owner: owner,
        zone: zone,
        name: selected_source.name
      }),
      succCB: function() {
        utils.succMsg('资源池删除成功');
      },
      errCB: function(err) {
        utils.errMsg(err.ret_msg);
      },
      error: function() {
        utils.errMsg('资源池删除失败');
      }
    });
    $('#delete_compute_modal').modal('hide');
    location.href = '/admin/sourceManage/computeSource';
  });
});