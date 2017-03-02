/**
 * 管理用户页面逻辑处理
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
        $('#loading').show();
    }
    else {
        $('#loading').hide();
    }

}

/**
 * 显示用户数据
 * @param {Object} data 博客数据
 */
function showUsersData(data){
    // 创建博客表
    var $table = $('#users-table tbody');
    var users = data.users;
    for (var i in users){
        var nameSpan = '<span>' + users[i].name + '</span>';
        if (users[i].admin){
            nameSpan += '<span style="color:#d05"><i class="uk-icon-key"></i> 管理员</span>';
        }
        $table.append(
            '<tr>' +
            '<td class = "uk-text-middle">' +
            nameSpan +
            '</td>' +
            '<td>' +
            '<img class="uk-border-rounded" height="40" width="40" src="' + users[i].image + '">' +
            '</td>' +
            '<td class = "uk-text-middle">' +
            '<span>' + users[i].created_at.toDateTime() + '</span>' +
            '</td>' +
            '</tr>');
    }
}

/**
 * 获取用户请求结束处理函数
 * @param {Object} data 返回的数据
 */
function getUsersRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    console.log(data);
    showUsersData(data);
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
 * 发送获取用户信息请求
 */
function getUsersRequest(){
    var opt = {
        type: 'GET',
        url: '/api/users',
        dataType: 'json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(getUsersRequestDone);
    jqxhr.fail(requestFail);
}


/**
 * 初始化页面
 */
function initPage(){
    showErrorMessage(null);
    showDataLoading(true);
    getUsersRequest();
}

$(document).ready(initPage);