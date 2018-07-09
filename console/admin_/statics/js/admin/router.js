/**
 * Created by wuyang on 16/8/4.
 */

// 获取地址栏,根据路由调用响应的js
require.config({
    baseUrl: "/static/js/",
    paths: {
        // 各种框架与库
        'jquery': "lib/jquery.min",
        'bootstrap': '../libs/bootstrap/js/bootstrap.min',
        'messenger': '../libs/messenger/js/messenger.min',
        'Chart': 'lib/Chart.min',
        'slidebars': 'lib/slidebars',
        'moment': '../libs/daterange/js/moment',
        'daterangepicker': '../libs/daterange/js/daterangepicker',
        'tiny-scrollbar': 'lib/tiny-scrollbar',
        'datatables.net': '../libs/datatable/js/jquery.dataTables.min',
        'datatable-bootstrap': '../libs/datatable/js/dataTables.bootstrap.min',
        'datatable-foundation': '../libs/datatable/js/dataTables.foundation.min',
        'datatable-jquery': '../libs/datatable/js/dataTables.jqueryui.min',
        'multiselect': '../libs/multiselect-master/js/multiselect',
        'seekBar': './lib/seekBar',
        'selectBox': './lib/multiSelectBox',
        'subnetGroup': './lib/subnetGroup',
        'plusMinusInput': './lib/plusMinusInput',

        // 路由配置
        'router': 'router/admin-router',

        // 项目封装
        'adminLogin': 'login/admin-login',
        'adminSetting': 'common/admin-setting',

        'utils': 'common/utils',
        'dataTableOptions': 'common/data-table-options',
        'dashboard': 'dashboard/dashboard',
        'ticketQueue': 'ticket/ticket-queue',
        'ticketList': 'ticket/ticket-list',
        'ticketDetail': 'ticket/ticket-detail',
        'bpmList': 'ticket/bpm-list',
        'bpmDetail': 'ticket/bpm-detail',
        'flavor': 'customize/flavor',
        'editFlavor': 'customize/flavor-edit',
        'flavorDetail': 'customize/flavor-detail',
        'image': 'customize/image',
        'editImage': 'customize/image-edit',

        'customizeFlavorCreate': 'customize/flavor-create',
        'customizeImageCreate': 'customize/image-create',

        'virtualSource': 'source/virtualSource',
        'physicsSource': 'source/physicsSource',
        'virtualList': 'source/virtualList',
        'physicsSourceDetail': 'source/physicsSourceDetail',
        'netSource': 'source/netSource',
        'netSourceDetail': 'source/netSourceDetail',
        'computeSource': 'source/compute-source',
        'computeSourceCreate': 'source/compute-sourcecreate',
        'memorySource': 'source/memory-source',
        'memorySourceCreate': 'source/memory-sourcecreate',
        'memorySourceDetails': 'source/memory-sourcedetails',
        'memorySourceEdit': 'source/memory-sourceedit',
        'computeSourceEdit': 'source/compute-sourceedit',
        'computeSourceDetails': 'source/compute-sourcedetails',
        'topSpeed': 'source/topSpeed',

        'netsSubnetsCreate': 'nets/subnets-create',
        'netsSubnetsEdit': 'nets/subnets-edit',
        'netsSubnetsList': 'nets/subnets-list',
        'netsSubnetsDetail': 'nets/subnets-detail',
        'netsRouterCreate': 'nets/router-create',
        'netsRouterEdit': 'nets/router-edit',
        'netsRouterList': 'nets/router-list',
        'netsRouterDetail': 'nets/router-detail',

        'account': 'system/account',
        'permission': 'system/permission',
        'permissionDetail': 'system/permission_detail',

        // 'record': 'system/record',

        'advancedConfig': 'setting/advanced_config'
    },
    shim: {
        'slidebars': {
            deps: ['jquery']
        },
        'main': {
            deps: [
                'jquery',
                'bootstrap',
                'messenger',
                'Chart',
                'slidebars',
                'moment',
                'daterangepicker',
                'slidebars',
                'tiny-scrollbar',
                'multiselect'
            ]
        }

    },
    urlArgs: "v=" + (new Date()).getTime()
});
require(['jquery'], function() {
    require([
        'messenger',
        'slidebars',
        'Chart',
        'bootstrap',
        'datatable-bootstrap',
        'multiselect',
        'plusMinusInput'
    ], function() {
        function setCrumbs(url){
            var json = {
                '/admin/ticket/bpm' : '<span>工单</span> > <a href="#">bpm</a> ',
                '/admin/customize/flavor' : '个性化模板 > Flavor',
                '/admin/customize/flavor_detail' : '个性化模板 > <a href="/admin/customize/flavor">Flavor</a>  > 详情',
                '/admin/customize/create_flavor' : '个性化模板 > <a href="/admin/customize/flavor">Flavor</a>  > 创建',
                '/admin/customize/images' : '个性化模块 > 镜像',
                '/admin/customize/create_image' : '个性化模块 > 创建镜像',
                '/admin/customize/edit_flavor' : '个性化模块 > <a href="/admin/customize/flavor">Flavor</a> > 修改',
                '/admin/customize/edit_image' : '个性化模块 > <a href="/admin/customize/images">镜像</a> > 修改',
                '/admin/nets/router' : '网络 > 路由',
                '/admin/nets/create_router' : '网络 > <a href="/admin/nets/router">路由</a> > 创建路由',
                '/admin/nets/router_detail' : '网络 > <a href="/admin/nets/router">路由</a> > 详情',
                '/admin/nets/edit_router' : '网络 > <a href="/admin/nets/router">路由</a> > 修改',
                '/admin/nets/subnets' : '网络 > 子网',
                '/admin/nets/create_subnets' : '网络 > <a href="/admin/nets/subnets">子网</a> > 创建',
                '/admin/nets/subnets_detail' : '网络 > <a href="/admin/nets/subnets">子网</a> > 详情',
                '/admin/nets/edit_subnets' : '网络 > <a href="/admin/nets/subnets">子网</a> > 编辑',
                '/admin/sourceManage/computeSource' : '资源管理 > 计算资源',
                '/admin/sourceManage/computeSourceCreate' : '资源管理 > <a href="/admin/sourceManage/computeSource">计算资源</a> > 创建',
                '/admin/sourceManage/computeSourceDetails' : '资源管理 > <a href="/admin/sourceManage/computeSource">计算资源</a> > 详情',
                '/admin/sourceManage/computeSourceEdit' : '资源管理 > <a href="/admin/sourceManage/computeSource">计算资源</a> > 修改',
                '/admin/sourceManage/memorySource' : '资源管理 > 存储资源',
                '/admin/sourceManage/memorySourceCreate' : '资源管理 > <a href="/admin/sourceManage/memorySource">存储资源</a> > 创建',
                '/admin/sourceManage/memorySourceDetails' : '资源管理 > <a href="/admin/sourceManage/memorySource">存储资源</a> > 详情',
                '/admin/sourceManage/memorySourceEdit' : '资源管理 > <a href="/admin/sourceManage/memorySource">存储资源</a> > 修改',
                '/admin/sourceManage/netSource' : '资源管理 > 网络资源',
                '/admin/sourceManage/netDetail' : '资源管理 > <a href="/admin/sourceManage/netSource">网络资源</a> > 详情',
                '/admin/sourceManage/physicsSource' : '资源管理 > 物理资源',
                '/admin/sourceManage/physicsSourceDetail' : '资源管理 > <a href="/admin/sourceManage/physicsSource">物理资源</a> > 详情',
                '/admin/sourceManage/topSpeed' : '资源管理 > 极速创建',
                '/admin/sourceManage/virtualSource' : '资源管理 > 资源总览',
                // '/admin/system/record' : '操作日志',
                '/admin/setting/advanced_config' : '系统设置 > 高级设置',
                '/admin/sourceManage/virtualList' : '资源管理 > <a href="/admin/sourceManage/computeSource">计算资源</a> > 虚拟机列表',
                '/admin/sourceManage/virtualList?host' : '资源管理 > <a href="/admin/sourceManage/physicsSource">物理资源</a> > 物理虚拟机列表',
            };
            $("#page_crumbs").html(json[url]);
        }
        require(['router'], function(app) {
            app.get('/admin/login', function() {
                require(['adminLogin']);
            });
            app.get(/\/([^/]+(\/[^/]+)*)?$/, function() {
                setCrumbs(app.getUrl());
                require(['adminSetting']); this.next();
            });
            app.get(/^\/admin\/(dashboard|index)?$/, function() {
                require(['dashboard']);
            });
            app.get("/admin/ticket/queue", function() {
                require(['ticketQueue']);
            });
            app.get("/admin/ticket/list", function() {
                require(['ticketList']);
            });
            app.get(/\/admin\/ticket\/detail\/(.*)/, function() {
                require(['ticketDetail']);
            });
            app.get("/admin/ticket/bpm", function() {
                require(['bpmList']);
            });
            app.get("/admin/ticket/bpm_detail", function() {
                require(['bpmDetail']);
            });
            app.get("/admin/nets/create_subnets", function() {
                require(['netsSubnetsCreate']);
            });
            app.get("/admin/nets/edit_subnets", function() {
                require(['netsSubnetsEdit']);
            });
            app.get("/admin/nets/subnets_detail", function() {
                require(['netsSubnetsDetail']);
            });
            app.get("/admin/nets/subnets", function() {
                require(['netsSubnetsList']);
            });
            app.get("/admin/nets/create_router", function() {
                require(['netsRouterCreate']);
            });
            app.get(/\/admin\/nets\/router_detail/, function() {
                require(['netsRouterDetail']);
            });
            app.get("/admin/nets/edit_router", function() {
                require(['netsRouterEdit']);
            });
            app.get("/admin/nets/router", function() {
                require(['netsRouterList']);
            });
            app.get("/admin/customize/flavor", function() {
                require(['flavor']);
            });
            app.get(/\/admin\/customize\/edit_flavor/, function() {
                require(['editFlavor']);
            });
            app.get(/\/admin\/customize\/flavor_detail/, function() {
                require(['flavorDetail']);
            });
            app.get(/\/admin\/customize\/edit_image/, function() {
                require(['editImage']);
            });
            app.get("/admin/customize/create_flavor", function() {
                require(['customizeFlavorCreate']);
            });
            app.get("/admin/customize/images", function() {
                require(['image']);
            });
            app.get("/admin/customize/create_image", function() {
                require(['customizeImageCreate']);
            });
            app.get("/admin/sourceManage/virtualSource", function() {
                require(['virtualSource']);
            });
            app.get("/admin/sourceManage/computeSourceCreate", function() {
                require(['computeSourceCreate']);
            });
            app.get("/admin/sourceManage/memorySource", function() {
                require(['memorySource']);
            });
            app.get("/admin/sourceManage/memorySourceCreate", function() {
                require(['memorySourceCreate']);
            });
            app.get(/\/admin\/sourceManage\/memorySourceDetails/, function() {
                require(['memorySourceDetails']);
            });
            app.get(/\/admin\/sourceManage\/memorySourceEdit/, function() {
                require(['memorySourceEdit']);
            });
            app.get(/\/admin\/sourceManage\/computeSourceDetails/, function() {
                require(['computeSourceDetails']);
            });
            app.get(/\/admin\/sourceManage\/computeSourceEdit/, function() {
                require(['computeSourceEdit']);
            });
            app.get("/admin/sourceManage/computeSource", function() {
                require(['computeSource']);
            });
            app.get("/admin/sourceManage/topSpeed", function() {
                require(['topSpeed']);
            });
            app.get("/admin/sourceManage/virtualList", function() {
                require(['virtualList']);
            });
            app.get("/admin/sourceManage/physicsSource", function() {
                require(['physicsSource']);
            });
            app.get("/admin/sourceManage/physicsSourceDetail", function() {
                require(['physicsSourceDetail']);
            });
            app.get("/admin/sourceManage/netSource", function() {
                require(['netSource']);
            });
            app.get("/admin/sourceManage/netDetail", function() {
                require(['netSourceDetail']);
            });
            app.get("/admin/system/account", function() {
                require(['account']);
            });
            app.get("/admin/system/permission", function() {
                require(['permission']);
            });
            app.get(/\/admin\/system\/permission\/[^/]+$/, function() {
                require(['permissionDetail']);
            });
            // app.get("/admin/system/record", function() {
            //     require(['record']);
            // });
            app.get("/admin/setting/advanced_config", function() {
                require(['advancedConfig']);
            });

        });
    });
});


