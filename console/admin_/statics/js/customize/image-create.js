define(['utils', 'selectBox'], function (utils, SelectBox) {
    var owner = $("#owner").val();
    var zone = $("#zone").val();
    var moveFlavorsubmitBtn = {
        'stop': '停止上传',
        'start': '开始上传',
        'pause': '暂停上传',
        'keep': '继续上传',
        'success': '上传成功',
        'error': '上传失败',
        'updating': '上传中'
    };
    var edit_image = false; //是否修改镜像
    var is_protect = true;
    var is_public = true;
    // 文件在上传至服务器端的指针
    var fileObj = {
        index: 0,
        fileUpload_type: 'stop',
        fileSplitSize: 1000 * 1024,
        file: null,
        size: 0,
        name: '',
        date: "",
    };
    var fileObj_old = {};

    $("#create_image_file_hidden").on('change', function () {
        if(edit_image){
            // 镜像修改
            fileObj = Object.assign(fileObj, {index: 0, fileUpload_type: 'stop'});
            $("#edit_image_file").hide();
            $("#edit_image_file_upload").show();
            $("#edit_image_file_esc").show();
        }
        if (!$(this)[0].files[0]) return false;
        fileObj.file = $(this)[0].files[0];
        fileObj.size = fileObj.file.size;
        fileObj.name = fileObj.file.name;
        setFileName();
    });

    function setFileName() {
        $(".create_image_filename").html(fileObj.name);
        $("#create-flavor-name-modal").html(fileObj.name);
        $("#create-flavor-file-name-modal").html(fileObj.name);
        $("#migrateProgress").css('width', '0%');
        $("#progressNum").html('[' + 0 + ',' + utils.toAutoMemory(fileObj.size) + ']');
        $("#create_image_file_load").removeProp('disabled');
        $("#create_image_file_tip").html('');
    }

    $("#create_image_file").click(function () {
        $("#create_image_file_hidden").click();
    });

    $("#edit_image_file").click(function () {
        $("#create_image_file_hidden").click();
    });
    $("#edit_image_file_esc").click(function(){
        fileObj = Object.assign(fileObj, fileObj_old);
        console.log(fileObj);
        $(".create_image_filename").html(fileObj.name);
        $("#create-flavor-name-modal").html(fileObj.name);
        $("#create-flavor-file-name-modal").html(fileObj.name);
        $("#create_image_success").show();
        $("#create_image_load").hide();
        $("#edit_image_file").show();
        $("#edit_image_file_upload").hide();
        $("#edit_image_file_esc").hide();
    });

    $("#create_image_file_load").add("#edit_image_file_upload").click(function () {
        if (!fileObj.file) {
            utils.errMsg("请选择文件");
            return false;
        }
        var data = new FormData();
        data.append("name", encodeURIComponent(fileObj.file.name));
        data.append("date", fileObj.file.lastModified);
        data.append("owner", owner);
        $.ajax({
            url: '/admin/JudgeImageFileExist',
            type: 'post',
            data: data,
            contentType: false,
            processData: false,
            beforeSend: function (xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", utils.getCookie("csrftoken"));
            },
            success: function (data) {
                if (data.ret_code == 0) {
                    var fileInfo = data.ret_set;
                    if (fileInfo.length == 0) {
                        $("#create-flavor-modal").modal({backdrop: 'static', keyboard: false});
                    } else {
                        fileObj.index = fileInfo[0].index + 1;
                        fileObj.fileSplitSize = fileInfo[0].fileSplitSize;
                        $("#create-image-file-modal").modal('hide');
                        if (fileObj.index * fileObj.fileSplitSize > fileObj.size) {
                            $("#create-flavor-file-progress-modal").html('[' + utils.toAutoMemory(fileObj.size) + ',' + utils.toAutoMemory(fileObj.size) + ']');
                            $("#create-image-file-tip-modal").html('此文件已经上传完毕,是否直接使用.');
                            $("#create-flavor-modal").modal('hide');
                            $("#create-image-file-modal-reset").html('重新选择').click(function () {
                                $("#create_image_file_hidden").click();
                                $("#create_image_file_tip").html('');
                            });
                            $("#create-image-file-modal-goon").html('直接使用').click(function () {
                                fileUploadSuccess();
                            });
                        } else {
                            $("#create-image-file-tip-modal").html('原来有未完成的上传文件,是否要继续上传.');
                            $("#create-flavor-file-progress-modal").html('[' + utils.toAutoMemory(fileObj.fileSplitSize * fileObj.index) + ',' + utils.toAutoMemory(fileObj.size) + ']');
                            $("#create-flavor-modal").modal({backdrop: 'static', keyboard: false});
                            $("#create-image-file-modal-reset").html('重新上传').click(function () {
                                $("#migrateProgress").css('width', '0%');
                                $("#progressNum").html('[' + 0 + ',' + utils.toAutoMemory(fileObj.size) + ']');
                            });
                            $("#create-image-file-modal-goon").html('继续上传').click(function () {
                                $("#migrateProgress").css('width', (((fileObj.index - 1) * fileObj.fileSplitSize) / fileObj.size * 100) + '%');
                                $("#progressNum").html('[' + utils.toAutoMemory((fileObj.index - 1) * fileObj.fileSplitSize) + ',' + utils.toAutoMemory(fileObj.size) + ']');
                            });
                        }
                        $("#create-image-file-modal").modal({backdrop: 'static', keyboard: false});
                    }
                } else {
                    console.log('查询文件失败,请重新选择文件');
                }
            },
            error: function (err) {
                console.log(err);
            }
        });
    });
    $("#moveFlavorsubmitBtn").click(function () {
        setButtonType();
    });
    function fileUploadOver() {
        var type = fileObj.fileUpload_type;
        switch (type) {
            case "success":
                utils.succMsg(moveFlavorsubmitBtn[fileObj.fileUpload_type]);
                fileUploadSuccess();
                break;
            case "updating":
                fileUpload();
                break;
            case "error":
                utils.errMsg(moveFlavorsubmitBtn[fileObj.fileUpload_type]);
                $(this).data('type', "error");
                break;
            case "pause":
                utils.succMsg(moveFlavorsubmitBtn[fileObj.fileUpload_type]);
                break;
            case "keep":
                utils.succMsg(moveFlavorsubmitBtn[fileObj.fileUpload_type]);
                break;
        }
    }

    function fileUploadSuccess() {
        fileObj = Object.assign(fileObj, {index: 0, fileUpload_type:'success'});
        fileObj_old = Object.assign(fileObj_old, fileObj);
        edit_image = true;
        $("#create_image_success").show();
        $("#create_image_load").hide();
        $("#create-flavor-modal").modal('hide');
        $("#create-image-file-modal").modal('hide');
        $("#edit_image_file").show();
        $("#edit_image_file_upload").hide();
        $("#edit_image_file_esc").hide();
    }

    function setButtonType() {
        var button_type = $("#moveFlavorsubmitBtn").data("type");
        switch (button_type) {
            case "start":
                fileObj.fileUpload_type = "start";
                $(this).data('type', "updating").html(moveFlavorsubmitBtn['updating']);
                fileUpload();
                break;
            case "updating":
                fileObj.fileUpload_type = "pause";
                $(this).data('type', 'pause').html(moveFlavorsubmitBtn['pause']);
                break;
            case "error":
                $(this).data('type', fileObj.fileUpload_type).html(moveFlavorsubmitBtn[fileObj.fileUpload_type]);
                break;
            case "pause":
                $(this).data('type', "keep").html(moveFlavorsubmitBtn['keep']);
                break;
            case "keep":
                fileObj.fileUpload_type = "keep";
                $(this).data('type', "updating").html(moveFlavorsubmitBtn['updating']);
                fileUpload();
        }
    }

    function fileUpload() {
        var data = new FormData();
        var fileReader = new FileReader();
        var start = fileObj.fileSplitSize * fileObj.index;
        var end = fileObj.fileSplitSize * (fileObj.index + 1);
        var size = fileObj.size;
        var fileContent = fileObj.file.slice(start, end);
        fileReader.readAsBinaryString(fileContent);
        fileReader.onload = function (e) {
            var result = e.target.result;
            var md5 = utils.generateMD5(result);
            data.append("name", encodeURIComponent(fileObj.file.name));
            data.append("date", fileObj.file.lastModified);
            data.append("image_file", fileContent);
            data.append("index", fileObj.index);
            data.append("total_size", fileObj.size);
            data.append("fileSplitSize", fileObj.fileSplitSize);
            data.append("md5", md5);
            data.append("owner", owner);
            $.ajax({
                url: '/admin/GetImageFile',
                type: 'post',
                data: data,
                contentType: false,
                processData: false,
                beforeSend: function (xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", utils.getCookie("csrftoken"));
                },
                success: function (data) {
                    if (data.ret_code == 0) {
                        if (fileObj.fileUpload_type == "pause") {
                            fileUploadOver();
                            return false;
                        }
                        fileObj.index++;
                        var count = fileObj.index * fileObj.fileSplitSize;
                        if (count > fileObj.size) {
                            fileObj.fileUpload_type = "success";
                            $("#migrateProgress").css({'width': '100%'});
                            $("#progressNum").html('[' + utils.toAutoMemory(fileObj.size) + ',' + utils.toAutoMemory(fileObj.size) + ']');
                        } else {
                            fileObj.fileUpload_type = "updating";
                            $("#migrateProgress").css('width', ((fileObj.index * fileObj.fileSplitSize) / fileObj.size * 100) + '%');
                            $("#progressNum").html('[' + utils.toAutoMemory((fileObj.index * fileObj.fileSplitSize)) + ',' + utils.toAutoMemory(fileObj.size) + ']');
                        }
                    } else {
                        fileObj.fileUpload_type = "error";
                    }
                    fileUploadOver();
                },
                error: function (err) {
                    fileObj.fileUpload_type = "error";
                    fileUploadOver();
                }
            });
        };
    }

    $(".switch_button").on('click', function () {
        $(this).parent().find('.switch_button').removeClass('active');
        $(this).addClass('active');
        if($(this).attr('name') == 'is_protect'){
            is_protect = $(this).attr('value') === 'true' ? true : false;
        }
        if($(this).attr('name') == 'is_public'){
            is_public = $(this).attr('value') === 'true' ? true : false;
        }
    });

    $("#create_image").click(function(){
        var name = $("#image_name").val();
        var disk_format = $("input[name=disk_format]:checked").val();
        var image_type = $("input[name=image_type]:checked").val();
        var param = {
            zone: zone,
            owner: owner,
            name: name,
            date: fileObj.file.lastModified,
            disk_format: disk_format,
            image_type: image_type,
            is_protect: is_protect,
            is_public: is_public,
            file_name: encodeURIComponent(fileObj.file.name)
        };
        utils._ajax({
            url: "/admin/CreateImageFile",
            contentType: 'application/json',
            data: JSON.stringify(param),
            succCB: function () {
                utils.succMsg('镜像创建成功');
                location.href = '/admin/customize/images';
            },
            errCB: function (err) {
                utils.succMsg(err.ret_msg);
            },
            error: function () {
                utils.succMsg('镜像创建失败');
            }
        });
    });
});