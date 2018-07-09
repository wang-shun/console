define(['utils'], function(utils) {
    // 武扬2016年08月03日15:30:19判断lincesen
    utils._ajax({
        type: 'post',
        url: '/license',
        data: {action: "DecryptLicense", zone: "bj"},
        finalCB: function(data) {
            if (data.ret_code !== 0) {
                $("#licenseError").show();
                $("#licenseError .text-danger").html(data.ret_msg);
            } else {
                $("#inputs").show();

            }
        }
    });

    $("#licenseSubmit").click(function() {
        var license = $("#license").val();
        if (/^\s*$/.test(license)) {
            alert('请输入license');
            return false;
        } else {
            utils._ajax({
                type: 'post',
                url: '/license',
                data: JSON.stringify({post_type: "SetLicenseKey", license_key: license}),
                contentType: 'application/json',
                succCB: function() {
                    alert('license设置成功,请输入账号密码');
                    $("#inputs").show();
                    $("#licenseError").hide();
                    $("#active_license").html('激活license');
                    $('#active_license').on('click', activeLicenseFun);
                },
                errCB: function() {
                    alert('license设置有误,请重新输入');
                }
            });
        }
    });

    $('#active_license').on('click', activeLicenseFun);
    function activeLicenseFun() {
        $("#licenseError").show();
        $("#licenseError .text-danger").html('请输入激活license');
        $("#inputs").hide();
        $("#active_license").html('返回');
        $('#active_license').off('click').on('click', returnLoginFun);
    }
    function returnLoginFun() {
        $("#licenseError").hide();
        $("#licenseError .text-danger").html('');
        $("#inputs").show();
        $("#active_license").html('激活license');
        $('#active_license').off('click').on('click', activeLicenseFun);
    }
});
