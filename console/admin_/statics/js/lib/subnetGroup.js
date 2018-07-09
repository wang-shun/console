define(['utils'], function(utils) {
  // 创建子网对象
  var createSubnets = function() {
    this.name = "";
    this.cidr_ip = Array(4);
    this.cidr_mask = "";
    this.isGateway = true;
    this.ipGroup = [];
    this.Gateway = Array(4);
    this.startIP = ['', '', '', ''];
    this.endIP = ['', '', '', ''];
  };
  createSubnets.prototype.setName = function(name) {
    this.name = name;
  };
  createSubnets.prototype.getName = function() {
    return this.name;
  };
  createSubnets.prototype.setCIDR_ip = function(cidr_ip) {
    this.cidr_ip = cidr_ip;
  };
  createSubnets.prototype.getCIDR_ip = function() {
    return this.cidr_ip;
  };
  createSubnets.prototype.setCIDR_mask = function(cidr_mask) {
    this.cidr_mask = cidr_mask;
  };
  createSubnets.prototype.getCIDR_mask = function() {
    return this.cidr_mask;
  };
  createSubnets.prototype.setIsGateway = function(isGateway) {
    this.isGateway = isGateway;
  };
  createSubnets.prototype.getIsGateway = function() {
    return this.isGateway;
  };
  createSubnets.prototype.setGateway = function(gateway) {
    this.Gateway = gateway;
  };
  createSubnets.prototype.getGateway = function() {
    return this.Gateway;
  };
  createSubnets.prototype.setStartIP = function(startip) {
    this.startIP = startip;
  };
  createSubnets.prototype.getStartIP = function() {
    return this.startIP;
  };
  createSubnets.prototype.setEndIP = function(endip) {
    this.endIP = endip;
  };
  createSubnets.prototype.getEndIP = function() {
    return this.endIP;
  };
  createSubnets.prototype.getIpGroup = function() {
    return this.ipGroup;
  };
  createSubnets.prototype.setIpGroup = function(ipgroup) {
    this.ipGroup = ipgroup;
  };
  createSubnets.prototype.loadCIDR_ip = function() {
    var splitnum = 0;
    var cidr_mask = this.getCIDR_mask();
    var cidr_ip = this.getCIDR_ip();
    var start_ip = this.getStartIP();
    var end_ip = this.getEndIP();
    start_ip[0] = end_ip[0] = cidr_ip[0];
    start_ip[1] = end_ip[1] = cidr_ip[1];
    start_ip[2] = end_ip[2] = cidr_ip[2];
    start_ip[3] = end_ip[3] = cidr_ip[3];
    if (cidr_mask <= 16) {
      splitnum = Math.pow(2, (cidr_mask - 8));
      tmp = 256;
      while (cidr_ip[1] < tmp) {
        tmp -= 256 / splitnum;
      }
      cidr_ip[1] = tmp;
      start_ip[1] = tmp;
      end_ip[1] = tmp + (256 / splitnum) - 1;
      cidr_ip[2] = 0;
      cidr_ip[3] = 0;
      start_ip[2] = cidr_ip[2];
      start_ip[3] = cidr_ip[3];
      end_ip[2] = 255;
      end_ip[3] = 254;
      start_ip[3] = 2;
    } else if (cidr_mask > 16 && cidr_mask <= 24) {
      splitnum = Math.pow(2, (cidr_mask - 16));
      tmp = 256;
      while (cidr_ip[2] < tmp) {
        tmp -= 256 / splitnum;
      }
      cidr_ip[2] = tmp;
      start_ip[2] = tmp;
      end_ip[2] = tmp + (256 / splitnum) - 1;
      cidr_ip[3] = 0;
      start_ip[3] = cidr_ip[3];
      end_ip[3] = 254;
      start_ip[3] = 2;
    } else {
      splitnum = Math.pow(2, (cidr_mask - 24));
      tmp = 256;
      while (cidr_ip[3] < tmp) {
        tmp -= 256 / splitnum;
      }
      end_ip[3] = tmp + (256 / splitnum) - 1;
      start_ip[3] = tmp;
      cidr_ip[3] = tmp;
      start_ip[3] = tmp + 2;
    }
    this.setStartIP(start_ip);
    this.setEndIP(end_ip);
    this.setCIDR_ip(cidr_ip);
  };
  createSubnets.prototype.loadGateway = function() {
    var cidr_ip = this.getCIDR_ip();
    cidr_ip[3] = cidr_ip[3] + 1;
    this.setGateway(cidr_ip);
  };
  createSubnets.prototype.getNewIPGroupHTML = function() {
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    var str = '<div class="box-list-input-ips">' +
      '<div class="box-from-input-ip">' +
      '<input type="text" value="' + ip_start[0] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_start[1] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_start[2] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_start[3] + '" />' +
      '</div>' +
      '<span class="box-from-inline">至</span>' +
      '<div class="box-from-input-ip">' +
      '<input type="text" value="' + ip_end[0] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_end[1] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_end[2] + '" />' +
      '<span>.</span>' +
      '<input type="text" value="' + ip_end[3] + '" />' +
      '</div>' +
      '<a href="javascript:;" class="add-ip">' +
      '<span class="glyphicon glyphicon-plus-sign"></span>' +
      '添加IP段' +
      '</a>' +
      '<i class="box-list-error"></i>' +
      '</div>';
    return str;
  };
  createSubnets.prototype.getIPGroupTip = function() {
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    var str = '建议在' + ip_start.join(',') + '至' + ip_end.join(',') + '区间内填写,如果您不设置IP段,系统默认为您开通全网段';
    return str;
  };
  createSubnets.prototype.getDataIPGroupHTML = function() {
    var ipGroup = this.getIpGroup();
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    var str = "", i = 0, len = ipGroup.length;
    if (len > 0) {
      for (i; i < len; i++) {
        if (ipGroup[i] && ipGroup[i]['start']) {
          str += '<div class="box-list-input-ips">' +
            '<div class="box-from-input-ip">' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['start'][0], ip_end[0]), ip_start[0]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['start'][1], ip_end[1]), ip_start[1]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['start'][2], ip_end[2]), ip_start[2]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['start'][3], ip_end[3]), ip_start[3]) + '" />' +
            '</div>' +
            '<span class="box-from-inline">至</span>' +
            '<div class="box-from-input-ip">' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['end'][0], ip_end[0]), ip_start[0]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['end'][1], ip_end[1]), ip_start[1]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['end'][2], ip_end[2]), ip_start[2]) + '" />' +
            '<span>.</span>' +
            '<input type="text" value="' + utils.num_to_min(utils.num_to_max(ipGroup[i]['end'][3], ip_end[3]), ip_start[3]) + '" />' +
            '</div>' +
            '<a href="javascript:;" class="delete-ip">' +
            '<span class="glyphicon glyphicon-trash"></span>' +
            '删除' +
            '</a>' +
            '<i class="box-list-error"></i>' +
            '</div>';
        }
      }
      return str;
    } else {
      return this.getNewIPGroupHTML();
    }
  };
  createSubnets.prototype.loadIPGroupHTML = function() {
    var dataIPGroupHTML = this.getDataIPGroupHTML();
    var iPGroupTip = this.getIPGroupTip();
    var html_str = dataIPGroupHTML +
      '<span class="box-from-input-tip" id="IP_group_tip">' + iPGroupTip + '</span>';
    $("#create_subnets_ip_group").html(html_str);
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    $('#create_subnets_ip_group').find('.box-from-input-ip').each(function() {
      $(this).find('input').eq(0).attr('disabled', 'disabled');
      if (ip_start[1] == ip_end[1]) {
        $(this).find('input').eq(1).attr('disabled', 'disabled');
      } else {
        $(this).find('input').eq(1).removeAttr('disabled');
      }
      if (ip_start[2] == ip_end[2]) {
        $(this).find('input').eq(2).attr('disabled', 'disabled');
      } else {
        $(this).find('input').eq(2).removeAttr('disabled');
      }
    });
  };
  createSubnets.prototype.refIPGroupHTML = function() {
    var dataIPGroupHTML = this.getDataIPGroupHTML();
    var iPGroupTip = this.getIPGroupTip();
    var html_str = dataIPGroupHTML +
      '<span class="box-from-input-tip" id="IP_group_tip">' + iPGroupTip + '</span>';
    $("#create_subnets_ip_group").html(html_str);
    $('#create_subnets_ip_group').find('.box-list-input-ips:last')
      .find('.delete-ip')
      .addClass('add-ip')
      .removeClass('delete-ip')
      .html('<span class="glyphicon glyphicon-plus-sign"></span>添加IP段');
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    $('#create_subnets_ip_group').find('.box-from-input-ip').each(function() {
      $(this).find('input').eq(0).attr('disabled', 'disabled');
      if (ip_start[1] == ip_end[1]) {
        $(this).find('input').eq(1).attr('disabled', 'disabled');
      } else {
        $(this).find('input').eq(1).removeAttr('disabled');
      }
      if (ip_start[2] == ip_end[2]) {
        $(this).find('input').eq(2).attr('disabled', 'disabled');
      } else {
        $(this).find('input').eq(2).removeAttr('disabled');
      }
    });
  };
  createSubnets.prototype.setIPGroupdata = function() {
    var ipGroupArr = [];
    $("#create_subnets_ip_group").find('.box-list-input-ips').each(function() {
      var inputGroupJSON = {};
      var $startInput = $(this).find('.box-from-input-ip').eq(0).find('input');
      var $endInput = $(this).find('.box-from-input-ip').eq(1).find('input');
      inputGroupJSON.start = [
        $startInput.eq(0).val(),
        $startInput.eq(1).val(),
        $startInput.eq(2).val(),
        $startInput.eq(3).val()
      ];
      inputGroupJSON.end = [
        $endInput.eq(0).val(),
        $endInput.eq(1).val(),
        $endInput.eq(2).val(),
        $endInput.eq(3).val()
      ];
      ipGroupArr.push(inputGroupJSON);
    });
    this.setIpGroup(ipGroupArr);
  };
  createSubnets.prototype.loadIPGroupTip = function() {
    $("#IP_group_tip").html(this.getIPGroupTip());
  };
  createSubnets.prototype.addIP = function() {
    var inputGroupJSON = {};
    var ip_start = this.getStartIP();
    var ip_end = this.getEndIP();
    inputGroupJSON.start = [
      ip_start[0],
      ip_start[1],
      ip_start[2],
      ip_start[3]
    ];
    inputGroupJSON.end = [
      ip_end[0],
      ip_end[1],
      ip_end[2],
      ip_end[3]
    ];
    this.setIPGroupdata();
    this.ipGroup.push(inputGroupJSON);
    this.refIPGroupHTML();
  };
  createSubnets.prototype.deleteIP = function(index) {
    this.ipGroup.splice(index, 1);
    this.refIPGroupHTML();
  };

  createSubnets.prototype.checkValue = function() {
    var name = this.getName();
    var cidr_ip = this.getCIDR_ip();
    var cidr_mask = this.getCIDR_mask();
    var isGateway = this.getIsGateway();
    var gateWay = this.getGateway();
    var groupIp = this.getIpGroup();
    if (/^\s*$/.test(name)) {
      $("#create_subnets_name").parent().find('.box-list-error').html('名称不能为空');
      return false;
    } else {
      $("#create_subnets_name").parent().find('.box-list-error').html('');
    }
    if (!(
        /^\d+$/.test(cidr_ip[0]) &&
        /^\d+$/.test(cidr_ip[1]) &&
        /^\d+$/.test(cidr_ip[2]) &&
        /^\d+$/.test(cidr_ip[3])
      )
    ) {
      $("#create_subnets_cidr").parent().find('.box-list-error').html('CIDR不能为空');
      return false;
    } else {
      $("#create_subnets_cidr").parent().find('.box-list-error').html('');
    }
    if (!/^\d+$/.test(cidr_mask)) {
      $("#create_subnets_cidr").parent().find('.box-list-error').html('CIDR掩码不能为空');
      return false;
    } else {
      $("#create_subnets_cidr").parent().find('.box-list-error').html('');
    }
    for (var i = 0; i < groupIp.length; i++) {
      if (
        parseInt(groupIp[i]['start'][0]) > parseInt(groupIp[i]['end'][0]) ||
        (
          parseInt(groupIp[i]['start'][0]) == parseInt(groupIp[i]['end'][0]) &&
          parseInt(groupIp[i]['start'][1]) > parseInt(groupIp[i]['end'][1])
        ) ||
        (
          parseInt(groupIp[i]['start'][0]) == parseInt(groupIp[i]['end'][0]) &&
          parseInt(groupIp[i]['start'][1]) == parseInt(groupIp[i]['end'][1]) &&
          parseInt(groupIp[i]['start'][2]) > parseInt(groupIp[i]['end'][2])
        ) ||
        (
          parseInt(groupIp[i]['start'][0]) == parseInt(groupIp[i]['end'][0]) &&
          parseInt(groupIp[i]['start'][1]) == parseInt(groupIp[i]['end'][1]) &&
          parseInt(groupIp[i]['start'][2]) == parseInt(groupIp[i]['end'][2]) &&
          parseInt(groupIp[i]['start'][3]) > parseInt(groupIp[i]['end'][3])
        )
      ) {
        $('.box-list-input-ips').eq(i).find('.box-list-error').html('终止IP段不能小于起始IP段');
        return false;
      } else {
        $('.box-list-input-ips').eq(i).find('.box-list-error').html('');
      }
    }
    var allocation_pools = [];
    for (var i = 0; i < groupIp.length; i++) {
      allocation_pools.push({
        start: groupIp[i]['start'].join('.'),
        end: groupIp[i]['end'].join('.')
      });
    }
    var param = {
      name: name,
      cidr: cidr_ip.join('.') + '/' + cidr_mask,
      dns_namespace: '114.114.114.114',
      allocation_pools: allocation_pools
    };
    if (isGateway) {
      param.gateway_ip = gateWay.join('.');
    } else {
      delete (param.gateway_ip);
    }
    return param;
  };

  return createSubnets;
});