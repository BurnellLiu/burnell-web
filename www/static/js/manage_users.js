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

    if (!msg){
        $error.text("cake");
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
        $('#loading').show();
    }
    else {
        $('#loading').hide();
    }
}

/**
 * 跳页处理函数
 */
function jumpPageClicked(e){
    var num = $(e).attr('page');
    getUsersRequest(num);
}

/**
 * 显示用户数据
 * @param {Object} data 博客数据
 */
function showUsersData(data){
    // 创建博客表
    var $table = $('#users-table tbody');
        // 先清空子节点
    $table.children('tr').remove();

    var users = data.users;
    for (var i in users){
        var nameSpan = '<span>' + users[i].name + '</span>';
        if (users[i].admin){
            nameSpan += '<span style="color:#d05"><i class="uk-icon-key"></i> 管理员</span>';
        }
        $table.append(
            '<tr>' +
            '<td>' +
            nameSpan +
            '</td>' +
            '<td class="uk-text-center">' +
            '<img class="uk-border-rounded" height="40" width="40" src="' + users[i].image + '">' +
            '</td>' +
            '<td class = "uk-text-center">' +
            '<span>' + users[i].created_at.toDateTime() + '</span>' +
            '</td>' +
            '</tr>');
    }

    // 创建分页列
    var $ul = $('ul.uk-pagination');
    // 先清空子节点
    $ul.children('li').remove();

    var currentIndex = data.page.page_index;
    var pageCount = data.page.page_count;

    var previousLi = null;
    if (data.page.has_previous){
        var pageIndex = currentIndex-1;
        previousLi = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)">' +
            '<i class="uk-icon-angle-double-left"></i></a></li>'
    }
    else {
        previousLi = '<li class="uk-disabled"><span><i class="uk-icon-angle-double-left"></i></span></li>';
    }
    $ul.append(previousLi);

    if ((currentIndex - 4) > 0){
        var li = '<li><a page="1" onclick="jumpPageClicked(this)"><span>1</span></a></li><li><span>...</span></li>';
        $ul.append(li);
    }

    if ((currentIndex - 4) == 0){
        li = '<li><a page="1" onclick="jumpPageClicked(this)"><span>1</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex - 2) > 0){
        pageIndex = currentIndex-2;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex - 1) > 0){
        pageIndex = currentIndex-1;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    $ul.append('<li class="uk-active"><span>' + currentIndex + '</span></li>');

    if ((currentIndex + 1) <= pageCount){
        pageIndex = currentIndex+1;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 2) <= pageCount){
        pageIndex = currentIndex+2;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 3) == pageCount){
        pageIndex = currentIndex+3;
        li = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)"><span>' + pageIndex +'</span></a></li>';
        $ul.append(li);
    }

    if ((currentIndex + 3) < pageCount){
        li = '<li><span>...</span></li><li><a page="' + pageCount +'" onclick="jumpPageClicked(this)"><span>' + pageCount +'</span></a></li>';
        $ul.append(li);
    }

    var nextLi = null;
    if (data.page.has_next){
        pageIndex = currentIndex + 1;
        nextLi = '<li><a page="' + pageIndex +'" onclick="jumpPageClicked(this)">' +
            '<i class="uk-icon-angle-double-right"></i></a></li>';
    }
    else {
        nextLi = '<li class="uk-disabled"><span><i class="uk-icon-angle-double-right"></i></span></li>';
    }
    $ul.append(nextLi);
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
 * @param {String} pageIndex 页面索引
 */
function getUsersRequest(pageIndex){
    showErrorMessage(null);
    showDataLoading(true);

    var opt = {
        type: 'GET',
        url: '/api/users?page=' + pageIndex,
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
    getUsersRequest('1');
}

$(document).ready(initPage);