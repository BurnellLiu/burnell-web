

/**
 * 管理评论页面逻辑处理
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
 * 删除评论请求结束处理函数
 */
function deleteCommentRequestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }
    // 如果成功删除, 则刷新
    // 有待优化, 每删除一条评论都要刷新整个页面
    var pageIndex = window.commentsData.page.page_index;
    getCommentsRequest(pageIndex);
}

/**
 * 发送删除评论请求
 * @param {String} commentId 评论Id
 */
function postDeleteCommentRequest(commentId){
    var opt = {
        type: 'POST',
        url: '/api/comments/' + commentId + '/delete',
        dataType: 'json',
        data: JSON.stringify({}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(deleteCommentRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 删除评论处理函数
 * @param {String} id 评论id
 */
function trashIConClicked(id){

    var comments = window.commentsData.comments;
    for (var i in comments){
        if (comments[i].id === id){
            var content = comments[i].content;
            break;
        }
    }
    if (confirm('确认要删除"' + content + '"?删除后不可恢复!')){
        postDeleteCommentRequest(id);
    }
}

/**
 * 跳页处理函数
 */
function jumpPageClicked(e){
    var num = $(e).attr('page');
    getCommentsRequest(num);
}

/**
 * 显示评论数据
 * @param {Object} data 博客数据
 */
function showCommentsData(data){

    var $table = $('#comments-table').find('tbody');
    // 先清空子节点
    $table.children('tr').remove();

    var comments = data.comments;
    for (var i in comments){
        $table.append(
            '<tr comment-id="' + comments[i].id + '">' +
            '<td>' +
            '<span>' + comments[i].user_name + '</span>' +
            '</td>' +
            '<td>' +
            '<span>' + comments[i].content + '</span>' +
            '</td>' +
            '<td>' +
            '<span>' + comments[i].created_at.toDateTime() + '</span>'+
            '</td>' +
            '<td>' +
                '<span><a href="/blog/' + comments[i].blog_id +'">链接</a></span>' +
            '</td>' +
            '<td>' +
            '<a onclick="trashIConClicked(\'' + comments[i].id + '\')">' +
            '<i class="uk-icon-trash-o"></i></a>' +
            '</td>' +
            '</tr>');
    }
    // 少于10行的填充空白
    for (i = 0; i < 10-comments.length; i++){
        $table.append('<tr><td>&nbsp</td><td></td><td></td><td></td><td></td></tr>');
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
 * 获取评论请求结束处理函数
 * @param {Object} data 返回的数据
 */
function getCommentsRequestDone(data){
    showDataLoading(false);

    // 如果有错则显示错误消息
    if (data.error){
        showErrorMessage(data.message);
        return;
    }

    // 保存评论数据
    window.commentsData = data;

    showCommentsData(data);
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
 * 发送获取评论信息请求
 * @param {String} pageIndex 页面索引
 */
function getCommentsRequest(pageIndex){

    showErrorMessage(null);
    showDataLoading(true);

    var opt = {
        type: 'GET',
        url: '/api/comments?page=' + pageIndex,
        dataType: 'json'
    };

    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(getCommentsRequestDone);
    jqxhr.fail(requestFail);
}

/**
 * 初始化页面
 */
function initPage(){
    getCommentsRequest('1');
}

$(document).ready(initPage);