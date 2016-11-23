/**
 * 管理博客页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */


/**
 * 显示错误消息
 * @param {String} msg 错误消息, 如果设置为null, 则隐藏错误消息标签
 */
function showErrorMessage(msg){

    // 找到显示错误消息的标签
    var $error = $('#error');
    if ($error.length === 0){
        return;
    }

    if (!msg){
        $error.hide();
        return;
    }

    $error.text(msg);
    $error.show();
}

/**
 * 设置数据是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function showDataLoading(isLoading){
    if (isLoading){
        $('#loading').css("visibility", "visible");
    }
    else {
        $('#loading').css("visibility", "hidden");
    }

}


/**
 * 删除图片请求结束处理函数
 */
function deleteImageRequestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }
    // 如果成功删除博客, 则刷新页面
    var index = window.currentPageIndex;
    getImagesRequest(index.toString());
}

/**
 * 发送删除图片请求
 * @param {String} imageId 博客Id
 */
function postDeleteImageRequest(imageId){
    showErrorMessage(null);
    showDataLoading(true);

    var opt = {
        type: 'POST',
        url: '/api/images/' + imageId + '/delete',
        dataType: 'json',
        data: JSON.stringify({}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(deleteImageRequestDone);
    jqxhr.fail(requestFail);
}


/**
 * 删除图片处理函数
 * @param {Object} e 标签对象
 */
function trashIConClicked(e){
    var num = $(e).attr('num');
    var $image = $('#image-' + num);
    var imageId = $image.attr('image-id');
    var imageName = $image.find('span').text();

    if (confirm('确认要删除"' + imageName + '"?删除后不可恢复!')){
        postDeleteImageRequest(imageId);
    }
}


/**
 * 前一页博客处理函数
 */
function previousPageClicked(){
    var index = window.currentPageIndex - 1;
    getImagesRequest(index.toString());
}

/**
 * 后一页博客处理函数
 */
function nextPageClicked(){
    var index = window.currentPageIndex + 1;
    getImagesRequest(index.toString());
}


/**
 * 显示图像数据
 * @param {Object} data 图像数据
 */
function showImagesData(data){
    var images = data.images;
    var $image;
    var i;
    for (i in images){
        $image = $('#image-' + i);
        $image.attr('image-id', images[i].id);
        $image.find('img').attr('src', images[i].url);
        $image.find('span').text(images[i].url);
    }
    for (i = images.length; i < 6; i++){
        $image = $('#image-' + i);
        $image.find('img').attr('src', null);
        $image.find('span').text('');
    }

    // 创建分页列
    var $ul = $('ul.uk-pagination');
    // 先清空子节点
    $ul.children('li').remove();

    var previousLi = null;
    if (data.page.has_previous){
        previousLi =
            '<li>' +
            '<a onclick="previousPageClicked()">' +
            '<i class="uk-icon-angle-double-left"></i>' +
            '</a>' +
            '</li>'
    }
    else {
        previousLi =
            '<li class="uk-disabled">' +
            '<span><i class="uk-icon-angle-double-left"></i></span>' +
            '</li>';
    }
    $ul.append(previousLi);

    $ul.append('<li class="uk-active"><span>' + data.page.page_index + '</span></li>');

    var nextLi = null;
    if (data.page.has_next){
        nextLi =
            '<li>' +
            '<a onclick="nextPageClicked()">' +
            '<i class="uk-icon-angle-double-right"></i>' +
            '</a>' +
            '</li>';
    }
    else {
        nextLi =
            '<li class="uk-disabled">' +
            '<span><i class="uk-icon-angle-double-right"></i></span>' +
            '</li>';
    }
    $ul.append(nextLi);
}

/**
 * 获取图片请求结束处理函数
 * @param {Object} data 返回的数据
 */
function getImagesRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    window.currentPageIndex = data.page.page_index;
    showImagesData(data);
}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    showDataLoading(false);
    showErrorMessage('网络出了问题 (HTTP '+ xhr.status+')');
}


/**
 * 发送获取图片信息请求
 * @param {String} pageIndex 页面索引
 */
function getImagesRequest(pageIndex){

    showErrorMessage(null);
    showDataLoading(true);

    var opt = {
        type: 'GET',
        url: '/api/images?page=' + pageIndex,
        dataType: 'json'
    };
    // 发送请求
    var ajax = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    ajax.done(getImagesRequestDone);
    ajax.fail(requestFail);
}


/**
 * 上传图片请求结束处理函数
 * @param {Object} data 返回的数据
 */
function postImageRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    previewImgTrash()
    getImagesRequest(window.currentPageIndex.toString())

}


/**
 * 提交图片信息
 * @param {Object} data 图片数据
 */
function postImage(data){
    var opt = {
        type: 'POST',
        url: '/api/images',
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };

    showDataLoading(true);
    showErrorMessage(null);

    // 发送请求
    var ajax = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    ajax.done(postImageRequestDone);
    ajax.fail(requestFail);
}


/**
 * 预览图片删除处理函数
 */
function previewImgTrash(){
    // 隐藏图片预览
    var $imagePreview = $('#image-preview');
    $imagePreview.hide();

    // 重新生成input节点才可以重置input元素的值
    // 才可以重复选中同一张图片时多次触发selectedImage
    var $imageInputDiv = $('#image-input-div');
    $imageInputDiv.find('input').remove();
    $imageInputDiv.append(
        '<input id="image-input" type="file"' +
        'accept="image/jpeg, image/png" onchange="selectedImage(this)"' +
        'style="display:none;"/>');
}

/**
 * 预览图片上传处理函数
 */
function previewImgUpload(){
    var imageName = $('#image-preview span').text();
    var image = $('#image-preview img').attr('src');
    var imageData = {name: imageName, image: image};
    postImage(imageData);
}


/**
 * 选中图片处理函数
 */
function selectedImage(element){
    var file = element.files[0];
    if (!file){
        return;
    }
    var reader = new FileReader();
    reader.onload = function(evt){
        var $imagePreview = $('#image-preview');
        $imagePreview.find('span').text(file.name);
        $imagePreview.find('img').attr('src', evt.target.result);
        // 显示图片预览
        $imagePreview.show();
    };
    reader.readAsDataURL(file);
}


/**
 * 初始化页面
 */
function initPage(){
    getImagesRequest('1');

    // 设置增加新图片单击处理函数
    $('#new-image').click(function () {
        var imageInput = document.getElementById('image-input');
        imageInput.click();//加一个触发事件
    });

    $('#preview-trash').click(previewImgTrash);
    $('#preview-upload').click(previewImgUpload);

    // 隐藏图像预览
    $('#image-preview').hide();
}

$(document).ready(initPage);