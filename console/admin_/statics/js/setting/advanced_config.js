/**
 * Created by wuyang on 16/8/6.
 */
define(['utils'], function(utils) {
    $("#tactic").on('change', function() {
        $("#tactic").val($(this).val());
    });
    $("#quota").on('change', function() {
        $("#quotaForm").submit();
    });
    $("#quota_switch").find('input').on("click", function() {
        var isQuotaSwitchChecked = $("#quota_switch").find("input").prop("checked");
        utils._ajax({
            url: "/admin/setting/advanced_config",
            data: {
                'action': 'SetUserQuota',
                'switch': isQuotaSwitchChecked.toString()
            },
            succCB: function() {
                $("#quota_switch_label").html(isQuotaSwitchChecked ? '开启' : '关闭');
                utils.succMsg('用户模式配置成功');
            },
            errCB: function() {
                utils.errMsg('用户模式匹配失败');
            },
            error: function() {
                utils.errMsg('用户模式匹配失败');
            }
        });
    });

    utils._ajax({
        url: '/admin/setting/advanced_config',
        data: {'action': 'DescribeDrs'},
        succCB: function(result) {
            var obj = result.ret_set;
            for (var i in obj) {
                if (i == 'switch') continue;
                $("input[name='" + i + "']").val(obj[i]);
                $('#tableDrsInput' + i).html(obj[i]);
            }
            $('#tableDrsSwitch').html(obj.switch ? '开启' : '关闭');
            if (obj.switch) {
                $('#isSwitch_true').attr('checked', 'checked');
            } else {
                $('#isSwitch_false').attr('checked', 'checked');
            }
        },
        errCB: function(result) {
            utils.errMsg(result.ret_msg);
        },
        error: function(result) {
            utils.errMsg(result.ret_msg);
        }
    });

    $('body').on('click', '#drsSubmit', function() {
        var CPU = $('#inputCPU').val(), RAM = $('#inputMemory').val();
        var isSwitch = $('input[name="switch"]:checked').val();
        if (!/^\d+$/.test(CPU) || !/^\d+$/.test(RAM)) {
            utils.errMsg('cpu和内存必须设置为数字');
            return false;
        }
        if ((CPU > 100 || CPU < 0) || (RAM > 100 || RAM < 0)) {
            utils.errMsg('cpu和内存必须设置为0到100之内');
            return false;
        }
        utils._ajax({
            url: '/admin/setting/advanced_config',
            data: {'action': 'SetDrs', 'switch': !!isSwitch, CPU: CPU, RAM: RAM},
            succCB: function() {
                utils.succMsg('DRS动态资源调度成功');
                location.reload();
            },
            errCB: function(result) {
                utils.errMsg(result.ret_msg);
                location.reload();
            },
            error: function(result) {
                utils.errMsg(result.ret_msg);
                location.reload();
            }
        });
    });

    utils._ajax({
        url: '/admin/setting/advanced_config',
        data: {'action': 'DescribePolicy'},
        succCB: function(result) {
            var policy_list = result.ret_set;
            if (policy_list) {
                var str = '';
                var tablestr = '';
                for (var i = 0; i < policy_list.length; i++) {
                    str += '<label class="checkbox-inline">' +
                            '<input type="checkbox" ' + (policy_list[i].policy_used && "checked=checked") + ' value="' + policy_list[i].policy_id + '">' +
                            policy_list[i].policy_name +
                        '</label>';
                    tablestr += policy_list[i].policy_used ? '+' + policy_list[i].policy_name : '';
                }
                $('#tablePolicy').html(tablestr ? tablestr.substring(1) : '默认策略');
                $('#tacticSelect').html(str);
            }
        },
        errCB: function(result) {
            utils.errMsg(result.ret_msg);
        },
        error: function(result) {
            utils.errMsg(result.ret_msg);
        }
    });

    $('body').on('click', '#tacticSubmit', function() {
        var policylist = [];
        $('#tacticSelect').find('input:checked').each(function() {
            var obj = {'policy_id': ~~$(this).val()};
            policylist.push(obj);
        });
        utils._ajax({
            url: '/admin/setting/advanced_config',
            data: {'action': 'SetPolicy', 'policy_list': JSON.stringify(policylist)},
            finalCB: function(result) {
                utils.succMsg(result.ret_msg);
                location.reload();
            }
        });

    });

    $("#console_logo").click(function() {
        $("#console_logo_form").find('input[type="file"]').click().change(function() {
            $(this).parent().find('input[type="submit"]').click();
        });
    });
    $("#admin_logo").click(function() {
        $("#admin_logo_form").find('input[type="file"]').click().change(function() {
            $(this).parent().find('input[type="submit"]').click();
        });
    });

    var inputExp = {
        "^\s*$": "平台名称不能为空",
        "^.{21,}$": "长度不能超过20位字符"
    };

    var checkName = function($obj, val) {
        var $tip = $obj.parents('.modal-content').find('.input-text-tip');
        var $group = $obj.parents('.modal-content').find('.form-group');
        for (exp in inputExp) {
            var reg = new RegExp(exp);
            if (reg.test(val)) {
                $tip.html(inputExp[exp]).css('display', 'block');
                $group.addClass('has-error');
                return false;
            }
        }
        $tip.html(inputExp[exp]).css('display', 'none');
        $group.removeClass('has-error');
        return true;
    };

    $('#submit_consoleBtn').click(function() {
        var inputConsoleVal = $('#inputConsole').val().trim();
        var isCheckName = checkName($(this), inputConsoleVal);
        if (isCheckName) {
            utils._ajax({
                url: '/admin/setting/advanced_config',
                data: {'action': 'platform_name', 'console_name': inputConsoleVal},
                finalCB: function(result) {
                    utils.succMsg(result.ret_msg);
                    location.reload();
                }
            });
        }
    });

    $('#submit_adminBtn').click(function() {
        var inputAdminVal = $('#inputAdmin').val().trim();
        var isCheckName = checkName($(this), inputAdminVal);
        if (isCheckName) {
            utils._ajax({
                url: '/admin/setting/advanced_config',
                data: {'action': 'platform_name', 'admin_name': inputAdminVal},
                finalCB: function(result) {
                    utils.succMsg(result.ret_msg);
                    location.reload();
                }
            });
        }
    });

    var clickBtn = ['#drsBtn', '#tacticBtn', '#uploadLogoBtn', '#editName_consoleBtn', '#editName_adminBtn'];
    bindOpenModal(clickBtn);
    function bindOpenModal(btns, e) {
        $('body').on(e || 'click', btns.toString(), function() {
            var modal = this.id.slice(0, -3) + 'Modal';
            $("#" + modal).modal({
                backdrop: 'static',
                keyboard: true
            });
        });
    }
});
