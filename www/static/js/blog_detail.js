
/**
 * 博客详细页面逻辑处理
 * 作者: burnell liu
 * 邮箱: burnell_liu@outlook.com
 */



/**
 * 显示错误消息
 * @param {String} msg 错误消息
 */
function showErrorMessage(msg){

    // 找到显示错误消息的标签
    var $alert = $('#form-comment').find(".uk-alert-danger");
    if ($alert.length === 0){
        return;
    }

    if (!msg){
        $alert.text('');
        $alert.addClass('uk-hidden');
        return;
    }

    $alert.text(msg);
    $alert.removeClass('uk-hidden');
}

/**
 * 设置表单是否处于加载状态
 * @param {Boolean} isLoading true(加载状态), false(非加载状态)
 */
function showFormLoading(isLoading){
    var $formComment = $('#form-comment');
    var $button = $formComment.find('button');
    var $i = $formComment.find('button[type=submit]').find('i');

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
 * 请求结束处理函数
 * @param {Object} data 返回的数据
 */
function requestDone(data){
    // 如果有错则显示错误消息
    if (data.error){
        showFormLoading(false);
        showErrorMessage(data.message);
        return;
    }

    // 如果成功提交评论, 则刷新页面
    var url = location.pathname;
    location.assign(url);
}

/**
 * 请求错误处理函数
 * @param xhr
 * @param status
 */
function requestFail(xhr, status){
    showFormLoading(false);
    showErrorMessage('网络出了问题 (HTTP ' + xhr.status + ')(' + status + ')');
}


/**
 * 提交评论
 * @param {Object} data 评论数据
 */
function postComment(data){
    var blogId = location.pathname.replace('/blog/', '');
    var commentUrl = '/api/blogs/' + blogId + '/comments';
    console.log(commentUrl);
    var opt = {
        type: 'POST',
        url: commentUrl,
        dataType: 'json',
        data: JSON.stringify(data || {}),
        contentType: 'application/json'
    };
    // 发送请求
    var jqxhr = $.ajax(opt);
    // 设置请求完成和请求失败的处理函数
    jqxhr.done(requestDone);
    jqxhr.fail(requestFail);
}


/**
 * 评论提交处理函数
 * @param event
 */
function commentSubmit(event){
    // 通知浏览器提交已被处理， 阻止默认行为的发生
    event.preventDefault();



    // 检查评论内容
    var content = $('#form-comment').find('textarea').val().trim();
        if (content==='') {
            showErrorMessage('请输入评论内容！');
            return;
        }

    showFormLoading(true);

    var comment = {
        content: content
    };

    // 将评论信息POST出去
    postComment(comment);

}

/**
 * 回复评论处理函数
 * @param e 评论元素对象
 */
function commentReply(e){
    // 滚动页面到发表评论区域, 滚动时间200ms
    $('html, body').animate({scrollTop: $("#new-comment").offset().top}, 200);
    var author = $(e).attr('author');

    // 设置@, 设置焦点
    var $commentText = $('#new-comment-text');
    $commentText.val('回复@' + author + ':\n');
    $commentText.focus();
}


/**
 * 初始化页面
 */
function initPage(){
    // 设置评论提交处理函数
    var $formComment = $('#form-comment');
    $formComment.submit(commentSubmit);
}


$(document).ready(initPage);