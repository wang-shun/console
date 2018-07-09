/**
 * Created by wuyang on 16/8/4.
 */
define(['utils'], function(utils) {
    // 修改页面title 哪里有public_platform_name??
    var platformName = $("input[name='public_platform_name']").val();
    document.title = platformName.replace(/(^\s*)/g, "") ? platformName + '-' + document.title : document.title;

    // 配置massenger
    Messenger.options = {
        extraClasses: 'messenger-fixed messenger-on-bottom messenger-on-right',
        theme: 'air'
    };

    // 左边菜单选项
    $('#menu > ul > li > a').click(function() {
        $('#menu li').removeClass('active');
        $(this).closest('li').addClass('active');
        var checkElement = $(this).next();
        if ((checkElement.is('ul')) && (checkElement.is(':visible'))) {
            $(this).closest('li').removeClass('active');
            checkElement.slideUp('normal');
        }
        if ((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
            $('#menu ul ul:visible').slideUp('normal');
            checkElement.slideDown('normal');
        }
        if ($(this).closest('li').find('ul').children().length == 0) {
            return true;
        } else {
            return false;
        }
    });


// Mobile Nav
    $('#mob-nav').click(function() {
        if ($('aside.open').length > 0) {
            $("aside").animate({left: "-320px"}, 500).removeClass('open');
        } else {
            $("aside").animate({left: "0px"}, 500).addClass('open');
        }
    });

// Tooltips
//      $('a').tooltip('hide');
     $.slidebars();

    // 武扬2016年08月03日15:30:19判断lincesen

    utils._ajax({
        type: 'post',
        url: '/license',
        data: {action: "DecryptLicense", zone: "bj"},
        finalCB: function(data) {
            if (data.ret_code !== 0) {
                location.href = '/logout';
            }
        }
    });


});


