/**
 * 编辑博客页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */

/**
 * 显示错误消息
 * @param {String} msg 错误消息, 如果设置为null, 则隐藏错误消息标签
 */


/**
 * 生成UUID
 * @param {Number} len UUID长度
 * @param {Number} radix 进制显示， 可以为2， 10， 16
 * @returns {string} UUID
 */
function createUUID(len, radix) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
    var uuid = [], i;
    radix = radix || chars.length;

    if (len) {
      // Compact form
      for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random()*radix];
    } else {
      // rfc4122, version 4 form
      var r;

      // rfc4122 requires these characters
      uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
      uuid[14] = '4';

      // Fill in random data.  At i==19 set the high bits of clock sequence as
      // per rfc4122, sec. 4.1.5
      for (i = 0; i < 36; i++) {
        if (!uuid[i]) {
          r = 0 | Math.random()*16;
          uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
        }
      }
    }

    return uuid.join('');
}


function showErrorMessage(msg){

    // 找到显示错误消息的标签
    var $error = $('#error');
    if ($error.length === 0){
        return;
    }

    if (!msg){
        $error.css("visibility", "hidden");
        return;
    }

    $error.text(msg);
    $error.css("visibility", "visible");
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
 * 设置表单提交是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function showButtonLoading(isLoading){
    var $button = $blogForm.find('button[type=submit]');
    var $i = $blogForm.find('button[type=submit]').find('i');

    if (isLoading) {
        $button.attr('disabled', 'disabled');
        $i.addClass('uk-icon-spinner').addClass('uk-icon-spin');
    }
    else {
        $button.removeAttr('disabled');
        $i.removeClass('uk-icon-spinner').removeClass('uk-icon-spin');
    }
}

/**
 * 上传博客请求结束处理函数
 * @param {Object} data 返回的数据
 */
function postBlogRequestDone(data){
    showButtonLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    confirm('上传博客成功');

    // 清空原有内容
    $blogForm.find("#title").val(null);
    $blogForm.find("#summary").val(null);
    $blogForm.find("#content").val(null);


}

/**
 * 获取博客请求结束处理函数
 * @param {Object} data 返回的数据
 */
function getBlogRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    $blogForm.find("#title").val(data.name);
    $blogForm.find("#summary").val(data.summary);
    $blogForm.find("#content").val(data.content);

}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    showButtonLoading(false);
    showDataLoading(false);
    showErrorMessage('网络出了问题 (HTTP '+ xhr.status+')');
}

/**
 * 提交博客信息
 * @param {Object} data 博客数据
 */
function postBlog(data){

    showButtonLoading(true);

    var opt = {
        type: 'POST',
        url: window.blogAction,
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(postBlogRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 发送获取博客信息请求
 */
function getBlogRequest(){

    showDataLoading(true);

    var opt = {
        type: 'GET',
        url: window.blogAction,
        dataType: 'json',
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(getBlogRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 博客提交处理函数
 * @param event
 */
function blogSubmit(event) {
    // 通知浏览器提交已被处理， 阻止默认行为的发生
    event.preventDefault();

    var title = $blogForm.find("#title").val();
    var summary = $blogForm.find("#summary").val();
    var content = $blogForm.find("#content").val();

    // 博客信息是否合法
    if (!title.trim()) {
        showErrorMessage('请输入标题');
        return;
    }
    if (!summary.trim()) {
        showErrorMessage('请输入摘要');
        return;
    }
    if (!content.trim()) {
        showErrorMessage('请输入内容');
        return;
    }

    var blog = {
        name: title.trim(),
        summary: summary.trim(),
        content: content.trim()
    };

    postBlog(blog);
}

function selectedImage(imageInput){
    var file = imageInput.files[0];
    if (!file){
        return;
    }
    var reader = new FileReader();
    reader.onload = function(evt){
        console.log(file);
        var uuid = createUUID(16, 16);
        var filePath = '/static/img/blog/' + uuid + file.name;
        var $list = $('#img-list');
        $list.append(
            '<li id="' + uuid + '">' +
            '<div class="uk-thumbnail">' +
            '<img src="' + evt.target.result +'">' +
            '<div class="uk-text-large uk-text-success">' +
            filePath + '&nbsp;' +
            '<a><i class="uk-icon-trash-o uk-align-right uk-icon-small"></i></a>' +
            '</div>' +
            '</div>' +
            '</li>');
        image = evt.target.result;
    }
    reader.readAsDataURL(file);
}

/**
 * 初始化页面
 */
function initPage(){
    showErrorMessage(null);
    showDataLoading(false);

    window.$blogForm = $('#blog-form');
    window.$blogForm.submit(blogSubmit);

    $('#image-button').click(function () {
        var imageInput = document.getElementById('image-input');//隐藏的file文本ID
        imageInput.click();//加一个触发事件
    });

    var path = location.pathname;
    if (path === '/manage/blogs/create'){
        window.blogAction = '/api/blogs';
        return;
    }

    if (path === '/manage/blogs/edit'){
        var id = window.location.search.replace('?id=', '');
        window.blogAction = '/api/blogs/' + id;
        getBlogRequest();
        return;
    }
}

$(document).ready(initPage);